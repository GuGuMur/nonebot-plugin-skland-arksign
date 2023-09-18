from nonebot_plugin_alconna import Args, Option, Alconna, Subcommand

skland_alc = Alconna(
    "森空岛",
    Subcommand(
        "add",
        Args["uid", int]["token", str],
        [
            Option("-n|--note", Args["note", str]),
        ],
        help_text="添加一个新的签到账号",
    ),
    Subcommand(
        "list",
        [
            Option("-u|--uid", Args["uid", int]),
            Option("-n|--note", Args["note", str]),
        ],
        help_text="列出所有签到账号",
    ),
    Subcommand(
        "del",
        Args["identifier", str],
        help_text="删除一个签到账号",
    ),
    Subcommand(
        "update",
        Args["identifier", str],
        [
            Option("-u|--uid", Args["uid", int]),
            Option("-t|--token", Args["token", str]),
            Option("-n|--note", Args["note", str]),
        ],
        help_text="更新一个签到账号",
    ),
    Subcommand(
        "help",
        help_text="显示帮助信息",
    ),
    Option("-ds|--dont-sign-now", Args["dont_sign_now", bool, True], help_text="不立即签到"),
)
