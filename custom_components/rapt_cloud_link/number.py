from custom_components.rapt_cloud_link.const import CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT
from homeassistant.components.number import NumberEntity
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up number entities from a config entry."""
    brewzilla_coordinator = hass.data["rapt_cloud_link"][entry.entry_id]["brewzilla_coordinator"]
    numbers = []

    for device_id in brewzilla_coordinator.data:
        numbers.append(BrewZillaHeatUtilization(brewzilla_coordinator, device_id))
        numbers.append(BrewZillaPumpUtilization(brewzilla_coordinator, device_id))
        numbers.append(BrewZillaTargetTemperature(brewzilla_coordinator, device_id))

    async_add_entities(numbers, update_before_add=True)


class BaseBrewZillaNumber(NumberEntity):
    """Base class for BrewZilla number entities."""

    def __init__(self, coordinator, device_id, name_suffix, unique_suffix, unit, min_val, max_val, step, mode=None):
        self.coordinator = coordinator
        self._device_id = device_id
        device_name = coordinator.data.get(device_id, {}).get("name", f"BrewZilla {device_id}")
        self._attr_name = f"{device_name} {name_suffix}"
        self._attr_unique_id = f"{device_id}_{unique_suffix}"
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        if mode:
            self._attr_mode = mode
        self._unsub = None
        self._attr_device_info = {
            "identifiers": {("rapt_cloud_link", str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

    async def async_added_to_hass(self):
        self._unsub = self.coordinator.async_add_listener(self._handle_coordinator_update)

    async def async_will_remove_from_hass(self):
        if self._unsub:
            self._unsub()

    def _handle_coordinator_update(self):
        self.async_write_ha_state()


class BrewZillaHeatUtilization(BaseBrewZillaNumber):
    def __init__(self, coordinator, device_id):
        super().__init__(
            coordinator, device_id,
            name_suffix="Heat Utilization",
            unique_suffix="heat_utilization",
            unit="%",
            min_val=0,
            max_val=100,
            step=5
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self._device_id, {}).get("heatingUtilisation", 0)

    async def async_set_native_value(self, value: float):
        success = await self.coordinator.api.set_heating_utilization(self._device_id, int(value))
        if success and self._device_id in self.coordinator.data:
            self.coordinator.data[self._device_id]["heatingUtilisation"] = int(value)
            self.async_write_ha_state()


class BrewZillaPumpUtilization(BaseBrewZillaNumber):
    def __init__(self, coordinator, device_id):
        super().__init__(
            coordinator, device_id,
            name_suffix="Pump Utilization",
            unique_suffix="pump_utilization",
            unit="%",
            min_val=0,
            max_val=100,
            step=5
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self._device_id, {}).get("pumpUtilisation", 0)

    async def async_set_native_value(self, value: float):
        success = await self.coordinator.api.set_pump_utilization(self._device_id, int(value))
        if success and self._device_id in self.coordinator.data:
            self.coordinator.data[self._device_id]["pumpUtilisation"] = int(value)
            self.async_write_ha_state()


class BrewZillaTargetTemperature(BaseBrewZillaNumber):
    def __init__(self, coordinator, device_id):
        super().__init__(
            coordinator, device_id,
            name_suffix="Target Temperature",
            unique_suffix="target_temperature",
            unit="°C",
            min_val=0.0,
            max_val=110.0,
            step=0.1,
            mode="box"
        )

    @property
    def native_unit_of_measurement(self):
        unit = self.coordinator.config_entry.data.get(CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT)
        return "°F" if unit == "F" else "°C"
    @property
    def native_value(self):
        unit = self.coordinator.config_entry.data.get(CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT)
        if(unit == "F"):
            return (self.coordinator.data.get(self._device_id, {}).get("targetTemperature", 20.0) * 9/5) + 32
        return self.coordinator.data.get(self._device_id, {}).get("targetTemperature", 20.0)

    async def async_set_native_value(self, value: float):
        success = await self.coordinator.api.set_target_temperature(self._device_id, float(value))
        if success and self._device_id in self.coordinator.data:
            self.coordinator.data[self._device_id]["targetTemperature"] = float(value)
            self.async_write_ha_state()