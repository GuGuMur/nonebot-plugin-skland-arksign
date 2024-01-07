from sqlalchemy import select
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot_plugin_session import EventSession
from sqlalchemy.ext.asyncio import AsyncSession
from nonebot_plugin_datastore import get_session
from nonebot_plugin_saa import Text, PlatformTarget
from nonebot_plugin_session_saa import get_saa_target
from nonebot_plugin_alconna import AlconnaArg, UniMessage, AlconnaMatcher, on_alconna

from .sched import sched_sign
from .signin import run_signin
from .alc_parser import skland_cmd
from .model import SklandSubscribe
from .utils import cleantext, report_maker, compare_user_info
from .depends import skland_is_group, skland_list_subscribes, skland_session_extract

SessionId1 = str
BindUid = str

wait_bind_dict: dict[SessionId1, BindUid] = {}

skland = on_alconna(
    skland_cmd,
    aliases={"skd", "skl", "森空岛"},
    use_cmd_start=True,
    # use_cmd_sep=True,
    auto_send_output=True,
)
skland_add = skland.dispatch("add")
skland_bind = skland.dispatch("bind")
skland_list = skland.dispatch("list")
skland_del = skland.dispatch("del")
skland_update = skland.dispatch("update")
skland_signin = skland.dispatch("signin")
skland_signin_all = skland.dispatch("signin.identifier", "!all")
skland_rebind = skland.dispatch("rebind")


@skland_add.handle()
async def add(
    state: T_State,
    uid: str,
    token: str | None = None,
    note: str | None = None,
    event_session: EventSession = Depends(skland_session_extract),
    db_session: AsyncSession = Depends(get_session),
):
    logger.debug(f"匹配到的参数：{state}")
    send_to_dict = get_saa_target(event_session).dict()
    event_session_dict = event_session.dict()
    if not send_to_dict:
        await skland.finish("未能获取到当前会话的可发送用户信息，请检查")
    # logger.debug(f"当前会话的用户信息：{send_to_target.dict()}")

    # 先添加一个record
    # 1. 检查UID是否被注册
    async with db_session.begin():
        stmt = select(SklandSubscribe).where(SklandSubscribe.uid == uid)
        result = await db_session.scalar(stmt)
        if result:
            await skland.finish("该UID已经被您或其他用户注册，请检查")

    # 2. 检查用户绑定的 note 是否与自己绑的重复
    if note is not None:
        async with db_session.begin():
            stmt = select(SklandSubscribe).where(SklandSubscribe.note == note)
            result: list[SklandSubscribe] = (await db_session.scalars(stmt)).all()
            if any(i for i in result if compare_user_info(i, event_session)):
                await skland.finish("该note已经被您注册，请检查")

    # 3. 绑定到数据库里
    new_record = SklandSubscribe(uid=uid, user=event_session_dict, sendto=send_to_dict, token=token, cred="", note=note)
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
            await skland.finish("请通过 /森空岛 update 指令提供token！")

        await skland.send(cleantext(f"""
                [森空岛明日方舟签到器]已添加新账号！
                UID：{uid}
                TOKEN：{token}
                备注：{note or "无"}
                """))
        runres = await run_signin(uid=uid, token=token)
        await skland.finish(f"立即执行签到操作完成！\n{runres.text}")


