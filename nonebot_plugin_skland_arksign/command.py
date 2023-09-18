from nonebot.params import Depends
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna import on_alconna
from sqlalchemy.ext.asyncio import AsyncSession
from nonebot_plugin_datastore import get_session

from .alcparse import skland_alc

skland = on_alconna(
    skland_alc,
    aliases={"skd", "skl", "skland"},
    use_cmd_start=True,
)


@skland.assign("add")
async def add_processor(
    bot: Bot,
    Event: Event,
    uid: int,
    token: str,
    db_session: AsyncSession = Depends(get_session),
    note: str | None = None,
    dont_sign_now: bool = False,
):
    await skland.finish(f"uid: {uid}, token: {token}, note: {note}, dont_sign_now: {dont_sign_now}")
    # await skland.finish("add")
