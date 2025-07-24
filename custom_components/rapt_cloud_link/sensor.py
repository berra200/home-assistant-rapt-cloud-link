import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityDescription

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrewZilla sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = []
    for device in coordinator.data.values():
        device_id = device.get("id")
        name = device.get("name", f"BrewZilla {device_id}")
        sensors.append(BrewZillaTemperatureSensor(coordinator, device_id, name))

    if sensors:
        async_add_entities(sensors)
    else:
        _LOGGER.warning("No BrewZilla devices found")


class BrewZillaTemperatureSensor(CoordinatorEntity, SensorEntity):
    """BrewZilla Temperature Sensor."""

    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_temperature"
        self._attr_name = f"{device_name} Temperature"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

    @property
    def native_value(self):
        """Return the current temperature."""
        return self.coordinator.data.get(self._device_id, {}).get("temperature")







# import logging
# from homeassistant.core import HomeAssistant
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.helpers.update_coordinator import CoordinatorEntity
# from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

# from .const import DOMAIN

# _LOGGER = logging.getLogger(__name__)


# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
#     """Set up sensors from a config entry."""
#     coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

#     sensors = []
#     for device in coordinator.data.values():
#         device_id = device.get("id")
#         name = device.get("name", f"BrewZilla {device_id}")
#         sensors.append(BrewZillaTemperatureSensor(coordinator, device_id, name))

#     if sensors:
#         async_add_entities(sensors)
#     else:
#         _LOGGER.warning("No BrewZilla devices found")


# # ---------------------
# # Brewzilla
# # ---------------------

# class BrewZillaTemperatureSensor(CoordinatorEntity, SensorEntity):
#     """Temperature sensor for BrewZilla."""

#     def __init__(self, coordinator, device_id, name):
#         super().__init__(coordinator)
#         self._device_id = device_id
#         self._attr_name = "Temperature"
#         self._attr_unique_id = f"{device_id}_temperature"
#         self._attr_device_info = {
#             "identifiers": {(DOMAIN, device_id)},
#             "name": name,
#             "manufacturer": "RAPT",
#             "model": "BrewZilla",
#         }

#     @property
#     def native_value(self):
#         """Return the current temperature."""
#         device_data = self.coordinator.data.get(self._device_id)
#         if device_data:
#             return device_data.get("temperature")
#         return None

#     @property
#     def native_unit_of_measurement(self):
#         return "°C"

#     @property
#     def device_class(self):
#         return SensorDeviceClass.TEMPERATURE
