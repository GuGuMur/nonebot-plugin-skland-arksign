import pytest
from nonebug import App


@pytest.mark.asyncio
async def test_runable(app: App):
    from nonebot import require

    require("nonebot_plugin_skland_arksign")
