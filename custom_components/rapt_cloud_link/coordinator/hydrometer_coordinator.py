from .base_coordinator import BaseRaptCoordinator
from ..api.hydrometer_api import HydrometerAPI
from homeassistant.helpers.update_coordinator import UpdateFailed


class HydrometerDataUpdateCoordinator(BaseRaptCoordinator):
    def __init__(self, hass, token_manager, update_interval, entry):
        super().__init__(hass, token_manager, update_interval, entry, name="Hydrometer API")

    async def _async_update_data(self):
        try:
            api = await self._get_token_and_api(HydrometerAPI)
            devices = await api.get_hydrometers()
            return {device["id"]: device for device in devices if "id" in device}
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch Hydrometer data: {err}") from err
