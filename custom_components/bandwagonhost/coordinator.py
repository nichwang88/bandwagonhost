"""BandwagonHost 数据协调器。"""
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from.const import DOMAIN, LOGGER, SCAN_INTERVAL
from.api import BandwagonHostAPI, BandwagonHostError

class BandwagonHostCoordinator(DataUpdateCoordinator):
    """管理从 BandwagonHost API 获取数据的类。"""

    def __init__(
        self, 
        hass: HomeAssistant, 
        api: BandwagonHostAPI
    ) -> None:
        """初始化协调器。"""
        self.api = api
        self.veid = api._veid

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        """获取最新的数据。"""
        try:
            return await self.api.async_get_service_info()
        except BandwagonHostError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
