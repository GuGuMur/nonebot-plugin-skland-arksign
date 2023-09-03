from nonebot import on_command, require, on_shell_command
from nonebot.adapters.onebot.v11 import Message, PrivateMessageEvent
from nonebot.params import Depends, ShellCommandArgs
from nonebot.rule import ArgumentParser

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import get_session
from nonebot_plugin_datastore.db import create_session, post_db_init
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select, delete
from argparse import Namespace
from .model import SKLANDACCOUNT
from .utils import cleantext, run_sign

init_parser = ArgumentParser(
    add_help=False,
    description=cleantext(
        """森空岛自动签到插件
        使用：森空岛 [游戏账号ID] [森空岛cred]
        """
    ),
)
init_parser.add_argument("uid", type=str, help="tags!")
init_parser.add_argument("cred", type=str, help="tags!")
init_parser.add_argument("-h", "--help", dest="help", action="store_true")
skl_add = on_shell_command("森空岛", aliases={"skd", "skl"}, parser=init_parser)


@skl_add.handle()
async def _(
    event: PrivateMessageEvent,
    session: AsyncSession = Depends(get_session),
    args: Namespace = ShellCommandArgs(),
):
    # 处理帮助
    if args.help:
        await skl_add.finish(init_parser.description)

    useraccount = SKLANDACCOUNT(qid=event.user_id, uid=args.uid, cred=args.cred)

    session.add(useraccount)
    await session.commit()
    await session.refresh(useraccount)
    await skl_add.send(
        cleantext(
            f"""
                                    [森空岛明日方舟签到器]已添加新账号！
                                    QID：{event.user_id}
                                    UID：{args.uid}
                                    CRED：{args.cred}
                                    """
        )
    )
    runres = await run_sign(uid=args.uid, cred=args.cred)
    await skl_add.finish(f"立即执行签到操作完成！\n{runres['text']}")


del_parser = ArgumentParser(
    add_help=False,
    description=cleantext(
        """
        """
    ),
)
del_parser.add_argument("uid", type=str, help="tags!")
del_parser.add_argument("-h", "--help", dest="help", action="store_true")
skl_del = on_shell_command("森空岛.del", aliases={"skd.del", "skl.del"}, parser=del_parser)


@skl_del.handle()
async def _(
    event: PrivateMessageEvent,
    session: AsyncSession = Depends(get_session),
    args: Namespace = ShellCommandArgs(),
):
    async with session.begin():
        result = await session.execute(
            delete(SKLANDACCOUNT).where(SKLANDACCOUNT.uid == args.uid)
        )
        await session.flush()
        await session.commit()
    await skl_add.finish(
        cleantext(
            f"""
                                    [森空岛明日方舟签到器]已删除旧账号！
                                    QID：{event.user_id}
                                    UID：{args.uid}
                                    """
        )
    )
