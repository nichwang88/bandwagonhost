from __future__ import annotations

from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BandwagonHostAPI
from .const import DEFAULT_SCAN_INTERVAL_MINUTES

class BandwagonHostCoordinator(DataUpdateCoordinator[dict]):
  def __init__(self, hass: HomeAssistant, veid: str, api_key: str) -> None:
    self.api = BandwagonHostAPI(async_get_clientsession(hass), veid, api_key)

    super().__init__(
      hass,
      logger=__import__("logging").getLogger(__name__),
      name="BandwagonHost",
      update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES),
    )

  async def _async_update_data(self) -> dict:
    try:
      return await self.api.async_get_status()
    except Exception as err:
      raise UpdateFailed(str(err)) from err
