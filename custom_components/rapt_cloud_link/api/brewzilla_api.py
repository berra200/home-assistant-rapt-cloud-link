from aiohttp import ClientSession, ClientError
from async_timeout import timeout
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging

from ..const import API_BASE

_LOGGER = logging.getLogger(__name__)


async def get_brewzillas(hass, token):
    """Fetch BrewZilla devices from the RAPT Cloud API."""
    session: ClientSession = async_get_clientsession(hass)
    url = f"{API_BASE}/BrewZillas/GetBrewZillas"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    try:
        async with session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
            _LOGGER.debug(f"Fetched BrewZilla devices: {data}")
            return data
    except Exception as e:
        _LOGGER.error(f"Error fetching BrewZilla devices: {e}")
        raise


async def set_heating_enabled(hass, token: str, device_id: str, enabled: bool) -> bool:
    """Enable or disable heating on a BrewZilla device."""
    session = async_get_clientsession(hass)

    url = f"{API_BASE}/BrewZillas/SetHeatingEnabled?brewZillaId={device_id}&state={str(enabled).lower()}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with timeout(10):
            async with session.post(url, headers=headers) as resp:
                if resp.status == 200:
                    _LOGGER.debug(f"Heating {'enabled' if enabled else 'disabled'} for device {device_id}")
                    return True
                else:
                    text = await resp.text()
                    _LOGGER.warning(f"Failed to set heating: {resp.status} - {text}")
                    return False
    except ClientError as e:
        _LOGGER.error(f"Connection error when setting heating: {e}")
        return False
    

async def set_pump_enabled(hass, token: str, device_id: str, enabled: bool) -> bool:
    """Enable or disable pumping on a BrewZilla device."""
    session = async_get_clientsession(hass)

    url = f"{API_BASE}/BrewZillas/SetPumpEnabled?brewZillaId={device_id}&state={str(enabled).lower()}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with timeout(10):
            async with session.post(url, headers=headers) as resp:
                if resp.status == 200:
                    _LOGGER.debug(f"Pump {'enabled' if enabled else 'disabled'} for device {device_id}")
                    return True
                else:
                    text = await resp.text()
                    _LOGGER.warning(f"Failed to set pump: {resp.status} - {text}")
                    return False
    except ClientError as e:
        _LOGGER.error(f"Connection error when setting pump: {e}")
        return False
    

async def set_heating_utilization(hass, token: str, device_id: str, percent: int) -> bool:
    """Set heating utilisation on a BrewZilla device."""
    session = async_get_clientsession(hass)

    url = (
        f"{API_BASE}/BrewZillas/SetHeatingUtilisation"
        f"?brewZillaId={device_id}&utilisation={percent}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with timeout(10):
            async with session.post(url, headers=headers) as resp:
                if resp.status == 200:
                    _LOGGER.debug(
                        f"Successfully set heating utilisation to {percent}% for device {device_id}"
                    )
                    return True
                else:
                    text = await resp.text()
                    _LOGGER.warning(
                        f"Failed to set heating utilisation for device {device_id}: {resp.status} - {text}"
                    )
                    return False
    except ClientError as e:
        _LOGGER.error(f"Connection error when setting heating utilisation: {e}")
        return False
    

async def set_pump_utilization(hass, token: str, device_id: str, percent: int) -> bool:
    """Set pump utilisation on a BrewZilla device."""
    session = async_get_clientsession(hass)

    url = (
        f"{API_BASE}/BrewZillas/SetPumpUtilisation"
        f"?brewZillaId={device_id}&utilisation={percent}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with timeout(10):
            async with session.post(url, headers=headers) as resp:
                if resp.status == 200:
                    _LOGGER.debug(
                        f"Successfully set pump utilisation to {percent}% for device {device_id}"
                    )
                    return True
                else:
                    text = await resp.text()
                    _LOGGER.warning(
                        f"Failed to set pump utilisation for device {device_id}: {resp.status} - {text}"
                    )
                    return False
    except ClientError as e:
        _LOGGER.error(f"Connection error when setting pump utilisation: {e}")
        return False
    

async def set_target_temperature(hass, token: str, device_id: str, temperature: float) -> bool:
    """Set target temperature on BrewZilla device."""
    session = async_get_clientsession(hass)

    url = (
        f"{API_BASE}/BrewZillas/SetTargetTemperature"
        f"?brewZillaId={device_id}&target={temperature}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with timeout(10):
            async with session.post(url, headers=headers) as resp:
                if resp.status == 200:
                    _LOGGER.debug(
                        f"Target temperature set to {temperature}°C for device {device_id}"
                    )
                    return True
                else:
                    text = await resp.text()
                    _LOGGER.warning(
                        f"Failed to set target temperature: {resp.status} - {text}"
                    )
                    return False
    except ClientError as e:
        _LOGGER.error(f"Connection error when setting target temperature: {e}")
        return False