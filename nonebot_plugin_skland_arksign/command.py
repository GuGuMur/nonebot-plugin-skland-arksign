from sqlalchemy import select
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import on_alconna
from sqlalchemy.ext.asyncio import AsyncSession
from nonebot_plugin_saa import Text, PlatformTarget
from nonebot_plugin_session import Session, extract_session
from nonebot_plugin_datastore import get_session, create_session
from nonebot_plugin_session.model import SessionModel, get_or_add_session_model

from .alc_parser import skland_alc
from .model import SklandSubscribe
from .utils import run_sign, cleantext
from .depends import skland_session_extract

skland = on_alconna(
    skland_alc,
    aliases={"skd", "skl", "森空岛"},
    use_cmd_start=True,
    # use_cmd_sep=True,
    auto_send_output=True,
)


@skland.assign("add")
async def add(
    state: T_State,
    uid: str,
    token: str | None = None,
    note: str | None = None,
    event_session: Session = Depends(skland_session_extract),
    db_session: AsyncSession = Depends(get_session),
):
    logger.debug(f"匹配到的参数：{state}")
    user_account = event_session.get_saa_target()
    if not user_account:
        await skland.finish("未能获取到当前会话的可发送用户信息，请检查")
    logger.debug(f"当前会话的用户信息：{user_account.dict()}")

    # 判断是否为私信/群聊

    # 先添加一个record
    new_record = SklandSubscribe(user=user_account.dict(), uid=uid, token=token, cred="", note=note)
    db_session.add(new_record)
    await db_session.commit()
    await db_session.refresh(new_record)

    # 这是群聊
    if state.get("is_group"):
        # 把sessionb保存到消息数据库里
        async with create_session() as db_session:
            await get_or_add_session_model(event_session, db_session)
            logger.debug(f"当前会话的Session信息：{event_session.dict()}")

        await skland.finish(cleantext(f"""
            [森空岛明日方舟签到器]已在群聊{event_session.id2}添加新账号！
            UID：{uid}
            备注：{note or "无"}
            接下来，请你通过`私信`bot /森空岛 bind [该账号对应的token] 来完成定时签到服务！"""))

    # 这是私信
    else:
        if not token:
            await skland.finish(cleantext(f"""
                [森空岛明日方舟签到器]已添加新账号！
                UID：{uid}
                备注：{note or "无"}
                接下来，请你通过`私信`bot /森空岛 bind [该账号对应的token] 来完成定时签到服务！"""))

        await skland.send(cleantext(f"""
                [森空岛明日方舟签到器]已添加新账号！
                UID：{uid}
                TOKEN：{token}
                备注：{note or "无"}
                """))
        runres = await run_sign(uid=uid, token=token)
        await skland.finish(f"立即执行签到操作完成！\n{runres['text']}")


@skland.assign("bind")
async def bind(
    state: T_State,
    token: str,
    event_session: Session = Depends(skland_session_extract),
    db_session: AsyncSession = Depends(get_session),
):
    logger.debug(f"匹配到的参数：{state}")

    user_account = event_session.get_saa_target()
    if not user_account:
        await skland.finish("未能获取到当前会话的可发送用户信息，请检查")

    # 先找到私聊用户对应的群聊Session
    get_group_session_stmt = select(SessionModel).where(SessionModel.id1 == event_session.id1)
    group_session = (await db_session.scalars(get_group_session_stmt)).first()
    if not group_session:
        await skland.finish("未找到与你对应的群聊Session，请检查")
    elif group_session_saa := group_session.session.get_saa_target():
        group_session_dict = group_session_saa.dict()
        logger.debug(f"查询到的群聊Session: {group_session.session.dict()}")
        logger.debug(f"查询到的群聊Session对应的用户信息：{group_session_dict}")
        session_user_id: str | None = group_session.id1
        # 单独赋值是因为需要跨查询使用，如果在下一个查询里直接使用group_session.id1会报错
        group_session_id: str | None = group_session.id2
    else:
        await skland.finish("无法获取到对应可发送用户信息，请检查")

    # 再更新SklandSubscribe
    get_skland_subscribe_stmt = select(SklandSubscribe).where(SklandSubscribe.user == group_session_dict)
    skd_user: SklandSubscribe | None = (await db_session.scalars(get_skland_subscribe_stmt)).first()
    logger.debug(f"查询到的SklandSubscribe：{skd_user}")
    if not skd_user:
        await skland.finish("未能匹配到你在群聊注册的账号，请检查")
    skd_user.token = token
    await db_session.flush()
    # 发送成功信息（私聊）
    await skland.send(cleantext(f"""
            [森空岛明日方舟签到器]已经为绑定在群聊的游戏账号绑定TOKEN！
            群聊ID：{group_session_id}
            游戏账号UID：{skd_user.uid}
            TOKEN：{token}
            备注：{skd_user.note}
            """))
    # 再到群聊通知一下
    runres = await run_sign(uid=skd_user.uid, token=token)
    msg = Text(cleantext(f"""
        [森空岛明日方舟签到器]用户{session_user_id}已经通过私信绑定账号{skd_user.uid}的token！
        立即执行签到操作完成！
        信息如下：{runres['text']}"""))
    await msg.send_to(PlatformTarget.deserialize(skd_user.user))

    # 最后删掉Session数据库里的消息
    delete_session_stmt = select(SessionModel).where(SessionModel.id1 == event_session.id1)
    result = (await db_session.scalars(delete_session_stmt)).all()
    for i in result:
        await db_session.delete(i)
    await db_session.flush()
    # 保存到数据库
    await db_session.commit()


