from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_datastore")
require("nonebot_plugin_saa")
require("nonebot_plugin_session")

from .command import skl_add as skl_add  # noqa: E402
from .command import skl_del as skl_del  # noqa: E402
from .sched import scheduler as scheduler  # noqa: E402

__plugin_meta__ = PluginMetadata(
    name="森空岛明日方舟签到器",
    description="私聊机器人以获得自动明日方舟森空岛签到服务",
    usage="私聊机器人 森空岛 uid token",
    type="application",
    homepage="https://github.com/GuGuMur/nonebot-plugin-skland-arksign",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa", "nonebot_plugin_session"),
)
