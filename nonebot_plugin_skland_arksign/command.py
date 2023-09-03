from argparse import Namespace
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from nonebot import on_shell_command
from nonebot.adapters import Event, Bot
from nonebot.params import Depends, ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.rule import ArgumentParser
from nonebot_plugin_datastore import get_session
from nonebot_plugin_session import extract_session, SessionLevel

from .model import SklandSubscribe
from .utils import cleantext, run_sign

init_parser = ArgumentParser(
    add_help=False,
    description=cleantext(
        """森空岛自动签到插件
        使用：森空岛 [游戏账号ID] [森空岛cred]
        注意：如果在群聊使用请注意安全问题！
        """
    ),
)
init_parser.add_argument("uid", type=str, help="tags!")
init_parser.add_argument("cred", type=str, help="tags!")
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
    if session.level != SessionLevel.LEVEL1:
        await skl_add.finish("请在私聊中使用")

    user_account = session.get_saa_target()
    if not user_account:
        await skl_add.finish("未能获取到当前会话的用户信息，请检查")

    assert user_account
    new_record = SklandSubscribe(user=user_account.dict(), uid=args.uid, cred=args.cred)

    db_session.add(new_record)
    await db_session.commit()
    await db_session.refresh(new_record)
    await skl_add.send(
        cleantext(
            f"""
            [森空岛明日方舟签到器]已添加新账号！
            UID：{new_record.uid}
            CRED：{new_record.cred}
            """
        )
    )
    runres = await run_sign(uid=args.uid, cred=args.cred)
    await skl_add.finish(f"立即执行签到操作完成！\n{runres['text']}")


del_parser = ArgumentParser(
    add_help=False,
    description="删除森空岛账号",
)
del_parser.add_argument("uid", type=str, help="tags!")
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
    stmt = select(SklandSubscribe).where(SklandSubscribe.uid == args.uid)
    result = await db_session.scalar(stmt)

    if not result:
        await skl_add.finish("未找到该账号！")
    assert result

    if not SUPERUSER:
        user = extract_session(bot, event).get_saa_target()
        if not user:
            await skl_add.finish("未能获取到当前会话的用户信息，请检查")
        assert user

        if user.dict() != result.user:
            await skl_add.finish("您无权删除该账号！")

    await db_session.delete(result)
    await db_session.commit()

    await skl_add.finish(
        cleantext(
            f"""
            [森空岛明日方舟签到器]已删除旧账号！
            UID：{args.uid}
            """
        )
    )
