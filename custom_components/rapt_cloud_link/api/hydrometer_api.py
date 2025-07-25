import logging
from aiohttp import ClientSession
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class HydrometerAPI:
    def __init__(self, hass, token, entry):
        self.hass = hass
        self.token = token
        self.entry = entry

    def _build_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _get_url(self, path: str) -> str:
        return f"{API_BASE_URL}{path}"

    async def get_hydrometers(self):
        session = async_get_clientsession(self.hass)
        url = self._get_url("/Hydrometers/GetHydrometers")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        async with session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()