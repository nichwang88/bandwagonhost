from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_VEID, CONF_API_KEY

# Step user: user 输入 VEID 和 API Key
class BandwagonHostConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Bandwagon Host integration."""

    VERSION = 1  # 版本号，用于未来迁移
    # 如果只允许单个配置实例，可以设置 SINGLE_CHECK = True，但这将阻止添加多个
    # SINGLE_CHECK = True

    def __init__(self) -> None:
        """初始化临时存储用户输入的参数"""
        self._data: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """第 1 步 — 用户通过 UI 增加集成时调用。"""
        errors: dict[str, str] = {}

        if user_input is not None:
            # 用户点击提交后，暂存输入
            veid = user_input.get(CONF_VEID)
            api_key = user_input.get(CONF_API_KEY)

            # 可在此检查用户输入是否合法，例如访问 Bandwagon API 进行验证
            # 如果验证失败，可以用 errors["base"] = "auth_failed"
            # 例如：
            # try:
            #     await self.hass.async_add_executor_job(check_credentials, veid, api_key)
            # except Exception:
            #     errors["base"] = "auth_failed"

            # 如果一切 OK，创建 config entry
            if not errors:
                self._data[CONF_VEID] = veid
                self._data[CONF_API_KEY] = api_key

                return self.async_create_entry(
                    title=f"Bandwagon ({veid})", data=self._data
                )

        # 显示 UI 表单
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_VEID, default=""): str,
                    vol.Required(CONF_API_KEY, default=""): str,
                }
            ),
            errors=errors,
        )
