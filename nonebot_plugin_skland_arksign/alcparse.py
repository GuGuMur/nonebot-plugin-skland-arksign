from nonebot_plugin_alconna import Args, Option, Alconna, Subcommand
from .config import plugin_config

skland_alc = Alconna(
    "森空岛",
    Subcommand(
        "add",
        Args["uid", int]["token?", str],
        [
            Option("-t|--token", Args["token", str]),
        ],
        help_text=plugin_config.add_des,
    ),
    Subcommand(
        "群token",
        Args["token", str],
        help_text="继承群聊的消息来补充token信息",
    ),
    Subcommand(
        "del",
        Args["identifier", str],
        help_text=plugin_config.del_des,
    ),
    Subcommand(
        "list",
        help_text="列出当前所有签到账号",
    ),
    Subcommand(
        "help",
        help_text="显示帮助信息",
    ),
)
