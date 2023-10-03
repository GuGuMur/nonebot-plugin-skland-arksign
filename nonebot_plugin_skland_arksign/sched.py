import asyncio
from typing import Any

from sqlalchemy import select
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Text, PlatformTarget
from nonebot_plugin_datastore.db import create_session

from .utils import run_sign
from .model import SklandSubscribe

Target = dict[Any, Any]
Result = dict[str, Any]


@scheduler.scheduled_job("cron", hour=8, id="skland_sched")
# @scheduler.scheduled_job("cron", minute="*/1", id="skland_sched")
async def _():
    logger.info("森空岛签到任务开始执行！")
    stmt = select(SklandSubscribe)
    async with create_session() as session:
        result = await session.scalars(stmt)
        subscribes = result.all()

    sub_groups: dict[Target, list[Result]] = {}
    for sub in subscribes:
        if not sub.token:
            await Text(f"账号{sub.uid}未绑定Token，请重新绑定！").send_to(PlatformTarget.deserialize(sub.user))
            continue
        result = await run_sign(uid=sub.uid, token=sub.token)
        logger.info(f"uid: {sub.uid}, result: {result['status']}")
        logger.debug(result)
        if not sub_groups.get(sub.user):
            sub_groups[sub.user] = []
        sub_groups[sub.user].append(result)
        await asyncio.sleep(0.1)

    for target, results in sub_groups.items():
        msg_header = "[森空岛明日方舟签到器]执行定时任务！\n\n"
        merge_result_text = "\n----------\n".join(i["text"] for i in results)
        msg = Text(msg_header + merge_result_text)
        await msg.send_to(PlatformTarget.deserialize(target))
        await asyncio.sleep(0.2)
