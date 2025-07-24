from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up BrewZilla switches from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    switches = []

    for device_id, device in coordinator.data.items():
        name = device.get("name", f"BrewZilla {device_id}")
        switches.append(BrewZillaHeaterSwitch(coordinator, device_id, name))
        switches.append(BrewZillaPumpSwitch(coordinator, device_id, name))

    if switches:
        async_add_entities(switches, update_before_add=True)
    else:
        _LOGGER.warning("No BrewZilla devices found")


class BrewZillaHeaterSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{device_name} Heater"
        self._attr_unique_id = f"{device_id}_heater"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

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


class BrewZillaPumpSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, device_id: str, device_name: str):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"{device_name} Pump"
        self._attr_unique_id = f"{device_id}_pump"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device_name,
            "manufacturer": "RAPT",
            "model": "BrewZilla",
        }

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

























# from homeassistant.components.switch import SwitchEntity
# import logging

# from .api.brewzilla_api import set_heating_enabled, set_pump_enabled


# _LOGGER = logging.getLogger(__name__)


# async def async_setup_entry(hass, entry, async_add_entities):
#     """Set up switches from a config entry."""
#     coordinator = hass.data["rapt_cloud_link"][entry.entry_id]["coordinator"]

#     switches = []
#     for device_id in coordinator.data:
#         switches.append(BrewZillaHeaterSwitch(coordinator, device_id))
#         switches.append(BrewZillaPumpSwitch(coordinator, device_id))

#     async_add_entities(switches, update_before_add=True)


# # ---------------------
# # Brewzilla
# # ---------------------

# class BrewZillaHeaterSwitch(SwitchEntity):
#     def __init__(self, coordinator, device_id):
#         self.coordinator = coordinator
#         self._device_id = device_id
#         self._attr_name = "Heater"
#         self._attr_unique_id = f"{self._device_id}_heater"
#         self._attr_device_info = {
#             "identifiers": {("rapt_cloud_link", self._device_id)},
#             "name": f"BrewZilla {self._device_id}",
#             "manufacturer": "RAPT",
#             "model": "BrewZilla",
#         }

#     @property
#     def is_on(self):
#         device_data = self.coordinator.data.get(self._device_id, {})
#         return device_data.get("heatingEnabled", False)

#     async def async_turn_on(self, **kwargs):
#         token = await self.coordinator.token_manager.get_token()
#         success = await set_heating_enabled(self.coordinator.hass, token, self._device_id, True)
#         if success:
#             if self._device_id in self.coordinator.data:
#                 self.coordinator.data[self._device_id]["heatingEnabled"] = True
#             self.async_write_ha_state()

#     async def async_turn_off(self, **kwargs):
#         token = await self.coordinator.token_manager.get_token()
#         success = await set_heating_enabled(self.coordinator.hass, token, self._device_id, False)
#         if success:
#             if self._device_id in self.coordinator.data:
#                 self.coordinator.data[self._device_id]["heatingEnabled"] = False
#             self.async_write_ha_state()

#     async def async_added_to_hass(self):
#         self._unsub = self.coordinator.async_add_listener(self.async_write_ha_state)

#     async def async_will_remove_from_hass(self):
#         self._unsub()


# class BrewZillaPumpSwitch(SwitchEntity):
#     def __init__(self, coordinator, device_id):
#         self.coordinator = coordinator
#         self._device_id = device_id
#         self._attr_name = "Pump"
#         self._attr_unique_id = f"{self._device_id}_pump"
#         self._attr_device_info = {
#             "identifiers": {("rapt_cloud_link", self._device_id)},
#             "name": f"BrewZilla {self._device_id}",
#             "manufacturer": "RAPT",
#             "model": "BrewZilla",
#         }

#     @property
#     def is_on(self):
#         device_data = self.coordinator.data.get(self._device_id, {})
#         return device_data.get("pumpEnabled", False)

#     async def async_turn_on(self, **kwargs):
#         token = await self.coordinator.token_manager.get_token()
#         success = await set_pump_enabled(self.coordinator.hass, token, self._device_id, True)
#         if success:
#             if self._device_id in self.coordinator.data:
#                 self.coordinator.data[self._device_id]["pumpEnabled"] = True
#             self.async_write_ha_state()

#     async def async_turn_off(self, **kwargs):
#         token = await self.coordinator.token_manager.get_token()
#         success = await set_pump_enabled(self.coordinator.hass, token, self._device_id, False)
#         if success:
#             if self._device_id in self.coordinator.data:
#                 self.coordinator.data[self._device_id]["pumpEnabled"] = False
#             self.async_write_ha_state()

#     async def async_added_to_hass(self):
#         self._unsub = self.coordinator.async_add_listener(self.async_write_ha_state)

#     async def async_will_remove_from_hass(self):
#         self._unsub()