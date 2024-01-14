import asyncio
from typing import Any

from sqlalchemy import select
from nonebot.log import logger
from nonebot_plugin_orm import get_session
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Text, PlatformTarget

from .model import SklandSubscribe
from .signin import SignResult, run_signin

Result = dict[str, Any]


@scheduler.scheduled_job("cron", hour=8, id="skland_sched")
# @scheduler.scheduled_job("cron", minute="*/1", id="skland_sched")
async def sched_sign():
    logger.info("森空岛签到任务开始执行！")
    stmt = select(SklandSubscribe)
    async with get_session() as session:
        result = await session.scalars(stmt)
        subscribes = result.all()

    sub_groups: dict[PlatformTarget, list[SignResult]] = {}
    for sub in subscribes:
        target = PlatformTarget.deserialize(sub.user)
        logger.debug(f"target: {target.dict()}")
        if not sub.token:
            await Text(f"账号{sub.uid}未绑定Token，请重新绑定！").send_to(target)
            continue
        result = await run_signin(uid=sub.uid, token=sub.token)
        logger.info(f"uid: {sub.uid}, result: {result.status}")
        logger.debug(result)
        if not sub_groups.get(target):
            sub_groups[target] = []
        sub_groups[target].append(result)
        await asyncio.sleep(0.1)

    logger.debug(f"{sub_groups=}")
    for target, results in sub_groups.items():
        msg_header = "[森空岛明日方舟签到器]执行定时任务！\n\n"
        merge_result_text = "\n----------\n".join(i.text for i in results)
        msg = Text(msg_header + merge_result_text)
        await msg.send_to(target)
        await asyncio.sleep(0.2)
