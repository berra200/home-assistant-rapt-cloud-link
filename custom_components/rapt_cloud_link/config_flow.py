import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from aiohttp import ClientResponseError
from .const import CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT, TOKEN_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            email = user_input.get("email")
            api_token = user_input.get("api_token")

            if await self._validate_credentials(email, api_token):
                return self.async_create_entry(
                    title=email,
                    data={
                        "email": email,
                        "api_token": api_token,
                        CONF_TEMPERATURE_UNIT: user_input.get(CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT),
                    },
                )
            else:
                errors["base"] = "auth_failed"

        data_schema = vol.Schema(
            {
                vol.Required("email"): cv.string,
                vol.Required("api_token"): cv.string,
                vol.Optional(CONF_TEMPERATURE_UNIT, default=DEFAULT_TEMPERATURE_UNIT): vol.In(["C", "F"]),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    # Validate credentials against the API
    async def _validate_credentials(self, email: str, token: str) -> bool:
        """Attempt to authenticate against the API with email and token."""
        session = async_get_clientsession(self.hass)
        url = TOKEN_URL
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        body = {
            "grant_type": "password",
            "client_id": "rapt-user",
            "username": email,
            "password": token,
        }

        try:
            resp = await session.post(url, data=body, headers=headers)
            if resp.status == 200:
                json_resp = await resp.json()
                _LOGGER.debug(f"Authentication response: {json_resp}")
                return True
            else:
                _LOGGER.warning(f"Authentication failed, status code: {resp.status}")
                return False
        except ClientResponseError as e:
            _LOGGER.error(f"HTTP error during authentication: {e}")
            return False
        except Exception as e:
            _LOGGER.error(f"Unexpected error during authentication: {e}")
            return False
