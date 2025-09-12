import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from .const import CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT, DOMAIN
from .base import BaseRaptSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    brewzilla_coordinator = hass.data[DOMAIN][entry.entry_id]["brewzilla_coordinator"]
    hydrometer_coordinator = hass.data[DOMAIN][entry.entry_id]["hydrometer_coordinator"]
    temperature_controller_coordinator = hass.data[DOMAIN][entry.entry_id]["temperature_controller_coordinator"]

    sensors = []

    # BrewZilla
    for device_id, device in brewzilla_coordinator.data.items():
        name = device.get("name", f"BrewZilla {device_id}")
        sensors.append(BrewZillaTemperatureSensor(brewzilla_coordinator, device_id))
        sensors.append(BrewZillaConnectionStateSensor(brewzilla_coordinator, device_id))

    # Hydrometer
    for device_id, device in hydrometer_coordinator.data.items():
        name = device.get("name", f"Pill {device_id}")
        sensors.append(HydrometerTemperatureSensor(hydrometer_coordinator, device_id))
        sensors.append(HydrometerGravitySensor(hydrometer_coordinator, device_id))
        sensors.append(HydrometerBatterySensor(hydrometer_coordinator, device_id))
        sensors.append(HydrometerConnectionStateSensor(hydrometer_coordinator, device_id))

    # Temperature Controller
    for device_id, device in temperature_controller_coordinator.data.items():
        name = device.get("name", f"Temperature Controller {device_id}")
        sensors.append(TemperatureControllerTemperatureSensor(temperature_controller_coordinator, device_id))


    # Add sensors if any
    if sensors:
        async_add_entities(sensors, update_before_add=True)


# ---------------------
# BrewZilla
# ---------------------
class BrewZillaTemperatureSensor(BaseRaptSensor):
    """BrewZilla Temperature Sensor."""
    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="BrewZilla",
            name_suffix="Temperature",
            unique_suffix="temperature",
            unit="°C"
        )
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

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
    
class BrewZillaConnectionStateSensor(BaseRaptSensor):
    """BrewZilla Connection State Sensor."""
    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="BrewZilla",
            name_suffix="Connection",
            unique_suffix="connection_state"
        )
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["Connected", "Disconnected"]

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
class HydrometerTemperatureSensor(BaseRaptSensor):
    """Hydrometer Temperature Sensor."""
    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="Hydrometer",
            name_suffix="Temperature",
            unique_suffix="temperature",
            unit="°C"
        )
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

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
    
class HydrometerGravitySensor(BaseRaptSensor):
    """Hydrometer Gravity Sensor."""
    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="Hydrometer",
            name_suffix="Gravity",
            unique_suffix="gravity",
            unit="SG"  # Specific Gravity
        )
        self._attr_device_class = None # No specific device class for gravity
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the current gravity."""
        device = self.coordinator.data.get(self._device_id)
        if device:
            sg = device.get("gravity")
            while sg > 10:
                sg /= 10
            return round(sg, 3)
        return None
    

class HydrometerBatterySensor(BaseRaptSensor):
    """Hydrometer Battery Sensor."""
    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="Hydrometer",
            name_suffix="Battery",
            unique_suffix="battery",
            unit="%"
        )
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the current battery."""
        device = self.coordinator.data.get(self._device_id)
        if device:
            return round(device.get("battery"), 1)
        return None
    
class HydrometerConnectionStateSensor(BaseRaptSensor):
    """Hydrometer Connection State Sensor."""
    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="Hydrometer",
            name_suffix="Connection",
            unique_suffix="connection_state"
        )
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["Connected", "Disconnected"]

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
class TemperatureControllerTemperatureSensor(BaseRaptSensor):
    """TemperatureController Temperature Sensor."""
    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="Temperature Controller",
            name_suffix="Temperature",
            unique_suffix="temperature",
            unit="°C"
        )
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

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