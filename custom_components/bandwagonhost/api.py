"""BandwagonHost API 客户端库。"""
import asyncio
import socket
import aiohttp
import async_timeout

from.const import API_ENDPOINT, DEFAULT_TIMEOUT

class BandwagonHostError(Exception):
    """基础异常类。"""

class BandwagonHostConnectionError(BandwagonHostError):
    """连接异常。"""

class BandwagonHostAuthError(BandwagonHostError):
    """认证异常。"""

class BandwagonHostAPI:
    """处理与 KiwiVM API 的通信。"""

    def __init__(
        self, 
        session: aiohttp.ClientSession, 
        veid: str, 
        api_key: str
    ) -> None:
        """初始化 API 客户端。"""
        self._session = session
        self._veid = veid
        self._api_key = api_key

    async def async_get_service_info(self) -> dict:
        """获取 VPS 服务信息。"""
        params = {
            "veid": self._veid,
            "api_key": self._api_key
        }
        
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                response = await self._session.get(
                    API_ENDPOINT, 
                    params=params
                )
                response.raise_for_status()
                data = await response.json()
                
                # KiwiVM API 返回 error: 0 表示成功
                if data.get("error")!= 0:
                    error_msg = data.get("message", "Unknown API error")
                    raise BandwagonHostAuthError(f"API Error {data.get('error')}: {error_msg}")
                
                return data

        except asyncio.TimeoutError as exception:
            raise BandwagonHostConnectionError("Timeout fetching data from KiwiVM") from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise BandwagonHostConnectionError(f"Error communicating with KiwiVM: {exception}") from exception
