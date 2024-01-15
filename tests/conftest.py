from pathlib import Path

import pytest
import nonebot
from sqlalchemy import delete
from pytest_mock import MockerFixture
from nonebug import NONEBOT_INIT_KWARGS, App
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter
from nonebot.adapters.onebot.v12 import Adapter as OnebotV12Adapter


def pytest_configure(config: pytest.Config) -> None:
    config.stash[NONEBOT_INIT_KWARGS] = {
        "sqlalchemy_database_url": "sqlite+aiosqlite:///:memory:",
        "alembic_startup_check": False,
        "superusers": [
            "10",
        ],
    }


@pytest.fixture(scope="session", autouse=True)
def load_adapters(nonebug_init: None):
    driver = nonebot.get_driver()
    driver.register_adapter(OnebotV11Adapter)
    driver.register_adapter(OnebotV12Adapter)
    return driver


@pytest.fixture()
async def app(app: App, mocker: MockerFixture, tmp_path: Path):
    # 加载插件
    # nonebot.require("nonebot_plugin_orm")
    nonebot.require("nonebot_plugin_skland_arksign")
    from nonebot_plugin_orm import init_orm, get_session

    mocker.patch("nonebot_plugin_orm._data_dir", tmp_path / "orm")

    await init_orm()

    yield app

    # 清理数据库

    from nonebot_plugin_skland_arksign.model import SklandSubscribe

    async with get_session() as session, session.begin():
        await session.execute(delete(SklandSubscribe))


@pytest.fixture()
async def session(app: App):
    from nonebot_plugin_orm import get_session

    async with get_session() as session:
        yield session
