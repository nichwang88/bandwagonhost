"""BandwagonHost 集成入口。"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from.const import DOMAIN, CONF_VEID, CONF_API_KEY
from.coordinator import BandwagonHostCoordinator
from.api import BandwagonHostAPI

# 修复：明确定义支持的平台列表
PLATFORMS: list[Platform] =

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """从配置条目设置集成。"""
    session = async_get_clientsession(hass)
    
    # 确保从 entry.data 中正确获取参数
    api = BandwagonHostAPI(
        session, 
        entry.data, 
        entry.data
    )
    
    coordinator = BandwagonHostCoordinator(hass, api)

    # 首次加载时尝试获取数据
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载配置条目。"""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data.pop(entry.entry_id)
    return unload_ok
