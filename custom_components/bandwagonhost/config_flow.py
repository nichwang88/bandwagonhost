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
    api = BandwagonHostAPI(
        session=async_get_clientsession(hass),
        veid=data[CONF_VEID],
        api_key=data[CONF_API_KEY],
    )

    # Test the connection by getting service info
    info = await api.async_get_service_info()

    return {
        "title": info.get("hostname", f"BandwagonHost {data[CONF_VEID]}"),
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
            except BandwagonHostAuthError:
                errors["base"] = "invalid_auth"
            except BandwagonHostConnectionError:
                errors["base"] = "cannot_connect"
            except BandwagonHostAPIError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID to prevent duplicate entries
                await self.async_set_unique_id(user_input[CONF_VEID])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
