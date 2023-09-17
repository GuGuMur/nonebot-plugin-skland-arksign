from nonebot import get_driver

from .utils import cleantext

config = get_driver().config.dict()

skland_arksign_allow_group: bool = config.get("skland_arksign_allow_group", False)


def init_des() -> str:
    if skland_arksign_allow_group is True:
        return cleantext("""
            森空岛自动签到插件
            私信使用：森空岛 [游戏账号ID] [森空岛token]
            群聊使用：森空岛 [游戏账号ID] ； 之后通过与bot私聊输入token
            注意：如果在群聊使用请注意安全问题！
            """)
    else:
        return cleantext("""
            森空岛自动签到插件
            使用：森空岛 [游戏账号ID] [森空岛token]
            """)


def del_des() -> str:
    # if skland_arksign_allow_group == True:
    #     return cleantext("""
    #         删除森空岛账号
    #         使用：森空岛.del [游戏账号ID]
    #         注意：
    #           绑定到群聊的账号可以被群管理员删除；
    #           非超级用户只可删除自己绑定的账号；
    #           超级用户可以删除bot数据库内所有账号
    #         """)
    # else:
    return cleantext("""
        删除森空岛账号
        使用：森空岛.del [游戏账号ID]
        注意：非超级用户只可删除自己绑定的账号；超级用户可以删除bot数据库内所有账号
        """)
