from sqlalchemy import select, and_, or_
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.adapters import MessageTemplate
from nonebot.adapters import Bot, Event
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import on_alconna, AlconnaArg, AlconnaMatcher, UniMessage
from nonebot_plugin_orm import async_scoped_session
from nonebot_plugin_saa import Text, PlatformTarget

from .utils import cleantext, report_maker
from .sched import sched_sign
from .signin import run_signin
from .alc_parser import skland_alc
from .model import SklandSubscribe
from .depends import skland_session_extract, SklandEventSession

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

skland_add = skland.dispatch("add")
skland_bind = skland.dispatch("bind")
skland_list = skland.dispatch("list")
skland_del = skland.dispatch("del")
skland_update = skland.dispatch("update")
skland_signin_all = skland.dispatch("signin.identifier", "!all")
skland_signin = skland.dispatch("signin")
skland_rebind = skland.dispatch("rebind")


@skland_add.handle()
async def add(
    state: T_State,
    uid: str,
    db_session: async_scoped_session,
    token: str | None = None,
    note: str | None = None,
    quicksignin: bool = True,
    event_session: SklandEventSession = Depends(skland_session_extract),
):
    logger.debug(f"匹配到的参数：{state}")
    user_account = event_session.saa_target
    if not user_account:
        await skland.finish("未能获取到当前会话的可发送用户信息，请检查")
    logger.debug(f"当前会话的用户信息：{user_account.dict()}")

    # 判断是否为私信/群聊 -> depends.skland_session_extract

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
            stmt = select(SklandSubscribe).where(
                and_(SklandSubscribe.note == note, SklandSubscribe.user_feature == event_session.event_user_feature)
            )
            result = await db_session.scalar(stmt)
            if result:
                await skland.finish("该账号备注名已经被您或其他用户注册，请检查")

    # 3. 绑定到数据库里
    new_record = SklandSubscribe(
        uid=uid, user=event_session.dict(), address=user_account.dict(), token=token, note=note, status=None
    )
    db_session.add(new_record)
    await db_session.commit()
    await db_session.refresh(new_record)

    # 这是群聊
    if event_session.is_group:
        # 把sessionb保存到消息数据库里
        if not event_session.id1:
            await skland.finish("不能从群会话提取私聊id，请使用私聊添加账号")
        elif exist_bind := wait_bind_dict.get(event_session.id1):
            await skland.finish(f"已经有一个账号在等待绑定，无法添加新账号！\nUID：{exist_bind}")
        else:
            wait_bind_dict[event_session.id1] = uid

        await skland.finish(
            cleantext(
                f"""
                [森空岛明日方舟签到器]已在群聊{event_session.id2}添加新账号！
                UID：{uid}
                备注：{note or "无"}
                接下来，请你通过`私信`bot /森空岛 bind [该账号对应的token] 来完成定时签到服务！"""
            )
        )

    # 这是私信
    else:
        if not token:
            await skland.finish("请提供token！")

        await skland.send(
            cleantext(
                f"""
                [森空岛明日方舟签到器]已添加新账号！
                UID：{uid}
                TOKEN：{token}
                备注：{note or "无"}
                """
            )
        )
        if quicksignin:
            runres = await run_signin(uid=uid, token=token)
            await skland.finish(f"立即执行签到操作完成！\n{runres.text}")


