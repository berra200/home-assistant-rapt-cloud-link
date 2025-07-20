from homeassistant.components.number import NumberEntity
import logging

from .api.brewzilla_api import set_heating_utilization, set_pump_utilization, set_target_temperature

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["rapt_cloud"][entry.entry_id]["coordinator"]
    numbers = []

    for device_id in coordinator.data:
        numbers.append(BrewZillaHeatUtilization(coordinator, device_id))
        numbers.append(BrewZillaPumpUtilization(coordinator, device_id))
        numbers.append(BrewZillaTargetTemperature(coordinator, device_id))

    async_add_entities(numbers, update_before_add=True)


class BrewZillaHeatUtilization(NumberEntity):
    def __init__(self, coordinator, device_id):
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = "Heat Utilization"
        self._attr_unique_id = f"{device_id}_heat_utilization"
        self._attr_device_info = {
            "identifiers": {("rapt_cloud", device_id)},
            "name": f"BrewZilla {device_id}",
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 5

    def _get_current_value(self):
        device_data = self.coordinator.data.get(self._device_id, {})
        return device_data.get("heatUtilisation", 0)

    @property
    def native_value(self):
        return self._get_current_value()

    async def async_set_native_value(self, value: float):
        token = await self.coordinator.token_manager.get_token()
        success = await set_heating_utilization(
            self.coordinator.hass, token, self._device_id, int(value)
        )
        if success:
            self.coordinator.data[self._device_id]["heatUtilisation"] = int(value)
            self.async_write_ha_state()

    async def async_added_to_hass(self):
        self._unsub = self.coordinator.async_add_listener(self._handle_coordinator_update)

    def _handle_coordinator_update(self):
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self):
        self._unsub()



class BrewZillaPumpUtilization(NumberEntity):
    def __init__(self, coordinator, device_id):
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = "Pump Utilization"
        self._attr_unique_id = f"{device_id}_pump_utilization"
        self._attr_device_info = {
            "identifiers": {("rapt_cloud", device_id)},
            "name": f"BrewZilla {device_id}",
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 5

    def _get_current_value(self):
        device_data = self.coordinator.data.get(self._device_id, {})
        return device_data.get("pumpUtilisation", 0)

    @property
    def native_value(self):
        return self._get_current_value()

    async def async_set_native_value(self, value: float):
        token = await self.coordinator.token_manager.get_token()
        success = await set_pump_utilization(
            self.coordinator.hass, token, self._device_id, int(value)
        )
        if success:
            self.coordinator.data[self._device_id]["pumpUtilisation"] = int(value)
            self.async_write_ha_state()

    async def async_added_to_hass(self):
        self._unsub = self.coordinator.async_add_listener(self._handle_coordinator_update)

    def _handle_coordinator_update(self):
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self):
        self._unsub()


class BrewZillaTargetTemperature(NumberEntity):
    def __init__(self, coordinator, device_id):
        self.coordinator = coordinator
        self._device_id = device_id
        self._attr_name = "Target Temperature"
        self._attr_unique_id = f"{device_id}_target_temperature"
        self._attr_device_info = {
            "identifiers": {("rapt_cloud", device_id)},
            "name": f"BrewZilla {device_id}",
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }
        self._attr_native_unit_of_measurement = "°C"
        self._attr_native_min_value = 0.0
        self._attr_native_max_value = 105.0
        self._attr_native_step = 0.1
        self._attr_mode = "box"

    def _get_current_value(self):
        device_data = self.coordinator.data.get(self._device_id, {})
        return device_data.get("targetTemperature", 20.0)

    @property
    def native_value(self):
        return self._get_current_value()

    async def async_set_native_value(self, value: float):
        token = await self.coordinator.token_manager.get_token()
        success = await set_target_temperature(
            self.coordinator.hass, token, self._device_id, float(value)
        )
        if success:
            self.coordinator.data[self._device_id]["targetTemperature"] = float(value)
            self.async_write_ha_state()

    async def async_added_to_hass(self):
        self._unsub = self.coordinator.async_add_listener(self._handle_coordinator_update)

    def _handle_coordinator_update(self):
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self):
        self._unsub()
