import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from aiohttp import ClientResponseError
from .const import TOKEN_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


# ---------------------
# Options Flow (via UI)
# ---------------------
class RaptCloudOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        super().__init__()
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                options=user_input,
            )
            _LOGGER.debug(f"Saved options: {user_input}")

            await self.hass.config_entries.async_reload(self.config_entry.entry_id)

            return self.async_create_entry(title="", data={})

        options = self.config_entry.options or {}
        current_interval = options.get("poll_interval", 3)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("poll_interval", default=current_interval): vol.All(int, vol.Range(min=1, max=60)),
            })
        )


# ---------------------
# Config Flow (initial setup)
# ---------------------
class RaptCloudFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
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
                    },
                )
            else:
                errors["base"] = "auth_failed"

        data_schema = vol.Schema(
            {
                vol.Required("email"): cv.string,
                vol.Required("api_token"): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    # Links the OptionsFlow to this ConfigFlow
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return RaptCloudOptionsFlowHandler(config_entry)

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
