"""BandwagonHost 集成的配置流处理程序。"""
from __future__ import annotations
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from.const import DOMAIN, CONF_VEID, LOGGER
from.api import BandwagonHostAPI, BandwagonHostAuthError, BandwagonHostConnectionError

class BandwagonHostConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理 BandwagonHost 的配置流。"""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """处理用户发起的配置步骤。"""
        errors: dict[str, str] = {}

        if user_input is not None:
            # 1. 唯一性检查
            await self.async_set_unique_id(str(user_input))
            self._abort_if_unique_id_configured()

            # 2. 验证凭证
            session = async_get_clientsession(self.hass)
            
            # [修复关键点] 必须传入具体的字符串值，而不是整个字典
            api = BandwagonHostAPI(
                session, 
                user_input, 
                user_input
            )

            try:
                await api.async_get_service_info()
            except BandwagonHostAuthError:
                errors["base"] = "invalid_auth"
            except BandwagonHostConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # 3. 验证通过，创建配置条目
                return self.async_create_entry(
                    title=f"VPS {user_input}",
                    data=user_input,
                )

        # 定义表单
        data_schema = vol.Schema({
            vol.Required(CONF_VEID): str,
            vol.Required(CONF_API_KEY): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
