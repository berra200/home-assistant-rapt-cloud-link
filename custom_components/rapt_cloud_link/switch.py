from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging
from .base import BaseRaptSwitch

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    brewzilla_coordinator = hass.data[DOMAIN][entry.entry_id]["brewzilla_coordinator"]

    switches = []

    for device_id, device in brewzilla_coordinator.data.items():
        name = device.get("name", f"BrewZilla {device_id}")
        switches.append(BrewZillaHeaterSwitch(brewzilla_coordinator, device_id))
        switches.append(BrewZillaPumpSwitch(brewzilla_coordinator, device_id))

    if switches:
        async_add_entities(switches, update_before_add=True)


class BrewZillaHeaterSwitch(BaseRaptSwitch):
    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="BrewZilla",
            name_suffix="Heater",
            unique_suffix="heater"
        )

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


class BrewZillaPumpSwitch(BaseRaptSwitch):
    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="BrewZilla",
            name_suffix="Pump",
            unique_suffix="pump"
        )

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