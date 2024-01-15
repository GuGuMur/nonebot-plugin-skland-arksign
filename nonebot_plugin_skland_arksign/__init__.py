from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_orm")
require("nonebot_plugin_saa")
require("nonebot_plugin_session")
require("nonebot_plugin_alconna")
require("nonebot_plugin_session_saa")

from nonebot_plugin_saa import enable_auto_select_bot

from . import migrations
from .command import skland as skland
from .sched import scheduler as scheduler

enable_auto_select_bot()

__plugin_meta__ = PluginMetadata(
    name="森空岛明日方舟签到器",
    description="私聊机器人以获得自动明日方舟森空岛签到服务",
    usage="在私信或群聊中使用指令 /森空岛 add 游戏账号ID [森空岛token]",
    type="application",
    homepage="https://github.com/GuGuMur/nonebot-plugin-skland-arksign",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa", "nonebot_plugin_session"),
    extra={
        "orm_version_location": migrations,
    },
)