@skland_bind.handle()
async def bind(
    state: T_State,
    token: str,
    event_session: EventSession = Depends(skland_session_extract),
    db_session: AsyncSession = Depends(get_session),
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


@skland_list.handle()
async def list_(
    bot: Bot,
    event: Event,
    state: T_State,
    matcher: AlconnaMatcher,
    event_session: EventSession,
    db_session: AsyncSession = Depends(get_session),
):
    is_group = skland_is_group(bot, event)
    all_subscribes: list[SklandSubscribe] = await skland_list_subscribes(bot, event, matcher, db_session)
    if not all_subscribes:
        await skland.finish("当前没有绑定任何森空岛签到账号！")
    await skland.finish("您可查询的森空岛签到账号如下：\n" + report_maker(all_subscribes, is_group))


@skland_del.handle()
async def del_1(
    bot: Bot,
    event: Event,
    state: T_State,
    identifier: str,
    matcher: AlconnaMatcher,
    event_session: EventSession,
    db_session: AsyncSession = Depends(get_session),
):
    all_subscribes = await skland_list_subscribes(bot, event, matcher, db_session)
    is_group = skland_is_group(bot, event)

    all_subscribes = [i for i in all_subscribes if (i.uid == identifier) | (i.note == identifier)]
    if not all_subscribes:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")
    state["prompt"] = (
        "您可执行操作的森空岛签到账号如下：\n" + report_maker(all_subscribes, is_group) + "\n请输入对应序号完成操作！"
    )

    state["all_subscribes"] = all_subscribes
    if len(all_subscribes) == 1:
        matcher.set_path_arg("del.position", 0)


@skland_del.got_path("del.position", prompt=UniMessage.template("{prompt}"))
async def del_2(
    bot: Bot,
    event: Event,
    state: T_State,
    matcher: AlconnaMatcher,
    event_session: EventSession,
    position: int | None = AlconnaArg("del.position"),
    db_session: AsyncSession = Depends(get_session),
):
    if position >= len(state["all_subscribes"]):
        await skland.reject("输入的序号超出了您所能控制的账号数，请重新输入！")
    result = state["all_subscribes"][position]
    uid = result.uid
    note = result.note or "无"
    await db_session.delete(result)
    await db_session.commit()

    await skland.finish(cleantext(f"""
            [森空岛明日方舟签到器]已删除旧账号！
            UID：{uid}
            备注：{note or "无"}
            """))


@skland_update.handle()
async def update_1(
    bot: Bot,
    event: Event,
    state: T_State,
    identifier: str,
    matcher: AlconnaMatcher,
    event_session: EventSession,
    uid: str | None = None,
    token: str | None = None,
    note: str | None = None,
    db_session: AsyncSession = Depends(get_session),
):
    # 动token的操作 还是自己来吧
    is_group = skland_is_group(bot, event)
    stmt = select(SklandSubscribe).where((SklandSubscribe.uid == identifier) | (SklandSubscribe.note == identifier))
    all_subscribes = (await db_session.scalars(stmt)).all()
    if not await SUPERUSER(bot, event):
        all_subscribes = [i for i in all_subscribes if compare_user_info(i, event_session)]
    if not all_subscribes:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")

    if len(all_subscribes) == 1:
        matcher.set_path_arg("update.position", 0)
    state["prompt"] = (
        "您可执行操作的森空岛签到账号如下：\n" + report_maker(all_subscribes, is_group) + "\n请输入对应序号完成操作！"
    )

    state["all_subscribes"] = all_subscribes


@skland_update.got_path("update.position", prompt=UniMessage.template("{prompt}"))
async def update_2(
    bot: Bot,
    event: Event,
    identifier: str,
    matcher: AlconnaMatcher,
    state: T_State,
    event_session: EventSession,
    uid: str | None = None,
    token: str | None = None,
    note: str | None = None,
    position: int | None = AlconnaArg("update.position"),
    db_session: AsyncSession = Depends(get_session),
):
    if position >= len(state["all_subscribes"]):
        await skland.reject("输入的序号超出了您所能控制的账号数，请重新输入！")
    result = state["all_subscribes"][position]
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


@skland_signin_all.handle()
async def signin_all():
    await sched_sign()
    await skland.finish("所有账号已经手动重新触发签到！")


@skland_signin.handle()
async def signin_1(
    bot: Bot,
    event: Event,
    state: T_State,
    identifier: str,
    matcher: AlconnaMatcher,
    event_session: EventSession,
    db_session: AsyncSession = Depends(get_session),
):
    is_group = skland_is_group(bot, event)
    all_subscribes = await skland_list_subscribes(bot, event, matcher, db_session)
    all_subscribes = [i for i in all_subscribes if (i.uid == identifier) | (i.note == identifier)]
    if not all_subscribes:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")
    state["prompt"] = (
        "您可执行操作的森空岛签到账号如下：\n" + report_maker(all_subscribes, is_group) + "\n请输入对应序号完成操作！"
    )
    state["all_subscribes"] = all_subscribes
    if len(all_subscribes) == 1:
        matcher.set_path_arg("signin.position", 0)


@skland_signin.got_path("signin.position", prompt=UniMessage.template("{prompt}"))
async def signin_2(
    bot: Bot,
    event: Event,
    state: T_State,
    matcher: AlconnaMatcher,
    event_session: EventSession,
    position: int | None = AlconnaArg("signin.position"),
    db_session: AsyncSession = Depends(get_session),
):
    if position >= len(state["all_subscribes"]):
        await skland.reject("输入的序号超出了您所能控制的账号数，请重新输入！")
    result = state["all_subscribes"][position]
    sign_res = await run_signin(uid=result.uid, token=result.token)
    await skland.finish(cleantext(f"""
            [森空岛明日方舟签到器]已为账号{result.uid}手动签到！
            信息如下：{sign_res.text}
            """))


@skland_rebind.handle()
async def rebind(
    state: T_State,
    uid: str,
    event_session: EventSession,
    db_session: AsyncSession = Depends(get_session),
):
    stmt = select(SklandSubscribe).where(SklandSubscribe.uid == uid)
    result: SklandSubscribe | None = await db_session.scalar(stmt)
    if not result:
        await skland.finish("没有找到需要重新绑定的账户，请检查")
    old_user = result.sendto
    now_sendto_dict = get_saa_target(event_session).dict()
    if old_user == now_sendto_dict:
        result.user = event_session.dict()
        await db_session.flush()
        await db_session.commit()
        await skland.finish(f"已完成UID:{uid}的森空岛账号的用户信息重绑定！")
    else:
        await skland.finish("该账户此前并非您所有，请检查")
