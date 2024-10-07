from nonebot import logger, require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_orm")
require("nonebot_plugin_saa")
require("nonebot_plugin_session")
require("nonebot_plugin_alconna")
require("nonebot_plugin_session_saa")

from nonebot_plugin_saa import enable_auto_select_bot

from . import migrations
from .config import plugin_config
from .command import skland as skland
from .sched import scheduler as scheduler

if plugin_config.skland_sm_method_identifier == 0:
    logger.info("选用 dId 获取方案：retrieval-server api")
elif plugin_config.skland_sm_method_identifier == 1:
    logger.info("选用 dId 获取方案：本地 Python 原生模拟")
    try:
        import cryptography as cryptography

        from .did import local_simulate as local_simulate
    except Exception:
        logger.warning("请安装 nonebot-plugin-skland-arksign[sm_local]！")
elif plugin_config.skland_sm_method_identifier == 2:
    logger.info("选用 dId 获取方案：playwright 模拟浏览器")
    try:
        require("nonebot_plugin_htmlrender")
        from .did import html_simulate as html_simulate
    except Exception:
        logger.warning("请安装 nonebot-plugin-skland-arksign[sm_htmlrender]！")


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
