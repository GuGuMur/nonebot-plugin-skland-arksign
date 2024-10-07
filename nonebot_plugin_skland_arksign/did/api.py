# ID: 0
from httpx import AsyncClient

from ..config import plugin_config


async def get_did() -> str:
    async with AsyncClient() as client:
        response = await client.get(plugin_config.skland_sm_api_endpoint)
        response.raise_for_status()
        response = response.json()
        return response["dId"]
