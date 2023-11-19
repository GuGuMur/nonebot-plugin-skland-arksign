from nonebot import get_driver
from pydantic import BaseModel

from .utils import cleantext


class Config(BaseModel):
    skland_arksign_allow_group: bool = False
    skland_timestamp_delay: int = 2
    skland_use_web_timestamp: bool = False

    @property
    def init_des(self) -> str:
        if self.skland_arksign_allow_group is True:
            return cleantext("""
                森空岛自动签到插件
                私信使用：森空岛 add [游戏账号ID] [森空岛token]
                群聊使用：森空岛 add [游戏账号ID] ； 之后通过与bot私聊输入token
                如何获取token：登录森空岛（https://www.skland.com/ ）后访问网址（https://web-api.skland.com/account/info/hg ），看到的"content"中内容即为token。
                注意：如果在群聊使用请注意安全问题！
                """)
        else:
            return cleantext("""
                森空岛自动签到插件
                使用：森空岛 add [游戏账号ID] [森空岛token]
                如何获取token：登录森空岛（https://www.skland.com/ ）后访问网址（https://web-api.skland.com/account/info/hg ），看到的"content"中内容即为token。
                """)

    @property
    def del_des(self) -> str:
        return cleantext("""
            删除森空岛账号
            使用：森空岛 del [游戏账号ID]
            注意：非超级用户只可删除自己绑定的账号；超级用户可以删除bot数据库内所有账号
            """)

    @property
    def use_example(self) -> str:
        return cleantext("""
            /森空岛 add [游戏账号ID] [森空岛token]
            /森空岛 del [游戏账号ID]
            /森空岛 list
            * 注意检查 游戏账号ID 和 森空岛token 是否正确和配对
            """)


plugin_config: Config = Config.parse_obj(get_driver().config)
