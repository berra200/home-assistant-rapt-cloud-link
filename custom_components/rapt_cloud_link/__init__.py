from datetime import timedelta
import logging

from .coordinator import BrewZillaDataUpdateCoordinator
from .const import DOMAIN
from .api.token_manager import TokenManager
from .api.brewzilla_api import BrewZillaAPI

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "switch", "number"]

async def async_setup_entry(hass, entry):
    update_interval = timedelta(minutes=entry.options.get("poll_interval", 3))
    _LOGGER.info("Using polling interval: %s", update_interval)

    email = entry.data["email"]
    api_token = entry.data["api_token"]

    token_manager = TokenManager(hass, email, api_token, entry)
    coordinator = BrewZillaDataUpdateCoordinator(hass, token_manager, update_interval, entry)
    await coordinator.async_config_entry_first_refresh()
    
    # Create a brewzilla coordinator
    # coordinator = BrewZillaDataUpdateCoordinator(
    #     hass,
    #     token_manager,
    #     update_interval,
    #     entry=entry
    # )
    # await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "token_manager": token_manager,
        "coordinator": coordinator,
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