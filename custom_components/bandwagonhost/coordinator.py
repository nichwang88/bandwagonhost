"""BandwagonHost Data Update Coordinator."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    BandwagonHostAPI,
    BandwagonHostAPIError,
    BandwagonHostAuthError,
    BandwagonHostConnectionError,
)
from .const import DEFAULT_SCAN_INTERVAL_MINUTES, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BandwagonHostCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """BandwagonHost data update coordinator."""

    def __init__(self, hass: HomeAssistant, veid: str, api_key: str) -> None:
        """Initialize the coordinator."""
        self.api = BandwagonHostAPI(
            session=async_get_clientsession(hass),
            veid=veid,
            api_key=api_key,
        )
        self.veid = veid

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{veid}",
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from BandwagonHost API."""
        try:
            return await self.api.async_get_status()
        except BandwagonHostAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except BandwagonHostConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except BandwagonHostAPIError as err:
            raise UpdateFailed(f"API error: {err}") from err
