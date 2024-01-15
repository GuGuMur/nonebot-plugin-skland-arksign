from sqlalchemy import select
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_orm import async_scoped_session
from nonebot_plugin_saa import Text, PlatformTarget
from nonebot_plugin_session_saa import get_saa_target
from nonebot_plugin_session import EventSession, extract_session

from .utils import cleantext
from .sched import sched_sign
from .signin import run_signin
from .alc_parser import skland_alc
from .model import SklandSubscribe
from .depends import skland_session_extract

SessionId1 = str
BindUid = str

wait_bind_dict: dict[SessionId1, BindUid] = {}

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
    db_session: async_scoped_session,
    token: str | None = None,
    note: str | None = None,
    event_session: EventSession = Depends(skland_session_extract),
):
    logger.debug(f"匹配到的参数：{state}")
    user_account = get_saa_target(event_session)
    if not user_account:
        await skland.finish("未能获取到当前会话的可发送用户信息，请检查")
    logger.debug(f"当前会话的用户信息：{user_account.dict()}")

    # 判断是否为私信/群聊

    # 先添加一个record
    stmt = select(SklandSubscribe).where(SklandSubscribe.uid == uid)
    result = await db_session.scalar(stmt)
    if result:
        await skland.finish("该UID已经被注册，请检查")
    new_record = SklandSubscribe(user=user_account.dict(), uid=uid, token=token, cred="", note=note)
    db_session.add(new_record)
    await db_session.commit()
    await db_session.refresh(new_record)

    # 这是群聊
    if state.get("is_group"):
        # 把sessionb保存到消息数据库里
        if not event_session.id1:
            await skland.finish("不能从群会话提取私聊id，请使用私聊添加账号")
        elif exist_bind := wait_bind_dict.get(event_session.id1):
            await skland.finish(f"已经有一个账号在等待绑定，无法添加新账号！\nUID：{exist_bind}")
        else:
            wait_bind_dict[event_session.id1] = uid

        await skland.finish(cleantext(f"""
            [森空岛明日方舟签到器]已在群聊{event_session.id2}添加新账号！
            UID：{uid}
            备注：{note or "无"}
            接下来，请你通过`私信`bot /森空岛 bind [该账号对应的token] 来完成定时签到服务！"""))

    # 这是私信
    else:
        if not token:
            await skland.finish("请提供token！")

        await skland.send(cleantext(f"""
                [森空岛明日方舟签到器]已添加新账号！
                UID：{uid}
                TOKEN：{token}
                备注：{note or "无"}
                """))
        runres = await run_signin(uid=uid, token=token)
        await skland.finish(f"立即执行签到操作完成！\n{runres.text}")


@skland.assign("bind")
async def bind(
    state: T_State,
    token: str,
    db_session: async_scoped_session,
    event_session: EventSession = Depends(skland_session_extract),
):
    logger.debug(f"匹配到的参数：{state}")
    if not event_session.id1:
        await skland.finish("不能提取私聊id，请更换私聊方式或者聊天平台")
    # 先找到私聊用户对应的待绑定账号
    bind_uid = wait_bind_dict.get(event_session.id1)
    if not bind_uid:
        await skland.finish("请先在群聊添加账号，再通过私聊绑定")

    # 判断是否有与SklandSubscribe匹配的用户
    get_skland_subscribe_stmt = select(SklandSubscribe).where(SklandSubscribe.uid == bind_uid)
    # uid是主键，所以只会有一个
    skd_user: SklandSubscribe | None = (await db_session.scalars(get_skland_subscribe_stmt)).one_or_none()
    logger.debug(f"查询到的SklandSubscribe：{skd_user}")
    if not skd_user:
        await skland.finish("未能匹配到你在群聊注册的账号，请检查")
    skd_user.token = token
    # 保存到数据库
    await db_session.commit()
    await db_session.refresh(skd_user)

    uid = skd_user.uid
    note = skd_user.note or "无"
    user = skd_user.user
    logger.debug(f"更新后的SklandSubscribe：{skd_user}")

    # 删除待绑定账号
    del wait_bind_dict[event_session.id1]

    # 发送成功信息（私聊）
    await skland.send(cleantext(f"""
            [森空岛明日方舟签到器]已经为绑定在群聊的游戏账号绑定TOKEN！
            群聊：{user}
            游戏账号UID：{uid}
            TOKEN：{token}
            备注：{note}
            """))
    # 再到群聊通知一下
    runres = await run_signin(uid=uid, token=token)
    msg = Text(cleantext(f"""
        [森空岛明日方舟签到器]用户{event_session.id1}已经通过私信绑定账号{uid}的token！
        立即执行签到操作完成！
        信息如下：{runres.text}"""))
    await msg.send_to(PlatformTarget.deserialize(user))


# 删除功能可以在各处使用
@skland.assign("del")
async def del_(
    bot: Bot,
    event: Event,
    identifier: str,
    db_session: async_scoped_session,
    event_session: EventSession = Depends(extract_session),
):
    # identifier 可以是uid或者备注, 需要都尝试一下
    stmt = select(SklandSubscribe).where((SklandSubscribe.uid == identifier) | (SklandSubscribe.note == identifier))
    result = await db_session.scalar(stmt)
    if not result:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")

    if not await SUPERUSER(bot, event):
        user = get_saa_target(event_session)
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
            备注：{note or "无"}
            """))


@skland.assign("list", parameterless=[Depends(skland_session_extract)])
async def list_(
    bot: Bot,
    event: Event,
    state: T_State,
    db_session: async_scoped_session,
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
    db_session: async_scoped_session,
    uid: str | None = None,
    token: str | None = None,
    note: str | None = None,
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


@skland.assign("signin.identifier", "!all")
async def signin_all():
    await sched_sign()
    await skland.finish("所有账号已经手动重新触发签到！")


# 手动签到功能可以在各处使用
@skland.assign("signin")
async def signin(
    bot: Bot,
    event: Event,
    identifier: str,
    db_session: async_scoped_session,
):
    if not await SUPERUSER(bot, event):
        await skland.finish("您无权手动签到！")

    stmt = select(SklandSubscribe).where((SklandSubscribe.uid == identifier) | (SklandSubscribe.note == identifier))
    result = await db_session.scalar(stmt)
    if not result:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")

    sign_res = await run_signin(uid=result.uid, token=result.token)
    await skland.finish(cleantext(f"""
            [森空岛明日方舟签到器]已为账号{result.uid}手动签到！
            信息如下：{sign_res.text}
            """))
