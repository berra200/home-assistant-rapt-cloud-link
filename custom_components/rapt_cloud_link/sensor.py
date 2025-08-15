import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from .const import CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up BrewZilla sensors from a config entry."""
    brewzilla_coordinator = hass.data[DOMAIN][entry.entry_id]["brewzilla_coordinator"]
    hydrometer_coordinator = hass.data[DOMAIN][entry.entry_id]["hydrometer_coordinator"]

    sensors = []

    # BrewZilla
    for device_id, device in brewzilla_coordinator.data.items():
        name = device.get("name", f"BrewZilla {device_id}")
        sensors.append(BrewZillaTemperatureSensor(brewzilla_coordinator, device_id, name))
        sensors.append(BrewZillaConnectionStateSensor(brewzilla_coordinator, device_id, name))

    if not brewzilla_coordinator.data:
        _LOGGER.info("No BrewZilla devices found")

    # Hydrometer
    for device_id, device in hydrometer_coordinator.data.items():
        name = device.get("name", f"Pill {device_id}")
        sensors.append(HydrometerTemperatureSensor(hydrometer_coordinator, device_id, name))
        sensors.append(HydrometerGravitySensor(hydrometer_coordinator, device_id, name))
        sensors.append(HydrometerBatterySensor(hydrometer_coordinator, device_id, name))
        sensors.append(HydrometerConnectionStateSensor(hydrometer_coordinator, device_id, name))

    if not hydrometer_coordinator.data:
        _LOGGER.info("No Hydrometer devices found")

    # Lägg till alla en gång
    if sensors:
        async_add_entities(sensors)


# ---------------------
# BrewZilla
# ---------------------
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
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

    @property
    def unit_of_measurement(self):
        unit = self.coordinator.config_entry.data.get(CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT)
        return "°F" if unit == "F" else "°C"
    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_id)
        if device:
            return device.get("temperature")
        return None
    
class BrewZillaConnectionStateSensor(CoordinatorEntity, SensorEntity):
    """BrewZilla Connection State Sensor."""

    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_connection_state"
        self._attr_name = f"{device_name} Connection"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["Connected", "Disconnected"]
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

    @property
    def native_value(self):
        """Return the current connection state."""
        device = self.coordinator.data.get(self._device_id)
        if device:
            return device.get("connectionState", "Disconnected")
        return "Disconnected"
    

# ---------------------
# Hydrometer
# ---------------------
class HydrometerTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Hydrometer Temperature Sensor."""

    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_temperature"
        self._attr_name = f"{device_name} Temperature"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "Pill",
        }
    @property
    def unit_of_measurement(self):
        unit = self.coordinator.config_entry.data.get(CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT)
        return "°F" if unit == "F" else "°C"
    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_id)
        if device:
            return device.get("temperature")
        return None
    
class HydrometerGravitySensor(CoordinatorEntity, SensorEntity):
    """Hydrometer Gravity Sensor."""

    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_gravity"
        self._attr_name = f"{device_name} Gravity"
        self._attr_native_unit_of_measurement = "SG"  # Specific Gravity
        self._attr_device_class = None  # Ingen standardklass för gravity
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "Pill",
        }

    @property
    def native_value(self):
        """Return the current gravity."""
        device = self.coordinator.data.get(self._device_id)
        if device:
            return device.get("gravity")
        return None
    
class HydrometerBatterySensor(CoordinatorEntity, SensorEntity):
    """Hydrometer Battery Sensor."""

    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_battery"
        self._attr_name = f"{device_name} Battery"
        self._attr_native_unit_of_measurement = "V"
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "Pill",
        }

    @property
    def native_value(self):
        """Return the current battery."""
        device = self.coordinator.data.get(self._device_id)
        if device:
            return device.get("battery")
        return None
    
class HydrometerConnectionStateSensor(CoordinatorEntity, SensorEntity):
    """Hydrometer Connection State Sensor."""

    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_connection_state"
        self._attr_name = f"{device_name} Connection"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["Connected", "Disconnected"]
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "Pill",
        }

    @property
    def native_value(self):
        """Return the current connection state."""
        device = self.coordinator.data.get(self._device_id)
        if device:
            return device.get("connectionState", "Disconnected")
        return "Disconnected"


# ---------------------
# Temperature Controller
# ---------------------
class TemperatureControllerTemperatureSensor(CoordinatorEntity, SensorEntity):
    """TemperatureController Temperature Sensor."""

    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_temperature_controller"
        self._attr_name = f"{device_name} Temperature"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "Temperature Controller",
        }
    @property
    def unit_of_measurement(self):
        unit = self.coordinator.config_entry.data.get(CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT)
        return "°F" if unit == "F" else "°C"
    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_id)
        if device:
            return device.get("temperature")
        return None