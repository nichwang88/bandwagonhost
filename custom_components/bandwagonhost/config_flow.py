from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_VEID, CONF_API_KEY
from .api import BandwagonHostAPI

STEP_USER_DATA_SCHEMA = vol.Schema(
  {
    vol.Required(CONF_VEID): str,
    vol.Required(CONF_API_KEY): str,
  }
)

async def _async_validate_input(hass: HomeAssistant, data: dict) -> None:
  api = BandwagonHostAPI(async_get_clientsession(hass), data[CONF_VEID], data[CONF_API_KEY])
  # 做一次轻量 API 调用验证（失败就抛异常）
  await api.async_get_status()

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
  VERSION = 1

  async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
    errors: dict[str, str] = {}

    if user_input is not None:
      try:
        await _async_validate_input(self.hass, user_input)
      except Exception:
        errors["base"] = "cannot_connect"
      else:
        # 防重复（同 veid）
        await self.async_set_unique_id(user_input[CONF_VEID])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
          title=f"BandwagonHost {user_input[CONF_VEID]}",
          data=user_input,
        )

    return self.async_show_form(
      step_id="user",
      data_schema=STEP_USER_DATA_SCHEMA,
      errors=errors,
    )
