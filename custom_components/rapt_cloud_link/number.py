from .const import CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT,DOMAIN
from .base import BaseRaptNumber


async def async_setup_entry(hass, entry, async_add_entities):
    brewzilla_coordinator = hass.data[DOMAIN][entry.entry_id]["brewzilla_coordinator"]
    temperature_controller_coordinator = hass.data[DOMAIN][entry.entry_id]["temperature_controller_coordinator"]

    numbers = []

    # BrewZilla
    for device_id in brewzilla_coordinator.data:
        numbers.append(BrewZillaHeatUtilization(brewzilla_coordinator, device_id))
        numbers.append(BrewZillaPumpUtilization(brewzilla_coordinator, device_id))
        numbers.append(BrewZillaTargetTemperature(brewzilla_coordinator, device_id))

    # TemperatureController
    for device_id in temperature_controller_coordinator.data:
        numbers.append(TemperatureControllerTargetTemperature(temperature_controller_coordinator, device_id))

    # Add sensors if any
    if numbers:
        async_add_entities(numbers, update_before_add=True)


# class BaseBrewZillaNumber(NumberEntity):
#     """Base class for BrewZilla number entities."""
#     def __init__(self, coordinator, device_id, name_suffix, unique_suffix, unit, min_val, max_val, step, mode=None):
#         self.coordinator = coordinator
#         self._device_id = device_id
#         device_name = coordinator.data.get(device_id, {}).get("name", f"BrewZilla {device_id}")
#         self._attr_name = f"{device_name} {name_suffix}"
#         self._attr_unique_id = f"{device_id}_{unique_suffix}"
#         self._attr_native_unit_of_measurement = unit
#         self._attr_native_min_value = min_val
#         self._attr_native_max_value = max_val
#         self._attr_native_step = step
#         if mode:
#             self._attr_mode = mode
#         self._unsub = None
#         self._attr_device_info = {
#             "identifiers": {(DOMAIN, str(device_id))},
#             "name": device_name,
#             "manufacturer": "RAPT",
#             "model": "BrewZilla",
#         }

#     async def async_added_to_hass(self):
#         self._unsub = self.coordinator.async_add_listener(self._handle_coordinator_update)

#     async def async_will_remove_from_hass(self):
#         if self._unsub:
#             self._unsub()

#     def _handle_coordinator_update(self):
#         self.async_write_ha_state()


class BrewZillaHeatUtilization(BaseRaptNumber):
    def __init__(self, coordinator, device_id):
        super().__init__(
            coordinator, device_id,
            model="BrewZilla",
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


class BrewZillaPumpUtilization(BaseRaptNumber):
    def __init__(self, coordinator, device_id):
        super().__init__(
            coordinator, device_id,
            model="BrewZilla",
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


class BrewZillaTargetTemperature(BaseRaptNumber):
    def __init__(self, coordinator, device_id):
        super().__init__(
            coordinator, device_id,
            model="BrewZilla",
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
        value = self.coordinator.data.get(self._device_id, {}).get("targetTemperature", 20.0)

        if(unit == "F"):
            value = (value * 9/5) + 32
            
        return round(value, 1)

    async def async_set_native_value(self, value: float):
        success = await self.coordinator.api.set_target_temperature(self._device_id, float(value))
        if success and self._device_id in self.coordinator.data:
            self.coordinator.data[self._device_id]["targetTemperature"] = float(value)
            self.async_write_ha_state()


# ---------------------
# Temperature Controller
# ---------------------
# class BaseTemperatureControllerNumber(NumberEntity):
#     """Base class for Temperature Controller number entities."""
#     def __init__(self, coordinator, device_id, name_suffix, unique_suffix, unit, min_val, max_val, step, mode=None):
#         self.coordinator = coordinator
#         self._device_id = device_id
#         device_name = coordinator.data.get(device_id, {}).get("name", f"Temperature Controller {device_id}")
#         self._attr_name = f"{device_name} {name_suffix}"
#         self._attr_unique_id = f"{device_id}_{unique_suffix}"
#         self._attr_native_unit_of_measurement = unit
#         self._attr_native_min_value = min_val
#         self._attr_native_max_value = max_val
#         self._attr_native_step = step
#         if mode:
#             self._attr_mode = mode
#         self._unsub = None
#         self._attr_device_info = {
#             "identifiers": {(DOMAIN, str(device_id))},
#             "name": device_name,
#             "manufacturer": "RAPT",
#             "model": "Temperature Controller",
#         }

#     async def async_added_to_hass(self):
#         self._unsub = self.coordinator.async_add_listener(self._handle_coordinator_update)

#     async def async_will_remove_from_hass(self):
#         if self._unsub:
#             self._unsub()

#     def _handle_coordinator_update(self):
#         self.async_write_ha_state()


class TemperatureControllerTargetTemperature(BaseRaptNumber):
    def __init__(self, coordinator, device_id):
        super().__init__(
            coordinator, device_id,
            model="Temperature Controller",
            name_suffix="Target Temperature",
            unique_suffix="target_temperature",
            unit="°C",
            min_val=-20.0,
            max_val=120.0,
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
        value = self.coordinator.data.get(self._device_id, {}).get("targetTemperature", 20.0)

        if(unit == "F"):
            value = (value * 9/5) + 32

        return round(value, 1)

    async def async_set_native_value(self, value: float):
        success = await self.coordinator.api.set_target_temperature(self._device_id, float(value))
        if success and self._device_id in self.coordinator.data:
            self.coordinator.data[self._device_id]["targetTemperature"] = float(value)
            self.async_write_ha_state()