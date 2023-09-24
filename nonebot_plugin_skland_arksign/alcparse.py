from nonebot_plugin_alconna import Args, Alconna, Subcommand, CommandMeta
from .config import plugin_config

skland_alc = Alconna(
    "森空岛",
    Subcommand(
        "add",
        Args["uid", int]["token?", str],
        help_text=plugin_config.add_des,
    ),
    Subcommand(
        "群token",
        Args["token", str],
        help_text="继承群聊的消息来补充token信息",
    ),
    Subcommand(
        "del",
        Args["uid", str],
        help_text=plugin_config.del_des,
    ),
    Subcommand(
        "list",
        help_text="列出当前所有签到账号",
    ),
    meta=CommandMeta(
        description="用于每日早八定时签到森空岛明日方舟的Nonebot插件",
        usage=plugin_config.init_des,
        example=plugin_config.use_example
    )
)
