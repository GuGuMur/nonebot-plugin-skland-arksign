from nonebot_plugin_alconna import Args, Option, Alconna, Subcommand, CommandMeta

from .config import plugin_config

skland_alc = Alconna(
    "skland",
    Subcommand(
        "add",
        Args["uid", str]["token?", str],
        Option("-n|--note", Args["note", str]),
        help_text="添加一个新的签到账号",
    ),
    Subcommand(
        "list",
        help_text="列出所有签到账号",
    ),
    Subcommand(
        "del",
        Args["identifier", str],
        help_text="使用uid或者备注删除一个签到账号",
    ),
    Subcommand(
        "update",
        Args["identifier", str],
        [
            Option("-u|--uid", Args["uid", str]),
            Option("-t|--token", Args["token", str]),
            Option("-n|--note", Args["note", str]),
        ],
        help_text="使用uid或者备注更新一个签到账号",
    ),
    Subcommand(
        "bind",
        Args["token", str],
        help_text="在私聊绑定一个在群聊中添加的签到账号",
    ),
    Subcommand(
        "signin",
        Args["identifier", str],
        help_text="使用uid或者备注立刻签到一个账号",
    ),
    meta=CommandMeta(
        description="用于每日定时签到森空岛明日方舟的Nonebot插件",
        usage=plugin_config.init_des,
        example=plugin_config.use_example,
    ),
)
