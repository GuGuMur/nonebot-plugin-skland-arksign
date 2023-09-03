import asyncio
from nonebot.log import logger
from nonebot_plugin_datastore.db import create_session
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Text, PlatformTarget
from sqlalchemy import select
from .model import SklandSubscribe
from .utils import run_sign

@scheduler.scheduled_job("cron", hour=8, id="skland_sched")
# @scheduler.scheduled_job("cron", minute="*/1", id="skland_sched")
async def _():
    logger.info("森空岛签到任务开始执行！")
    stmt = select(SklandSubscribe)
    async with create_session() as session:
        result = await session.scalars(stmt)
        subscribes = result.all()

    for sub in subscribes:
        result = await run_sign(uid=sub.uid, cred=sub.cred)
        logger.info(result)
        msg = Text("[森空岛明日方舟签到器]执行定时任务！\n") + Text(result["text"])

        await msg.send_to(PlatformTarget.deserialize(sub.user))
        await asyncio.sleep(0.2)