from argparse import Namespace

from sqlalchemy import select
from nonebot.adapters import Bot, Event
from nonebot.rule import ArgumentParser
from nonebot.permission import SUPERUSER
from sqlalchemy.ext.asyncio import AsyncSession
from nonebot import get_driver, on_shell_command
from nonebot.params import Depends, ShellCommandArgs
from nonebot_plugin_datastore import get_session, create_session
from nonebot_plugin_session import SessionLevel, extract_session
from nonebot_plugin_session.model import SessionModel, get_or_add_session_model

from .config import Config
from .model import SklandSubscribe
from .utils import run_sign, cleantext

plugin_config: Config = Config.parse_obj(get_driver().config).weather

init_parser = ArgumentParser(add_help=False, description=plugin_config.init_des())
init_parser.add_argument("uid", type=str, help="游戏账号ID", nargs="?", default="")
init_parser.add_argument("token", type=str, help="森空岛token", nargs="?", default="")
init_parser.add_argument("-h", "--help", dest="help", action="store_true")
skl_add = on_shell_command("森空岛", aliases={"skd", "skl"}, parser=init_parser)


@skl_add.handle()
async def _(
    bot: Bot,
    event: Event,
    db_session: AsyncSession = Depends(get_session),
    args: Namespace = ShellCommandArgs(),
):
    # 处理帮助
    if args.help:
        await skl_add.finish(init_parser.description)

    session = extract_session(bot, event)

    user_account = session.get_saa_target()
    if not user_account:
        await skl_add.finish("未能获取到当前会话的用户信息，请检查")
    assert user_account

    # 根据Session判断是否为私信/群聊

    # 这是群聊
    if session.level != SessionLevel.LEVEL1:
        if not plugin_config.skland_arksign_allow_group:
            await skl_add.finish("请在私聊中使用该指令！")
        else:
            # 先添加一个record
            group_new_record = SklandSubscribe(user=user_account.dict(), uid=args.uid, token="", cred="")
            db_session.add(group_new_record)
            await db_session.commit()
            await db_session.refresh(group_new_record)
            # 然后把session注册到消息数据库里
            async with create_session() as db_session:
                await get_or_add_session_model(session, db_session)
            # 最后回应一下
            await skl_add.finish(cleantext(f"""
                [森空岛明日方舟签到器]已在群聊{session.id2}添加新账号！
                UID：{group_new_record.uid}
                接下来，请你通过私信bot /森空岛.group_add_token [该账号对应的token]来获得定时签到服务！"""))

    # 这是私信
    else:
        private_new_record = SklandSubscribe(user=user_account.dict(), uid=args.uid, token=args.token, cred="")

        db_session.add(private_new_record)
        await db_session.commit()
        await db_session.refresh(private_new_record)
        await skl_add.send(cleantext(f"""
                [森空岛明日方舟签到器]已添加新账号！
                UID：{private_new_record.uid}
                TOKEN：{private_new_record.token}
                """))
        runres = await run_sign(uid=args.uid, token=args.token)
        await skl_add.finish(f"立即执行签到操作完成！\n{runres['text']}")


group_add_token_parser = ArgumentParser(
    add_help=False,
    description=cleantext("""
            森空岛明日方舟签到器
            在通过群聊注册账号到群聊后，私聊机器人/森空岛.group_add_token [账号对应的token]来获得定时签到服务！"""),
)
group_add_token_parser.add_argument("token", type=str, help="森空岛token", nargs="?", default="")
group_add_token_parser.add_argument("-h", "--help", dest="help", action="store_true")
group_add_token = on_shell_command(
    "森空岛.group_add_token", aliases={"skd.group_add_token", "skl.group_add_token"}, parser=group_add_token_parser
)


