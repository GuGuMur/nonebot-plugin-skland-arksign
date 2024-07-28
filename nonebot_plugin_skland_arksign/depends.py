from nonebot.compat import model_dump, type_validate_python
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from pydantic import Field
from nonebot_plugin_session import SessionLevel, extract_session
from nonebot_plugin_session_saa import get_saa_target, PlatformTarget
from nonebot_plugin_session import EventSession

from .config import plugin_config


class SklandEventSession(EventSession):
    """用于森空岛插件的EventSession"""

    is_group: bool = Field(default=False, exclude=True)

    @property
    def saa_target(self) -> PlatformTarget | None:
        return get_saa_target(self)

    @property
    def event_user_feature(self) -> dict[str, any]:
        return {
            "bot_type": self.bot_type,
            "platform": self.platform,
            "id1": self.id1,
        }




async def skland_session_extract(bot: Bot, event: Event, matcher: Matcher) -> SklandEventSession:
    """
    从当前会话中提取Session, 按照 plugin_config.skland_arksign_allow_group 的值判断是否允许群聊使用
    """
    session = extract_session(bot, event)
    dump_session = model_dump(session)
    if session.level != SessionLevel.LEVEL1:
        if plugin_config.skland_arksign_allow_group:
            dump_session["is_group"] = True
        else:
            await matcher.finish("请在私聊中使用该指令！")
    return type_validate_python(SklandEventSession, dump_session)
