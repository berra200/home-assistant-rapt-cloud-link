from .base_coordinator import BaseRaptCoordinator
from ..api.temperatureController_api import TemperatureControllerAPI
from homeassistant.helpers.update_coordinator import UpdateFailed


class TemperatureControllerDataUpdateCoordinator(BaseRaptCoordinator):
    def __init__(self, hass, token_manager, update_interval, entry):
        super().__init__(hass, token_manager, update_interval, entry, name="Temperature Controller API")

    async def _async_update_data(self):
        try:
            api = await self._get_token_and_api(TemperatureControllerAPI)
            devices = await api.get_temperatureControllers()
            return {device["id"]: device for device in devices if "id" in device}
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch Temperatur Controller data: {err}") from err
