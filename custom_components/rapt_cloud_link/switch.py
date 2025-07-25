from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up BrewZilla switches from a config entry."""
    brewzilla_coordinator = hass.data[DOMAIN][entry.entry_id]["brewzilla_coordinator"]
    switches = []

    for device_id, device in brewzilla_coordinator.data.items():
        name = device.get("name", f"BrewZilla {device_id}")
        switches.append(BrewZillaHeaterSwitch(brewzilla_coordinator, device_id, name))
        switches.append(BrewZillaPumpSwitch(brewzilla_coordinator, device_id, name))

    if switches:
        async_add_entities(switches, update_before_add=True)
    else:
        _LOGGER.warning("No BrewZilla devices found")


class BrewZillaHeaterSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{device_name} Heater"
        self._attr_unique_id = f"{device_id}_heater"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

    @property
    def is_on(self):
        device = self.coordinator.data.get(self._device_id)
        if device:
            return device.get("heatingEnabled", False)
        return False

    async def async_turn_on(self, **kwargs):
        success = await self.coordinator.api.set_heating_enabled(self._device_id, True)
        if success:
            device = self.coordinator.data.get(self._device_id)
            if device:
                device["heatingEnabled"] = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        success = await self.coordinator.api.set_heating_enabled(self._device_id, False)
        if success:
            device = self.coordinator.data.get(self._device_id)
            if device:
                device["heatingEnabled"] = False
            self.async_write_ha_state()


class BrewZillaPumpSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{device_name} Pump"
        self._attr_unique_id = f"{device_id}_pump"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

    @property
    def is_on(self):
        device = self.coordinator.data.get(self._device_id)
        if device:
            return device.get("pumpEnabled", False)
        return False

    async def async_turn_on(self, **kwargs):
        success = await self.coordinator.api.set_pump_enabled(self._device_id, True)
        if success:
            device = self.coordinator.data.get(self._device_id)
            if device:
                device["pumpEnabled"] = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        success = await self.coordinator.api.set_pump_enabled(self._device_id, False)
        if success:
            device = self.coordinator.data.get(self._device_id)
            if device:
                device["pumpEnabled"] = False
            self.async_write_ha_state()