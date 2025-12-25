from __future__ import annotations

from dataclasses import dataclass
import aiohttp

@dataclass
class BandwagonHostAPI:
  session: aiohttp.ClientSession
  veid: str
  api_key: str

  async def async_get_status(self) -> dict:
    # TODO: 把你现在的真实 API URL/参数/解析逻辑搬到这里
    # 例如：
    # url = "https://api.64clouds.com/v1/getServiceInfo"
    # params = {"veid": self.veid, "api_key": self.api_key}
    # async with self.session.get(url, params=params, timeout=30) as resp:
    #   resp.raise_for_status()
    #   return await resp.json()
    raise NotImplementedError