@group_add_token.handle()
async def _(
    bot: Bot,
    event: Event,
    db_session: AsyncSession = Depends(get_session),
    args: Namespace = ShellCommandArgs(),
):
    # 处理帮助
    if args.help:
        await group_add_token.finish(group_add_token_parser.description)

    session = extract_session(bot, event)

    user_account = session.get_saa_target()
    if not user_account:
        await group_add_token.finish("未能获取到当前会话的用户信息，请检查")
    assert user_account

    if session.level != SessionLevel.LEVEL1:
        if not plugin_config.skland_arksign_allow_group:
            await group_add_token.finish("请在私聊中使用该指令！")

    # 先找到私聊用户对应的群聊Session
    async with db_session.begin():
        group_messages = await db_session.execute(select(SessionModel).where(SessionModel.id1 == session.id1))
        group_session: SessionModel | None = group_messages.scalars().first()
        if not group_session:
            await group_add_token.finish("请检查您是否先在任意群聊注册自动签到！")
        else:
            if group_session_dict := group_session.session.get_saa_target():
                group_session_id = group_session.id2
                session_user_id = group_session.id1
            else:
                await group_add_token.finish("先前绑定的群聊会话信息有误，请检查")
    # 再更新SklandSubscribe
    async with db_session.begin():
        stmt = select(SklandSubscribe).where(SklandSubscribe.user == group_session_dict)
        skd_users = await db_session.scalars(stmt)
        skd_user: SklandSubscribe | None = skd_users.first()
        skd_user.token = args.token
        skd_user_token = skd_user.token
        skd_user_uid = skd_user.uid
        skd_user_send_saa_target = skd_user.user
        await db_session.flush()
        await db_session.commit()
    # 再发送信息
    # await group_add_token.send(cleantext(f"""
    #             [森空岛明日方舟签到器]已经为绑定在群聊的游戏账号{skd_user.token}绑定TOKEN！
    #             群聊ID：{group_session.id2}
    #             游戏账号UID：{skd_user.uid}
    #             TOKEN：{skd_user.token}
    #             """))
    await group_add_token.send(cleantext(f"""
            [森空岛明日方舟签到器]已经为绑定在群聊的游戏账号绑定TOKEN！
            群聊ID：{group_session_id}
            游戏账号UID：{skd_user_uid}
            TOKEN：{skd_user_token}
            """))
    # 再到群聊通知一下
    from nonebot_plugin_saa import Text, PlatformTarget

    runres = await run_sign(uid=skd_user_uid, token=args.token)
    msg = Text(cleantext(f"""
        [森空岛明日方舟签到器]用户{session_user_id}已经通过私信绑定账号{skd_user_uid}的token！
        立即执行签到操作完成！
        信息如下：{runres['text']}"""))
    await msg.send_to(PlatformTarget.deserialize(skd_user_send_saa_target))
    # 最后删掉Session数据库里的消息
    async with db_session.begin():
        await db_session.execute(SessionModel.__table__.delete().where(SessionModel.id1 == session.id1))
        await db_session.commit()


del_parser = ArgumentParser(add_help=False, description=plugin_config.del_des())
del_parser.add_argument("uid", type=str, help="游戏账号ID", nargs="?", default="")
del_parser.add_argument("-h", "--help", dest="help", action="store_true")
skl_del = on_shell_command("森空岛.del", aliases={"skd.del", "skl.del"}, parser=del_parser)


# 删除功能可以在各处使用
@skl_del.handle()
async def _(
    bot: Bot,
    event: Event,
    db_session: AsyncSession = Depends(get_session),
    args: Namespace = ShellCommandArgs(),
):
    # 处理帮助
    if args.help:
        await skl_del.finish(init_parser.description)

    stmt = select(SklandSubscribe).where(SklandSubscribe.uid == args.uid)
    result = await db_session.scalar(stmt)

    if not result:
        await skl_del.finish("未找到该账号！")
    assert result

    if not SUPERUSER:
        user = extract_session(bot, event).get_saa_target()
        if not user:
            await skl_del.finish("未能获取到当前会话的用户信息，请检查")
        assert user

        if user.dict() != result.user:
            await skl_del.finish("您无权删除该账号！")

    await db_session.delete(result)
    await db_session.commit()

    await skl_del.finish(cleantext(f"""
            [森空岛明日方舟签到器]已删除旧账号！
            UID：{args.uid}
            """))
