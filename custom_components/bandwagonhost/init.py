from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS, CONF_VEID, CONF_API_KEY
from .coordinator import BandwagonHostCoordinator

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
  # 可选：支持从 YAML 导入（import flow），否则可不做
  return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  coordinator = BandwagonHostCoordinator(
    hass,
    veid=entry.data[CONF_VEID],
    api_key=entry.data[CONF_API_KEY],
  )
  await coordinator.async_config_entry_first_refresh()

  hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
  await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
  return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
  unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
  if unload_ok:
    hass.data[DOMAIN].pop(entry.entry_id, None)
  return unload_ok
