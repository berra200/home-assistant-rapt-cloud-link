from .base_coordinator import BaseRaptCoordinator
from ..api.bonded_devices_api import BondedDevicesAPI
from homeassistant.helpers.update_coordinator import UpdateFailed


class BondedDevicesDataUpdateCoordinator(BaseRaptCoordinator):
    def __init__(self, hass, token_manager, update_interval, entry):
        super().__init__(
            hass, token_manager, update_interval, entry, name="Bonded Devices API"
        )

    async def _async_update_data(self):
        try:
            api = await self._get_token_and_api(BondedDevicesAPI)
            devices = await api.get_bonded_devices()
            return {device["id"]: device for device in devices if "id" in device}
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch Bonded Devices data: {err}") from err
