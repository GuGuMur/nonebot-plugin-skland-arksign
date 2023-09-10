from nonebot import get_driver

config = get_driver().config.dict()

skland_arksign_allow_group: bool = config.get("skland_arksign_allow_group", False)
