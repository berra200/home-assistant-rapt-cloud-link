import logging

from .base_coordinator import BaseRaptCoordinator
from ..api.brewzilla_api import BrewZillaAPI
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


class BrewZillaDataUpdateCoordinator(BaseRaptCoordinator):
    def __init__(self, hass, token_manager, update_interval, entry):
        super().__init__(hass, token_manager, update_interval, entry, name="BrewZilla API")
        self._session_profiles = {}
        self._step_starts = {}

    async def _async_update_data(self):
        try:
            api = await self._get_token_and_api(BrewZillaAPI)
            devices = await api.get_brewzillas()
            for device in devices:
                await self._attach_active_profile(api, device)
                await self._attach_step_start(api, device)
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

    async def _attach_step_start(self, api, device):
        """Record when the active profile step started, as activeProfileStepStart.

        The API does not say, so it is read from telemetry once per step.
        """
        session = device.get("activeProfileSession")
        step_id = device.get("activeProfileStepId")
        if not session or not step_id:
            self._step_starts.pop(device.get("id"), None)
            return
        cached_step_id, start = self._step_starts.get(device.get("id"), (None, None))
        if cached_step_id != step_id:
            # The new step started after the previous one, so its telemetry is enough
            since = start or session.get("startDate")
            start = await self._find_step_start(api, device, session, step_id, since)
            if start:
                self._step_starts[device.get("id")] = (step_id, start)
        device["activeProfileStepStart"] = start

    async def _find_step_start(self, api, device, session, step_id, since):
        """Return when the latest unbroken run of step_id began in the telemetry.

        Telemetry rows carry the step id. Only the latest run counts, since a
        session can run its profile more than once. None until a row for the
        step shows up, which a later update then retries.
        """
        try:
            rows = await api.get_telemetry(device.get("id"), since, dt_util.utcnow().isoformat(), session.get("id"))
        except Exception as err:
            _LOGGER.debug("Failed to fetch BrewZilla telemetry: %s", err)
            return None
        rows = sorted((row for row in rows if row.get("createdOn")), key=lambda row: dt_util.parse_datetime(row["createdOn"]))
        start = None
        for row in reversed(rows):
            if row.get("profileStepId") != step_id:
                break
            start = row["createdOn"]
        return start
