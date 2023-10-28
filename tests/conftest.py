import pytest
import nonebot

# 导入适配器


@pytest.fixture(scope="session", autouse=True)
def load_bot():
    # 加载适配器
    driver = nonebot.get_driver()
    nonebot.load_from_toml("pyproject.toml")
    return driver
