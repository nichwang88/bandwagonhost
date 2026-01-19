"""BandwagonHost API Client."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://api.64clouds.com/v1"
REQUEST_TIMEOUT = 30


class BandwagonHostAPIError(Exception):
    """Base exception for BandwagonHost API errors."""


class BandwagonHostAuthError(BandwagonHostAPIError):
    """Authentication error."""


class BandwagonHostConnectionError(BandwagonHostAPIError):
    """Connection error."""


@dataclass
class BandwagonHostAPI:
    """BandwagonHost API client."""

    session: aiohttp.ClientSession
    veid: str
    api_key: str
    _rate_limited: bool = field(default=False, init=False)

    async def _request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make an API request."""
        url = f"{API_BASE_URL}/{endpoint}"
        request_params = {
            "veid": self.veid,
            "api_key": self.api_key,
        }
        if params:
            request_params.update(params)

        _LOGGER.debug("Making request to %s", url)

        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                async with self.session.get(url, params=request_params) as response:
                    _LOGGER.debug("Response status: %s", response.status)

                    # Try to read response text first for debugging
                    response_text = await response.text()
                    _LOGGER.debug("Response text: %s", response_text[:500] if response_text else "empty")

                    # Check for HTTP errors
                    if response.status == 401:
                        raise BandwagonHostAuthError("Invalid VEID or API key")
                    if response.status == 429:
                        self._rate_limited = True
                        raise BandwagonHostAPIError("Rate limited by API")
                    if response.status >= 400:
                        raise BandwagonHostConnectionError(
                            f"HTTP error {response.status}: {response_text[:200]}"
                        )

                    # Try to parse JSON
                    try:
                        import json
                        data = json.loads(response_text)
                    except (json.JSONDecodeError, ValueError) as err:
                        _LOGGER.error("Failed to parse JSON response: %s", response_text[:200])
                        raise BandwagonHostAPIError(f"Invalid JSON response: {err}") from err

                    # Check for API-level errors
                    # BandwagonHost API returns error: 0 for success
                    # If error key exists and is not 0, it's an error
                    if isinstance(data, dict):
                        error_code = data.get("error")
                        if error_code is not None and error_code != 0:
                            error_msg = data.get("message", "Unknown API error")
                            _LOGGER.error("API error %s: %s", error_code, error_msg)
                            raise BandwagonHostAPIError(f"{error_msg}")

                    self._rate_limited = False
                    return data

        except asyncio.TimeoutError as err:
            _LOGGER.error("Request timeout for %s", endpoint)
            raise BandwagonHostConnectionError(f"Request timeout: {endpoint}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error for %s: %s", endpoint, err)
            raise BandwagonHostConnectionError(f"Connection error: {err}") from err

    async def async_get_service_info(self) -> dict[str, Any]:
        """Get basic service information."""
        return await self._request("getServiceInfo")

    async def async_get_live_service_info(self) -> dict[str, Any]:
        """Get live service information with real-time status.

        Note: This call may take up to 15 seconds to complete.
        """
        return await self._request("getLiveServiceInfo")

    async def async_get_status(self) -> dict[str, Any]:
        """Get VPS status - combines service info with processed data."""
        data = await self.async_get_live_service_info()

        # Process and normalize the data
        result = {
            # Basic info
            "hostname": data.get("hostname", ""),
            "vm_type": data.get("vm_type", ""),
            "os": data.get("os", ""),
            "node_location": data.get("node_location", ""),
            "ip_addresses": data.get("ip_addresses", []),

            # Plan info
            "plan": data.get("plan", ""),
            "plan_disk_bytes": data.get("plan_disk", 0),
            "plan_ram_bytes": data.get("plan_ram", 0),
            "plan_swap_bytes": data.get("plan_swap", 0),

            # Bandwidth
            "plan_monthly_data_bytes": data.get("plan_monthly_data", 0),
            "data_counter_bytes": data.get("data_counter", 0),
            "data_next_reset": data.get("data_next_reset", 0),
            "monthly_data_multiplier": data.get("monthly_data_multiplier", 1),

            # Status
            "suspended": data.get("suspended", 0),
            "is_cpu_throttled": data.get("is_cpu_throttled", 0),
            "ssh_port": data.get("ssh_port"),
        }

        # Calculate bandwidth usage percentage
        plan_data = result["plan_monthly_data_bytes"] * result["monthly_data_multiplier"]
        if plan_data > 0:
            result["bandwidth_used_percent"] = round(
                (result["data_counter_bytes"] / plan_data) * 100, 2
            )
        else:
            result["bandwidth_used_percent"] = 0

        # Convert bytes to GB for display
        result["plan_disk_gb"] = round(result["plan_disk_bytes"] / (1024**3), 2)
        result["plan_ram_mb"] = round(result["plan_ram_bytes"] / (1024**2), 2)
        result["plan_monthly_data_gb"] = round(plan_data / (1024**3), 2)
        result["data_counter_gb"] = round(result["data_counter_bytes"] / (1024**3), 2)
        result["bandwidth_remaining_gb"] = round(
            (plan_data - result["data_counter_bytes"]) / (1024**3), 2
        )

        # KVM specific
        if data.get("vm_type") == "kvm":
            result["ve_status"] = data.get("ve_status", "Unknown")
            result["ve_used_disk_space_bytes"] = data.get("ve_used_disk_space_b", 0)
            result["ve_used_disk_space_gb"] = round(
                result["ve_used_disk_space_bytes"] / (1024**3), 2
            )
            if result["plan_disk_bytes"] > 0:
                result["disk_used_percent"] = round(
                    (result["ve_used_disk_space_bytes"] / result["plan_disk_bytes"]) * 100, 2
                )
            else:
                result["disk_used_percent"] = 0

            # Memory stats (if available)
            if "mem_available_kb" in data:
                mem_available = data.get("mem_available_kb", 0) * 1024
                mem_total = result["plan_ram_bytes"]
                mem_used = mem_total - mem_available
                result["mem_used_mb"] = round(mem_used / (1024**2), 2)
                result["mem_available_mb"] = round(mem_available / (1024**2), 2)
                if mem_total > 0:
                    result["mem_used_percent"] = round((mem_used / mem_total) * 100, 2)
                else:
                    result["mem_used_percent"] = 0

            # Load average
            if "load_average" in data:
                result["load_average"] = data.get("load_average", "")

        # OVZ specific
        elif data.get("vm_type") == "ovz":
            vz_status = data.get("vz_status", {})
            result["ve_status"] = "Running" if vz_status else "Unknown"

            # Parse OVZ quota for disk usage
            vz_quota = data.get("vz_quota", {})
            if vz_quota:
                disk_used = vz_quota.get("disk_used_bytes", 0)
                result["ve_used_disk_space_bytes"] = disk_used
                result["ve_used_disk_space_gb"] = round(disk_used / (1024**3), 2)
                if result["plan_disk_bytes"] > 0:
                    result["disk_used_percent"] = round(
                        (disk_used / result["plan_disk_bytes"]) * 100, 2
                    )

        # Determine VPS state for simple status
        if result["suspended"]:
            result["vps_state"] = "Suspended"
        elif result.get("ve_status") == "Running":
            result["vps_state"] = "Running"
        elif result.get("ve_status") == "Stopped":
            result["vps_state"] = "Stopped"
        else:
            result["vps_state"] = result.get("ve_status", "Unknown")

        return result

    async def async_get_rate_limit_status(self) -> dict[str, Any]:
        """Get current rate limit status."""
        return await self._request("getRateLimitStatus")
