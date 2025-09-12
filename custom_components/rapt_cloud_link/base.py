# base.py
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN


class BaseRaptEntity(CoordinatorEntity):
    """Base class for all RAPT entities."""
    def __init__(self, coordinator, device_id, device_name=None, model="RAPT"):
        super().__init__(coordinator)
        device_name = coordinator.data.get(device_id, {}).get("name", f"Device {device_id}")
        self._device_id = device_id
        self._device_name = device_name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": self._device_name,
            "manufacturer": "RAPT",
            "model": model,
        }

    async def async_added_to_hass(self):
        """Subscribe to coordinator updates when added to hass."""
        self._unsub = self.coordinator.async_add_listener(self._handle_coordinator_update)

    async def async_will_remove_from_hass(self):
        """Unsubscribe from coordinator updates when removed."""
        if hasattr(self, "_unsub") and self._unsub:
            self._unsub()

    def _handle_coordinator_update(self):
        """Update state when coordinator data changes."""
        self.async_write_ha_state()


class BaseRaptSensor(BaseRaptEntity, SensorEntity):
    """Base class for RAPT sensors."""
    def __init__(self, coordinator, device_id, name_suffix, unique_suffix, unit=None, model="RAPT"):
        super().__init__(coordinator, device_id, model=model)
        self._attr_name = name_suffix
        self._attr_unique_id = f"{device_id}_{unique_suffix}"
        self._attr_native_unit_of_measurement = unit


class BaseRaptNumber(BaseRaptEntity, NumberEntity):
    """Base class for RAPT numbers."""
    def __init__(self, coordinator, device_id, name_suffix, unique_suffix, unit=None, min_val=None, max_val=None, step=None, mode=None, model="RAPT"):
        super().__init__(coordinator, device_id, model=model)
        self._attr_name = f"{name_suffix}"
        self._attr_unique_id = f"{device_id}_{unique_suffix}"
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        if mode:
            self._attr_mode = mode


class BaseRaptSwitch(BaseRaptEntity, SwitchEntity):
    """Base class for RAPT switches."""
    def __init__(self, coordinator, device_id, name_suffix, unique_suffix, model="RAPT"):
        super().__init__(coordinator, device_id, model=model)
        self._attr_name = name_suffix
        self._attr_unique_id = f"{device_id}_{unique_suffix}"
