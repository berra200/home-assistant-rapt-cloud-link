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
        self._session_profiles = {}

    async def _get_token_and_api(self, api_class):
        """Handles token refresh and (re)instantiates the API class."""
        token = await self.token_manager.get_token()

        if not self.api or self.api.token != token:
            self.api = api_class(self.hass, token, self.entry)

        return self.api

    async def _attach_active_profile(self, api, device):
        """Make sure an active profile session carries its profile and steps.

        Device lists embed them in activeProfileSession; should one not, fetch
        the profile once per session instead. A failed fetch only leaves the
        profile unknown, the device's other entities keep updating.
        """
        session = device.get("activeProfileSession")
        profile_id = device.get("activeProfileId")
        if not session or not profile_id or (session.get("profile") or {}).get("steps"):
            return
        session_id = session.get("id")
        if session_id not in self._session_profiles:
            try:
                self._session_profiles[session_id] = await api.get_profile(profile_id)
            except Exception as err:
                _LOGGER.debug("Failed to fetch profile %s: %s", profile_id, err)
                return
        session["profile"] = self._session_profiles[session_id]
