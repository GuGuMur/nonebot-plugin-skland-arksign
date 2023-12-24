from nonebot.typing import T_State
from typing import TYPE_CHECKING
from nonebot.permission import SUPERUSER

from nonebot.params import Depends
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from nonebot_plugin_session import Session, SessionLevel, extract_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from nonebot_plugin_datastore import get_session

from .utils import compare_user_info
from .model import SklandSubscribe

from .config import plugin_config


async def skland_session_extract(bot: Bot, event: Event, matcher: Matcher, state: T_State) -> Session:
    """
    从当前会话中提取Session, 按照 plugin_config.skland_arksign_allow_group 的值判断是否允许群聊使用
    """
    session = extract_session(bot, event)
    if session.level != SessionLevel.LEVEL1:
        if plugin_config.skland_arksign_allow_group:
            state["is_group"] = True
            return session
        else:
            await matcher.finish("请在私聊中使用该指令！")

    return session


async def skland_list_subscribes(
    bot: Bot,
    event: Event,
    matcher: Matcher,
    state: T_State,
    db_session: AsyncSession = Depends(get_session),
) -> Session:
    """
    根据用户组生成其能获取的订阅列表，文本生成逻辑应写在业务处
    """
    event_session = skland_session_extract(bot, event, matcher, state)
    is_group = state.get("is_group")
    flag: bool = False
    # SUPERUSER 的 list：返回全部
    if await SUPERUSER(bot, event):
        flag = True
        stmt = select(SklandSubscribe)
        result = (await db_session.scalars(stmt)).all()
        if not result:
            await matcher.finish("未能查询到任何账号，请检查")
        state["all_subscribes"] = result

    # QQ群管理的list：返回当前群聊的所有绑定
    elif is_group and flag is False:
        flag = True
        if not bot.adapter.get_name() == "OneBot V11":
            await matcher.finish("当前的森空岛签到插件无法提供Onebot V11外的群聊绑定记录...")
        if TYPE_CHECKING:
            from nonebot.adapters.onebot.v11.bot import Bot as OneBotV11Bot

            assert isinstance(bot, OneBotV11Bot)
        from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER

        if not (await GROUP_ADMIN(bot, event) or await GROUP_OWNER(bot, event)):
            await matcher.finish("您不是本群的管理员或群主，请通过私聊获取您的个人绑定记录！")

        stmt = select(SklandSubscribe).where(SklandSubscribe.sendto.group_id == event_session.id2)
        result = (await db_session.scalars(stmt)).all()
        if not result:
            await matcher.finish("未能查询到任何账号，请检查")
        state["all_subscribes"] = result

    # 普通用户的list：返回该用户绑定的所有账号
    else:
        stmt = select(SklandSubscribe)
        result: list[SklandSubscribe] = (await db_session.scalars(stmt)).all()
        result = [i for i in result if compare_user_info(i.user, event_session.dict())]
        if not result:
            await matcher.finish("未能查询到任何账号，请检查")
        state["all_subscribes"] = result

    return event_session