# 删除功能可以在各处使用
@skland.assign("del")
async def del_(
    bot: Bot,
    event: Event,
    identifier: str,
    event_session: Session = Depends(extract_session),
    db_session: AsyncSession = Depends(get_session),
):
    # identifier 可以是uid或者备注, 需要都尝试一下
    stmt = select(SklandSubscribe).where((SklandSubscribe.uid == identifier) | (SklandSubscribe.note == identifier))
    result = await db_session.scalar(stmt)
    if not result:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")

    if not await SUPERUSER(bot, event):
        user = event_session.get_saa_target()
        if not user:
            await skland.finish("未能获取到当前会话的用户信息，请检查")

        if user.dict() != result.user:
            await skland.finish("您无权删除该账号！")

    uid = result.uid
    note = result.note or "无"

    await db_session.delete(result)
    await db_session.commit()

    await skland.finish(cleantext(f"""
            [森空岛明日方舟签到器]已删除旧账号！
            UID：{uid}
            备注：{note}
            """))


@skland.assign("list", parameterless=[Depends(skland_session_extract)])
async def list_(
    bot: Bot,
    event: Event,
    state: T_State,
    db_session: AsyncSession = Depends(get_session),
):
    if not await SUPERUSER(bot, event):
        await skland.finish("您无权查看账号列表！")

    is_group = state.get("is_group")

    def show_token(token: str):
        if not token:
            return "未绑定"
        else:
            if is_group:
                return "已绑定"
            return token

    def report_maker(subscribes: list[SklandSubscribe]):
        report = []
        for i in subscribes:
            report.append(cleantext(f"""
                    UID：{i.uid}
                    TOKEN：{show_token(i.token)}
                    备注：{i.note}
                    """))
        return "\n\n".join(report)

    stmt = select(SklandSubscribe)
    result = (await db_session.scalars(stmt)).all()
    if not result:
        await skland.finish("未能查询到任何账号，请检查")
    await skland.finish(report_maker(list(result)))


@skland.assign("update", parameterless=[Depends(skland_session_extract)])
async def update(
    bot: Bot,
    event: Event,
    identifier: str,
    uid: str | None = None,
    token: str | None = None,
    note: str | None = None,
    db_session: AsyncSession = Depends(get_session),
):
    if not await SUPERUSER(bot, event):
        await skland.finish("您无权更新账号信息！")

    stmt = select(SklandSubscribe).where((SklandSubscribe.uid == identifier) | (SklandSubscribe.note == identifier))
    result = await db_session.scalar(stmt)
    if not result:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")

    if uid:
        result.uid = uid
    if token:
        result.token = token
    if note:
        result.note = note
    await db_session.flush()
    await db_session.commit()
    await skland.finish(cleantext(f"""
            [森空岛明日方舟签到器]已更新账号信息！
            UID：{uid or "未更改"}
            TOKEN：{token or "未更改"}
            备注：{note or "未更改"}
            """))


# 手动签到功能可以在各处使用
@skland.assign("signin")
async def signin(
    bot: Bot,
    event: Event,
    identifier: str,
    db_session: AsyncSession = Depends(get_session),
):
    if not await SUPERUSER(bot, event):
        await skland.finish("您无权手动签到！")

    stmt = select(SklandSubscribe).where((SklandSubscribe.uid == identifier) | (SklandSubscribe.note == identifier))
    result = await db_session.scalar(stmt)
    if not result:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")

    sign_res = await run_sign(uid=result.uid, token=result.token)
    await skland.send(cleantext(f"""
            [森空岛明日方舟签到器]已为账号{result.uid}手动签到！
            信息如下：{sign_res['text']}
            """))
