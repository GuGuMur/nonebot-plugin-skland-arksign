from sqlalchemy import select
from nonebot.params import Depends
from nonebot.adapters import Bot, Event
from nonebot.permission import SUPERUSER
from sqlalchemy.ext.asyncio import AsyncSession
from nonebot_plugin_alconna import Match, on_alconna
from nonebot_plugin_datastore import get_session, create_session
from nonebot_plugin_session import SessionLevel, extract_session
from nonebot_plugin_session.model import SessionModel, get_or_add_session_model

from .alcparse import skland_alc
from .config import plugin_config
from .model import SklandSubscribe
from .utils import run_sign, cleantext

skland = on_alconna(
    skland_alc, aliases={"skd", "skl", "skland"}, use_cmd_start=True, use_cmd_sep=True, auto_send_output=True
)


@skland.assign("add")
async def add_processor(
    bot: Bot,
    event: Event,
    uid: Match[str],
    token: Match[str],
    db_session: AsyncSession = Depends(get_session),
):
    session = extract_session(bot, event)

    user_account = session.get_saa_target()
    if not user_account:
        await skland.finish("未能获取到当前会话的用户信息，请检查")
    assert user_account

    # 根据Session判断是否为私信/群聊

    # 这是群聊
    if session.level != SessionLevel.LEVEL1:
        if not plugin_config.skland_arksign_allow_group:
            await skland.finish("请在私聊中使用该指令！")
        else:
            # 先添加一个record
            group_new_record = SklandSubscribe(user=user_account.dict(), uid=uid.result, token="", cred="")
            db_session.add(group_new_record)
            await db_session.commit()
            await db_session.refresh(group_new_record)
            # 然后把session注册到消息数据库里
            async with create_session() as db_session:
                await get_or_add_session_model(session, db_session)
            # 最后回应一下
            await skland.finish(cleantext(f"""
                [森空岛明日方舟签到器]已在群聊{session.id2}添加新账号！
                UID：{group_new_record.uid}
                接下来，请你通过私信bot /森空岛 群token [该账号对应的token]来获得定时签到服务！"""))

    # 这是私信
    else:
        if uid.available:
            private_new_record = SklandSubscribe(user=user_account.dict(), uid=uid.result, token=token.result, cred="")
            db_session.add(private_new_record)
            await db_session.commit()
            await db_session.refresh(private_new_record)
            await skland.send(cleantext(f"""
                    [森空岛明日方舟签到器]已添加新账号！
                    UID：{private_new_record.uid}
                    TOKEN：{private_new_record.token}
                    """))
            runres = await run_sign(uid=uid.result, token=token.result)
            await skland.finish(f"立即执行签到操作完成！\n{runres['text']}")
        else:
            await skland.finish("请重新执行该命令并补充token！")


@skland.assign("群token")
async def group_add_token_processor(
    bot: Bot,
    event: Event,
    token: Match[str],
    db_session: AsyncSession = Depends(get_session),
):
    session = extract_session(bot, event)

    user_account = session.get_saa_target()
    if not user_account:
        await skland.finish("未能获取到当前会话的用户信息，请检查")
    assert user_account


    if session.level != SessionLevel.LEVEL1:
        if not plugin_config.skland_arksign_allow_group:
            await skland.finish("请在私聊中使用该指令！")

    # 先找到私聊用户对应的群聊Session
    async with db_session.begin():
        group_messages = await db_session.execute(select(SessionModel).where(SessionModel.id1 == session.id1))
        group_session: SessionModel | None = group_messages.scalars().first()
        if not group_session:
            await skland.finish("请检查您是否先在任意群聊注册自动签到！")
            return
        elif group_session_dict := group_session.session.get_saa_target().dict():
            group_session_id: str | None = group_session.id2
            user_session_id: str | None = group_session.id1
        else:
            await skland.finish("先前绑定的群聊会话信息有误，请检查")
            return
    # 再更新SklandSubscribe
    async with db_session.begin():
        stmt = select(SklandSubscribe).where(SklandSubscribe.user == group_session_dict)
        skd_users = await db_session.scalars(stmt)
        skd_user: SklandSubscribe | None = skd_users.first()
        skd_user.token = token.result
        skd_user_token = skd_user.token
        skd_user_uid = skd_user.uid
        skd_user_send_saa_target = skd_user.user
        await db_session.flush()
        await db_session.commit()
    # 再发送信息
    await skland.send(cleantext(f"""
            [森空岛明日方舟签到器]已经为绑定在群聊的游戏账号绑定TOKEN！
            群聊ID：{group_session_id}
            游戏账号UID：{skd_user_uid}
            TOKEN：{skd_user_token}
            """))
    # 再到群聊通知一下
    from nonebot_plugin_saa import Text, PlatformTarget

    runres = await run_sign(uid=skd_user_uid, token=token.result)
    msg = Text(cleantext(f"""
        [森空岛明日方舟签到器]用户{user_session_id}已经通过私信绑定账号{skd_user_uid}的token！
        立即执行签到操作完成！
        信息如下：{runres['text']}"""))
    await msg.send_to(PlatformTarget.deserialize(skd_user_send_saa_target))
    # 最后删掉Session数据库里的消息
    async with db_session.begin():
        delete_session_stmt = select(SessionModel).where(SessionModel.id1 == session.id1)
        result = await db_session.scalars(delete_session_stmt)
        result = result.all()
        for i in result:
            await db_session.delete(i)
        await db_session.flush()
        await db_session.commit()


@skland.assign("del")
async def delete_processor(
    bot: Bot,
    event: Event,
    uid: Match[str],
    db_session: AsyncSession = Depends(get_session),
):
    stmt = select(SklandSubscribe).where(SklandSubscribe.uid == uid.result)
    result = await db_session.scalar(stmt)

    if not result:
        await skland.finish("未找到该账号！")
    assert result

    if not SUPERUSER:
        user = extract_session(bot, event).get_saa_target()
        if not user:
            await skland.finish("未能获取到当前会话的用户信息，请检查")
        assert user

        if user.dict() != result.user:
            await skland.finish("您无权删除该账号！")

    await db_session.delete(result)
    await db_session.commit()
    await skland.finish(cleantext(f"""
            [森空岛明日方舟签到器]已删除旧账号！
            UID：{uid.result}
            """))


@skland.assign("list")
async def list_processor(
    bot: Bot,
    event: Event,
    db_session: AsyncSession = Depends(get_session),
):
    msg_session = extract_session(bot, event)

    user_account = msg_session.get_saa_target()
    if not user_account:
        await skland.finish("未能获取到当前会话的用户信息，请检查")
    assert user_account

    stmt = select(SklandSubscribe)
    async with create_session() as session:
        result = await session.scalars(stmt)
        subscribes = result.all()

    current_subs = []
    for sub in subscribes:
        if msg_session.dict() == sub.user:
            current_subs.append(sub)

    if not current_subs:
        await skland.finish("您当前的聊天账号未绑定任何森空岛签到账号！")
    else:
        text = "您当前的聊天账号绑定了以下森空岛签到账号：" + "\n".join([f"{i.uid}" for i in current_subs])
        await skland.finish(text)
