from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_datastore")
require("nonebot_plugin_saa")
require("nonebot_plugin_session")

from nonebot_plugin_saa.utils.auto_select_bot import enable_auto_select_bot

from .command import skl_add as skl_add
from .command import skl_del as skl_del
from .sched import scheduler as scheduler
from .command import group_add_token as group_add_token

enable_auto_select_bot()

__plugin_meta__ = PluginMetadata(
    name="森空岛明日方舟签到器",
    description="私聊机器人以获得自动明日方舟森空岛签到服务",
    usage="在私信或群聊中使用指令 /森空岛 游戏账号ID [森空岛token]",
    type="application",
    homepage="https://github.com/GuGuMur/nonebot-plugin-skland-arksign",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa", "nonebot_plugin_session"),
)
