from homeassistant.components.switch import SwitchEntity
import logging

from .api.token_manager import TokenManager
from .api.brewzilla_api import get_brewzillas, set_heating_enabled, set_pump_enabled


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up switches from a config entry."""
    coordinator = hass.data["rapt_cloud_link"][entry.entry_id]["coordinator"]

    switches = []
    for device_id in coordinator.data:
        switches.append(BrewZillaHeaterSwitch(coordinator, device_id))
        switches.append(BrewZillaPumpSwitch(coordinator, device_id))

    async_add_entities(switches, update_before_add=True)


# ---------------------
# Brewzilla
# ---------------------

class BrewZillaHeaterSwitch(SwitchEntity):
    def __init__(self, coordinator, device_id):
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = "Heater"
        self._attr_unique_id = f"{self._device_id}_heater"
        self._attr_device_info = {
            "identifiers": {("rapt_cloud_link", self._device_id)},
            "name": f"BrewZilla {self._device_id}",
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

    @property
    def is_on(self):
        device_data = self.coordinator.data.get(self._device_id, {})
        return device_data.get("heatingEnabled", False)

    async def async_turn_on(self, **kwargs):
        token = await self.coordinator.token_manager.get_token()
        success = await set_heating_enabled(self.coordinator.hass, token, self._device_id, True)
        if success:
            if self._device_id in self.coordinator.data:
                self.coordinator.data[self._device_id]["heatingEnabled"] = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        token = await self.coordinator.token_manager.get_token()
        success = await set_heating_enabled(self.coordinator.hass, token, self._device_id, False)
        if success:
            if self._device_id in self.coordinator.data:
                self.coordinator.data[self._device_id]["heatingEnabled"] = False
            self.async_write_ha_state()

    async def async_added_to_hass(self):
        self._unsub = self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._unsub()


class BrewZillaPumpSwitch(SwitchEntity):
    def __init__(self, coordinator, device_id):
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = "Pump"
        self._attr_unique_id = f"{self._device_id}_pump"
        self._attr_device_info = {
            "identifiers": {("rapt_cloud_link", self._device_id)},
            "name": f"BrewZilla {self._device_id}",
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

    @property
    def is_on(self):
        device_data = self.coordinator.data.get(self._device_id, {})
        return device_data.get("pumpEnabled", False)

    async def async_turn_on(self, **kwargs):
        token = await self.coordinator.token_manager.get_token()
        success = await set_pump_enabled(self.coordinator.hass, token, self._device_id, True)
        if success:
            if self._device_id in self.coordinator.data:
                self.coordinator.data[self._device_id]["pumpEnabled"] = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        token = await self.coordinator.token_manager.get_token()
        success = await set_pump_enabled(self.coordinator.hass, token, self._device_id, False)
        if success:
            if self._device_id in self.coordinator.data:
                self.coordinator.data[self._device_id]["pumpEnabled"] = False
            self.async_write_ha_state()

    async def async_added_to_hass(self):
        self._unsub = self.coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._unsub()