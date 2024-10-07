# ID: 2
from pathlib import Path

from nonebot import require

from ...config import plugin_config

if plugin_config.skland_sm_method_identifier == 2:
    require("nonebot_plugin_htmlrender")
    from nonebot_plugin_htmlrender import get_new_page

    async def get_did() -> str:
        async with get_new_page() as page:
            path = Path(__file__).parent / "static"
            await page.goto(path / "index.html")

            button = await page.query_selector("#getDeviceId")
            await button.click()

            await page.wait_for_selector("#deviceIdOutput")
            textbox = await page.query_selector("#deviceIdOutput")
            textbox_value = await textbox.evaluate("node => node.innerText")
        return textbox_value
