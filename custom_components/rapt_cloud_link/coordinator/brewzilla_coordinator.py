from .base_coordinator import BaseRaptCoordinator
from ..api.brewzilla_api import BrewZillaAPI
from homeassistant.helpers.update_coordinator import UpdateFailed


class BrewZillaDataUpdateCoordinator(BaseRaptCoordinator):
    def __init__(self, hass, token_manager, update_interval, entry):
        super().__init__(hass, token_manager, update_interval, entry, name="BrewZilla API")
        self._session_profiles = {}

    async def _async_update_data(self):
        try:
            api = await self._get_token_and_api(BrewZillaAPI)
            devices = await api.get_brewzillas()
            for device in devices:
                await self._attach_active_profile(api, device)
            return {device["id"]: device for device in devices if "id" in device}
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch BrewZilla data: {err}") from err

    async def _attach_active_profile(self, api, device):
        """Make sure an active profile session carries its profile and steps.

        GetBrewZillas embeds them in activeProfileSession; should it ever
        not, fetch the profile once per session instead.
        """
        session = device.get("activeProfileSession")
        profile_id = device.get("activeProfileId")
        if not session or not profile_id or (session.get("profile") or {}).get("steps"):
            return
        session_id = session.get("id")
        if session_id not in self._session_profiles:
            self._session_profiles[session_id] = await api.get_profile(profile_id)
        session["profile"] = self._session_profiles[session_id]
