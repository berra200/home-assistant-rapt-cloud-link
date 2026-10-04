from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from .const import DOMAIN
from .base import BaseRaptBinarySensor


async def async_setup_entry(hass, entry, async_add_entities):
    brewzilla_coordinator = hass.data[DOMAIN][entry.entry_id]["brewzilla_coordinator"]

    binary_sensors = []

    # BrewZilla
    for device_id in brewzilla_coordinator.data:
        binary_sensors.append(BrewZillaProfileSessionBinarySensor(brewzilla_coordinator, device_id))
        binary_sensors.append(BrewZillaAtTargetTemperatureBinarySensor(brewzilla_coordinator, device_id))

    if binary_sensors:
        async_add_entities(binary_sensors, update_before_add=True)


def _control_temperature(device):
    """Return the temperature the BrewZilla regulates on.

    That is its bonded probe unless it is set to use its internal sensor.
    """
    if not device.get("useInternalSensor") and device.get("controlDeviceType") and device.get("controlDeviceTemperature") is not None:
        return device["controlDeviceTemperature"]
    return device.get("temperature")


class BrewZillaProfileSessionBinarySensor(BaseRaptBinarySensor):
    """BrewZilla Profile Session Binary Sensor: on while a profile session runs."""

    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="BrewZilla",
            name_suffix="Profile Session",
            unique_suffix="profile_session",
        )
        self._attr_device_class = BinarySensorDeviceClass.RUNNING

    @property
    def is_on(self):
        device = self.coordinator.data.get(self._device_id)
        return bool(device and device.get("activeProfileSession"))


class BrewZillaAtTargetTemperatureBinarySensor(BaseRaptBinarySensor):
    """BrewZilla At Target Temperature Binary Sensor.

    On while the temperature the BrewZilla regulates on is within its heating
    hysteresis of the target, whichever side it comes from.
    """

    def __init__(self, coordinator, device_id: str):
        super().__init__(
            coordinator,
            device_id,
            model="BrewZilla",
            name_suffix="At Target Temperature",
            unique_suffix="at_target_temperature",
        )
        self._attr_icon = "mdi:thermometer-check"

    @property
    def is_on(self):
        device = self.coordinator.data.get(self._device_id)
        if not device:
            return None
        temperature = _control_temperature(device)
        target = device.get("targetTemperature")
        if temperature is None or target is None:
            return None
        return abs(temperature - target) <= (device.get("heatingHysteresis") or 1)

    @property
    def extra_state_attributes(self):
        device = self.coordinator.data.get(self._device_id) or {}
        temperature = _control_temperature(device)
        return {
            "control_temperature": round(temperature, 1) if temperature is not None else None,
            "target_temperature": device.get("targetTemperature"),
            "hysteresis": device.get("heatingHysteresis"),
        }
