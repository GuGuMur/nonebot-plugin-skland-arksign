from .command import *
from .sched import *
from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name="森空岛明日方舟定时自动签到",
    description="私聊机器人以获得自动明日方舟森空岛签到服务",
    usage="私聊机器人森空岛 uid cred",
    type="application",
    homepage="https://github.com/GuGuMur/nonebot-plugin-skland-arksign",
    supported_adapters={"~onebot.v11"},
)