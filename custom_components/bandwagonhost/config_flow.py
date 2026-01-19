"""Config flow for BandwagonHost integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    BandwagonHostAPI,
    BandwagonHostAPIError,
    BandwagonHostAuthError,
    BandwagonHostConnectionError,
)
from .const import CONF_API_KEY, CONF_VEID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VEID): str,
        vol.Required(CONF_API_KEY): str,
    }
)


async def _async_validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Returns info to store in the config entry.
    """
    _LOGGER.debug("Validating input for VEID: %s", data[CONF_VEID])

    api = BandwagonHostAPI(
        session=async_get_clientsession(hass),
        veid=data[CONF_VEID].strip(),
        api_key=data[CONF_API_KEY].strip(),
    )

    # Test the connection by getting service info
    info = await api.async_get_service_info()
    _LOGGER.debug("Successfully retrieved service info: %s", info.get("hostname", "unknown"))

    return {
        "title": info.get("hostname") or f"BandwagonHost {data[CONF_VEID]}",
        "hostname": info.get("hostname", ""),
        "plan": info.get("plan", ""),
    }


class BandwagonHostConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BandwagonHost."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await _async_validate_input(self.hass, user_input)
            except BandwagonHostAuthError as err:
                _LOGGER.warning("Authentication failed: %s", err)
                errors["base"] = "invalid_auth"
            except BandwagonHostConnectionError as err:
                _LOGGER.warning("Connection error: %s", err)
                errors["base"] = "cannot_connect"
            except BandwagonHostAPIError as err:
                _LOGGER.warning("API error: %s", err)
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"
            else:
                # Set unique ID to prevent duplicate entries
                veid = user_input[CONF_VEID].strip()
                await self.async_set_unique_id(veid)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_VEID: veid,
                        CONF_API_KEY: user_input[CONF_API_KEY].strip(),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
