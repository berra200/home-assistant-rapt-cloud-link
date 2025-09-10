from datetime import timedelta
import logging

from .coordinator.brewzilla_coordinator import BrewZillaDataUpdateCoordinator
from .coordinator.hydrometer_coordinator import HydrometerDataUpdateCoordinator
from .coordinator.temperature_controller_coordinator import TemperatureControllerDataUpdateCoordinator

from .const import DOMAIN
from .api.token_manager import TokenManager

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "switch", "number"]

async def async_setup_entry(hass, entry):
    update_interval = timedelta(minutes=entry.options.get("poll_interval", 3))
    _LOGGER.info("Using polling interval: %s", update_interval)

    email = entry.data["email"]
    api_token = entry.data["api_token"]

    token_manager = TokenManager(hass, email, api_token, entry)

    # Coordinators
    brewzilla_coordinator = BrewZillaDataUpdateCoordinator(hass, token_manager, update_interval, entry)
    hydrometer_coordinator = HydrometerDataUpdateCoordinator(hass, token_manager, update_interval, entry)
    temperature_controller_coordinator = TemperatureControllerDataUpdateCoordinator(hass, token_manager, update_interval, entry)

    await brewzilla_coordinator.async_config_entry_first_refresh()
    await hydrometer_coordinator.async_config_entry_first_refresh()
    await temperature_controller_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "token_manager": token_manager,
        "brewzilla_coordinator": brewzilla_coordinator,
        "hydrometer_coordinator": hydrometer_coordinator,
        "temperature_controller_coordinator": temperature_controller_coordinator,
    }

    entry.async_on_unload(entry.add_update_listener(update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass, entry):
    """Unload the integration: remove platforms and clear data."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        return True
    return False


async def update_listener(hass, entry):
    """Handle options update: reload the integration to apply new polling interval."""
    await hass.config_entries.async_reload(entry.entry_id)
