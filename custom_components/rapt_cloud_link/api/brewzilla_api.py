import logging
from aiohttp import ClientSession
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class BrewZillaAPI:
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

    async def get_brewzillas(self):
        session = async_get_clientsession(self.hass)
        url = self._get_url("/BrewZillas/GetBrewZillas")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        async with session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def set_heating_enabled(self, device_id, enabled):
        session = async_get_clientsession(self.hass)
        url = self._get_url(f"/BrewZillas/SetHeatingEnabled?brewZillaId={device_id}&state={str(enabled).lower()}")
        async with session.post(url, headers=self._build_headers()) as resp:
            return resp.status == 200

    async def set_pump_enabled(self, device_id, enabled):
        session = async_get_clientsession(self.hass)
        url = self._get_url(f"/BrewZillas/SetPumpEnabled?brewZillaId={device_id}&state={str(enabled).lower()}")
        async with session.post(url, headers=self._build_headers()) as resp:
            return resp.status == 200

    async def set_heating_utilization(self, device_id, percent):
        session = async_get_clientsession(self.hass)
        url = self._get_url(f"/BrewZillas/SetHeatingUtilisation?brewZillaId={device_id}&utilisation={percent}")
        async with session.post(url, headers=self._build_headers()) as resp:
            return resp.status == 200

    async def set_pump_utilization(self, device_id, percent):
        session = async_get_clientsession(self.hass)
        url = self._get_url(f"/BrewZillas/SetPumpUtilisation?brewZillaId={device_id}&utilisation={percent}")
        async with session.post(url, headers=self._build_headers()) as resp:
            return resp.status == 200

    async def set_target_temperature(self, device_id, temperature):
        session = async_get_clientsession(self.hass)
        url = self._get_url(f"/BrewZillas/SetTargetTemperature?brewZillaId={device_id}&target={temperature}")
        async with session.post(url, headers=self._build_headers()) as resp:
            return resp.status == 200