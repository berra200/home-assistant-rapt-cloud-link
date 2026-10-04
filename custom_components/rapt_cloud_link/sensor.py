import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from .const import BONDED_DEVICE_TYPES, CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT, DOMAIN
from .base import BaseRaptSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    brewzilla_coordinator = hass.data[DOMAIN][entry.entry_id]["brewzilla_coordinator"]
    hydrometer_coordinator = hass.data[DOMAIN][entry.entry_id]["hydrometer_coordinator"]
    temperature_controller_coordinator = hass.data[DOMAIN][entry.entry_id]["temperature_controller_coordinator"]
    bonded_devices_coordinator = hass.data[DOMAIN][entry.entry_id]["bonded_devices_coordinator"]

    sensors = []

    # Bonded Devices
    for device_id, device in bonded_devices_coordinator.data.items():
        if device.get("deviceType") in BONDED_DEVICE_TYPES:
            device_type = device.get("deviceType")
            if "Temp" in device_type:
                sensors.append(BondedDeviceTemperatureSensor(bonded_devices_coordinator, device_id))
            if "Humidity" in device_type:
                sensors.append(BondedDeviceHumiditySensor(bonded_devices_coordinator, device_id))
            if "Pressure" in device_type:
                sensors.append(BondedDevicePressureSensor(bonded_devices_coordinator, device_id))
            sensors.append(BondedDeviceBatterySensor(bonded_devices_coordinator, device_id))

    # BrewZilla
    for device_id, device in brewzilla_coordinator.data.items():
        # name = device.get("name", f"BrewZilla {device_id}")
        sensors.append(BrewZillaTemperatureSensor(brewzilla_coordinator, device_id))
        sensors.append(BrewZillaConnectionStateSensor(brewzilla_coordinator, device_id))
        sensors.append(BrewZillaProfileSensor(brewzilla_coordinator, device_id))
        sensors.append(BrewZillaProfileStepSensor(brewzilla_coordinator, device_id))

    # Hydrometer
    for device_id, device in hydrometer_coordinator.data.items():
        # name = device.get("name", f"Pill {device_id}")
        sensors.append(HydrometerTemperatureSensor(hydrometer_coordinator, device_id))
        sensors.append(HydrometerGravitySensor(hydrometer_coordinator, device_id))
        sensors.append(HydrometerBatterySensor(hydrometer_coordinator, device_id))
        sensors.append(HydrometerConnectionStateSensor(hydrometer_coordinator, device_id))

    # Temperature Controller
    for device_id, device in temperature_controller_coordinator.data.items():
        # name = device.get("name", f"Temperature Controller {device_id}")
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
            unit="°C",
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
            unique_suffix="connection_state",
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


def _active_profile_steps(device):
    """Return the active profile's steps in order, and the index of the active one."""
    session = device.get("activeProfileSession") or {}
    profile = session.get("profile") or {}
    steps = sorted(profile.get("steps") or [], key=lambda step: step.get("order", 0))
    step_id = device.get("activeProfileStepId")
    index = next((i for i, step in enumerate(steps) if step.get("id") == step_id), None)
    return steps, index


class BrewZillaProfileSensor(BaseRaptSensor):
    """BrewZilla Profile Sensor: the profile its session is running, if any."""

    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="BrewZilla",
            name_suffix="Profile",
            unique_suffix="profile",
        )
        self._attr_icon = "mdi:clipboard-list-outline"

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_id)
        if device:
            session = device.get("activeProfileSession") or {}
            return (session.get("profile") or {}).get("name")
        return None

    @property
    def extra_state_attributes(self):
        device = self.coordinator.data.get(self._device_id) or {}
        session = device.get("activeProfileSession")
        if not session:
            return {}
        steps, _ = _active_profile_steps(device)
        return {
            "profile_id": device.get("activeProfileId"),
            "session_id": session.get("id"),
            "session_start": session.get("startDate"),
            "profile_length": session.get("profileLength"),
            "step_count": len(steps),
        }


class BrewZillaProfileStepSensor(BaseRaptSensor):
    """BrewZilla Profile Step Sensor: the step its profile session is at, if any."""

    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="BrewZilla",
            name_suffix="Profile Step",
            unique_suffix="profile_step",
        )
        self._attr_icon = "mdi:format-list-numbered"

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_id)
        if device:
            steps, index = _active_profile_steps(device)
            if index is not None:
                # A state is capped at 255 characters
                return (steps[index].get("name") or f"Step {index + 1}")[:255]
        return None

    @property
    def extra_state_attributes(self):
        steps, index = _active_profile_steps(self.coordinator.data.get(self._device_id) or {})
        if index is None:
            return {}
        step = steps[index]
        return {
            "step_id": step.get("id"),
            "step_number": index + 1,
            "step_count": len(steps),
            "control_type": step.get("controlType"),
            "end_type": step.get("endType"),
            "duration": step.get("length") if step.get("endType") == "Duration" else None,
            "target_temperature": step.get("temperature"),
            "next_step": steps[index + 1].get("name") if index + 1 < len(steps) else None,
        }


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
            unit="°C",
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
            unit="SG",  # Specific Gravity
        )
        self._attr_device_class = None  # No specific device class for gravity
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
            unit="%",
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
            unique_suffix="connection_state",
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
            unit="°C",
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
            return round(device.get("temperature"), 1)
        return None


# ---------------------
# Bonded Devices
# ---------------------
class BondedDeviceTemperatureSensor(BaseRaptSensor):
    """Bonded Device Temperature Sensor."""

    def __init__(self, coordinator, device_id: str):
        device = coordinator.data.get(device_id, {})
        model = f"{device.get('deviceType', 'Bonded Device')} (Bonded Device)"
        super().__init__(
            coordinator,
            device_id,
            model=model,
            name_suffix="Temperature",
            unique_suffix="temperature",
            unit="°C",
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
            return round(device.get("temperature"), 1)
        return None


class BondedDeviceHumiditySensor(BaseRaptSensor):
    """Bonded Device Humidity Sensor."""

    def __init__(self, coordinator, device_id: str):
        device = coordinator.data.get(device_id, {})
        model = f"{device.get('deviceType', 'Bonded Device')} (Bonded Device)"
        super().__init__(
            coordinator,
            device_id,
            model=model,
            name_suffix="Humidity",
            unique_suffix="humidity",
            unit="%",
        )
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_id)
        if device and "telemetry" in device and device["telemetry"]:
            return device["telemetry"][0].get("humidity")
        return None


class BondedDevicePressureSensor(BaseRaptSensor):
    """Bonded Device Pressure Sensor."""

    def __init__(self, coordinator, device_id: str):
        device = coordinator.data.get(device_id, {})
        model = f"{device.get('deviceType', 'Bonded Device')} (Bonded Device)"
        super().__init__(
            coordinator,
            device_id,
            model=model,
            name_suffix="Pressure",
            unique_suffix="pressure",
            unit="kPa",
        )
        self._attr_device_class = SensorDeviceClass.PRESSURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_id)
        if device and "telemetry" in device and device["telemetry"]:
            return device["telemetry"][0].get("pressure")
        return None


class BondedDeviceBatterySensor(BaseRaptSensor):
    """Bonded Device Battery Sensor."""

    def __init__(self, coordinator, device_id: str):
        device = coordinator.data.get(device_id, {})
        model = f"{device.get('deviceType', 'Bonded Device')} (Bonded Device)"
        super().__init__(
            coordinator,
            device_id,
            model=model,
            name_suffix="Battery",
            unique_suffix="battery",
            unit="%",
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