@skland_bind.handle()
async def bind(
    state: T_State,
    token: str,
    db_session: async_scoped_session,
    quicksignin: bool = True,
    event_session: SklandEventSession = Depends(skland_session_extract),
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
    groupid = skd_user.user.get("id2")
    address = skd_user.address
    logger.debug(f"更新后的SklandSubscribe：{skd_user}")

    # 删除待绑定账号
    del wait_bind_dict[event_session.id1]

    # 发送成功信息（私聊）
    await skland.send(
        cleantext(
            f"""
            [森空岛明日方舟签到器]已经为绑定在群聊的游戏账号绑定TOKEN！
            群聊：{groupid}
            游戏账号UID：{uid}
            TOKEN：{token}
            备注：{note}
            """
        )
    )
    # 再到群聊通知一下
    if quicksignin:
        runres = await run_signin(uid=uid, token=token)
        msg = Text(
            cleantext(
                f"""
                [森空岛明日方舟签到器]用户{event_session.id1}已经通过私信绑定账号{uid}的token！
                立即执行签到操作完成！
                信息如下：{runres.text}"""
            )
        )
        await msg.send_to(PlatformTarget.deserialize(address))
    else:
        ...


@skland_rebind.handle()
async def rebind(
    state: T_State,
    uid: str,
    event_session: SklandEventSession,
    db_session: async_scoped_session,
):
    stmt = select(SklandSubscribe).where(SklandSubscribe.uid == uid)
    result: SklandSubscribe | None = await db_session.scalar(stmt)
    if not result:
        await skland.finish("没有找到需要重新绑定的账户，请检查")
    old_user = result.user
    now_sendto_dict = event_session.saa_target
    if old_user == now_sendto_dict:
        result.user = event_session.dict()
        result.address = now_sendto_dict
        await db_session.flush()
        await db_session.commit()
        await skland.finish(f"已完成UID:{uid}的森空岛账号的用户信息重绑定！")
    else:
        await skland.finish("该账户此前并非您所有，请检查")


# 删除功能可以在各处使用
@skland_del.handle()
async def del_1(
    bot: Bot,
    event: Event,
    state: T_State,
    identifier: str,
    matcher: AlconnaMatcher,
    db_session: async_scoped_session,
    event_session: SklandEventSession = Depends(skland_session_extract),
):
    # if await SUPERUSER(bot, event):
    #     stmt = select(SklandSubscribe).where(SklandSubscribe.user_identity == identifier)
    # else:
    #     stmt = select(SklandSubscribe).where(
    #         and_(
    #             SklandSubscribe.user_identity == identifier,
    #             SklandSubscribe.user_feature == event_session.event_user_feature,
    #         )
    #     )
    # result = (await db_session.scalars(stmt)).all()
    result = (await db_session.scalars(select(SklandSubscribe).where())).all()
    if await SUPERUSER(bot, event):
        ...
    else:
        result = [i for i in result if i.user_identity == identifier]
    if not result:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")
    state["all_subscribes"] = result
    event_session.skland_prompt = (
        "您可执行操作的森空岛签到账号如下：\n"
        + report_maker(result, event_session.is_group)
        + "\n请输入对应序号完成操作！\n"
        + "\n**注意：若输入超出范围的序号，则自动退出处理进程"
    )
    if len(result) == 1:
        matcher.set_path_arg("del.position", 0)


@skland_del.got_path("del.position", prompt=UniMessage.template("{prompt}"))
async def del_2(
    bot: Bot,
    event: Event,
    identifier: str,
    matcher: AlconnaMatcher,
    state: T_State,
    db_session: async_scoped_session,
    event_session: SklandEventSession = Depends(skland_session_extract),
    position: int | None = AlconnaArg("del.position"),
):
    if position not in range(0, len(state["all_subscribes"])):
        await skland.finish("输入的序号超出了您所能控制的账号数，已退出处理进程！")
    subscribe = await db_session.merge(state["all_subscribes"][position])
    uid = subscribe.uid
    note = subscribe.note or "无"
    await db_session.delete(subscribe)
    await db_session.commit()
    await skland.finish(
        cleantext(
            f"""
            [森空岛明日方舟签到器]已删除旧账号！
            UID：{uid}
            备注：{note or "无"}
            """
        )
    )


@skland_list.handle()
async def list_(
    bot: Bot,
    event: Event,
    state: T_State,
    db_session: async_scoped_session,
    event_session: SklandEventSession = Depends(skland_session_extract),
):
    result = (await db_session.scalars(select(SklandSubscribe).where())).all()
    if await SUPERUSER(bot, event):
        ...
    else:
        result = [i for i in result if i.user_feature == event_session.event_user_feature]
    if not result:
        await skland.finish("未能查询到任何账号，请检查")
    await skland.finish(report_maker(list(result), is_show_token=event_session.is_group))


@skland_update.handle()
async def update_1(
    bot: Bot,
    event: Event,
    state: T_State,
    identifier: str,
    matcher: AlconnaMatcher,
    db_session: async_scoped_session,
    event_session: SklandEventSession = Depends(skland_session_extract),
    uid: str | None = None,
    token: str | None = None,
    note: str | None = None,
):
    # 预处理：identifier 不应与 uid 相同
    if isinstance(identifier, int):
        pre_result = (await db_session.scalars(select(SklandSubscribe).where(SklandSubscribe.uid == identifier))).all()
        if pre_result:
            await skland.finish("您要更改的账户的UID已登记在数据库中，请检查")
    # @TODO: 不会写了 呜呜
    # if await SUPERUSER(bot, event):
    #     stmt = select(SklandSubscribe).where(SklandSubscribe.user_identity == identifier)
    # else:
    #     stmt = select(SklandSubscribe).where(
    #         and_(
    #             SklandSubscribe.user_identity == identifier,
    #             SklandSubscribe.user_feature == event_session.event_user_feature,
    #         )
    #     )
    # result = (await db_session.scalars(stmt)).all()
    result = (await db_session.scalars(select(SklandSubscribe).where())).all()
    if await SUPERUSER(bot, event):
        result = [i for i in result if i.user_identity == identifier]
    else:
        result = [
            i for i in result if i.user_identity == identifier and i.user_feature == event_session.event_user_feature
        ]
    if not result:
        await skland.finish("未能使用uid或备注匹配到任何账号，请检查")
    state["all_subscribes"] = result
    # print(result)
    event_session.skland_prompt = (
        "您可执行操作的森空岛签到账号如下：\n"
        + report_maker(result, event_session.is_group)
        + "\n请输入对应序号完成操作！\n"
        + "\n**注意：若输入超出范围的序号，则自动退出处理进程"
    )
    state["prompt"] = (
        "您可执行操作的森空岛签到账号如下：\n"
        + report_maker(result, event_session.is_group)
        + "\n请输入对应序号完成操作！\n"
        + "\n**注意：若输入超出范围的序号，则自动退出处理进程"
    )
    if len(result) == 1:
        matcher.set_path_arg("update.position", 0)


@skland_update.got_path("update.position", prompt=UniMessage.template("{prompt}"))
async def update_2(
    bot: Bot,
    event: Event,
    identifier: str,
    matcher: AlconnaMatcher,
    state: T_State,
    db_session: async_scoped_session,
    event_session: SklandEventSession = Depends(skland_session_extract),
    uid: str | None = None,
    token: str | None = None,
    note: str | None = None,
    position: int | None = AlconnaArg("update.position"),
):
    if position not in range(0, len(state["all_subscribes"])):
        await skland.finish("输入的序号超出了您所能控制的账号数，已退出处理进程！")
    subscribe = await db_session.merge(state["all_subscribes"][position])
    if uid:
        subscribe.uid = uid
    if token:
        subscribe.token = token
    if note:
        subscribe.note = note
    await db_session.flush()
    await db_session.commit()
    await db_session.refresh(subscribe)
    await skland.finish(
        cleantext(
            f"""
            [森空岛明日方舟签到器]已更新账号信息！
            UID：{uid or "未更改"}
            TOKEN：{token or "未更改"}
            备注：{note or "未更改"}
            """
        )
    )


@skland_signin_all.handle()
async def signin_all():
    await sched_sign()
    await skland.finish("所有账号已经手动重新触发签到！")


# 手动签到功能可以在各处使用
@skland_signin.handle()
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
    await skland.finish(
        cleantext(
            f"""
            [森空岛明日方舟签到器]已为账号{result.uid}手动签到！
            信息如下：{sign_res.text}
            """
        )
    )
