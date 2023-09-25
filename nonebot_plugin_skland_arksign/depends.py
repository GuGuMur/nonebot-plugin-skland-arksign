from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from nonebot_plugin_session import Session, SessionLevel, extract_session

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
