import logging
from datetime import datetime, timedelta
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..const import TOKEN_URL


_LOGGER = logging.getLogger(__name__)


class TokenManager:
    def __init__(self, hass, email, api_token, entry):
        self.hass = hass
        self.email = email
        self.api_token = api_token
        self.access_token = None
        self.token_expiry = None  # datetime när token går ut
        self.entry = entry

    async def get_token(self):
        """Returnerar giltig token, hämtar ny om gammal eller saknas."""
        if self.access_token is None or self._token_expired():
            await self._fetch_new_token()
        return self.access_token

    def _token_expired(self):
        if self.token_expiry is None:
            return True
        return datetime.utcnow() >= self.token_expiry

    async def _fetch_new_token(self):
        session = async_get_clientsession(self.hass)
        url = TOKEN_URL
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "password",
            "client_id": "rapt-user",
            "username": self.email,
            "password": self.api_token,
        }
        try:
            resp = await session.post(url, data=body, headers=headers)
            resp.raise_for_status()
            data = await resp.json()
            self.access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)  # default 1h

            # Sätt expiry 5 min tidigare än faktisk för säkerhets skull
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 300)

            _LOGGER.debug(f"Ny token hämtad, giltig i {expires_in} sekunder")
        except Exception as e:
            _LOGGER.error(f"Misslyckades att hämta token: {e}")
            raise