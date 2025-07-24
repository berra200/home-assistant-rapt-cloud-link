from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
from .api.brewzilla_api import BrewZillaAPI
import logging

_LOGGER = logging.getLogger(__name__)

class BrewZillaDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, token_manager, update_interval, entry):
        super().__init__(
            hass,
            _LOGGER,
            name="BrewZilla API",
            update_interval=update_interval,
        )
        self.hass = hass
        self.token_manager = token_manager
        self.entry = entry
        self.api = None

    async def _async_update_data(self):
        """Fetch data from the BrewZilla API."""
        try:
            token = await self.token_manager.get_token()
            if not self.api or self.api.token != token:
                self.api = BrewZillaAPI(self.hass, token, self.entry)

            devices = await self.api.get_brewzillas()

            # 🔁 Konvertera lista till dict baserat på 'id'
            data_by_id = {
                device["id"]: device
                for device in devices
                if isinstance(device, dict) and "id" in device
            }

            return data_by_id

        except Exception as err:
            raise UpdateFailed(f"Failed to fetch BrewZilla data: {err}") from err


        





# class BrewZillaDataUpdateCoordinator(DataUpdateCoordinator):
#     def __init__(self, hass, token_manager, update_interval: timedelta, entry):
#         super().__init__(
#             hass,
#             _LOGGER,
#             name="BrewZillaDataCoordinator",
#             update_interval=update_interval,
#             always_update=False
#         )
#         self.token_manager = token_manager
#         self.entry = entry

#     async def _async_update_data(self):
#         _LOGGER.debug("Polling BrewZilla data...")

#         token = await self.token_manager.get_token()

#         try:
#             brewzillas = await get_brewzillas(self.hass, token, entry=self.entry)
#             self.data = {bz["id"]: bz for bz in brewzillas}
#             return self.data

#         except Exception as err:
#             raise UpdateFailed(f"Could not update BrewZilla data: {err}")