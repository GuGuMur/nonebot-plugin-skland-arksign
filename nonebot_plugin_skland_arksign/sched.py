from nonebot import require, get_bot, logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_datastore import get_session
from nonebot_plugin_datastore.db import create_session, post_db_init
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import func
from sqlalchemy import select
from .model import SKLANDACCOUNT
from .utils import run_sign, to_dict

scheduler = require("nonebot_plugin_apscheduler").scheduler

@scheduler.scheduled_job('cron', hour=8, id="skland_sched")
# @scheduler.scheduled_job("cron", minute="*/1", id="skland_sched")
async def _():
    logger.info("森空岛签到任务开始执行！")
    async with create_session() as session:
        users = await session.execute(select(SKLANDACCOUNT))
        users = users.scalars().all()
        users = [to_dict(data) for data in users]
        print(users)
    for i in users:
        result = await run_sign(uid=i["uid"],cred=i["cred"])
        print(result["text"])
        send = await get_bot().send_private_msg(
                    user_id=i["qid"], message="[skland_arksign]执行定时任务！\n"+result["text"]
                )