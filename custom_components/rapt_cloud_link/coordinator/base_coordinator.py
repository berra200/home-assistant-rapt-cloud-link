import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)


class BaseRaptCoordinator(DataUpdateCoordinator):
    """Base class for all RAPT coordinators."""

    def __init__(self, hass, token_manager, update_interval: timedelta, entry, name: str):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )
        self.hass = hass
        self.token_manager = token_manager
        self.entry = entry
        self.api = None  # to be instantiated by subclass

    async def _get_token_and_api(self, api_class):
        """Handles token refresh and (re)instantiates the API class."""
        token = await self.token_manager.get_token()

        if not self.api or self.api.token != token:
            self.api = api_class(self.hass, token, self.entry)

        return self.api
