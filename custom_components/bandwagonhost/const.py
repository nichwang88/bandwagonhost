"""BandwagonHost 集成常量。"""
import logging

DOMAIN = "bandwagonhost"
LOGGER = logging.getLogger(__package__)

CONF_VEID = "veid"
CONF_API_KEY = "api_key"

API_ENDPOINT = "https://api.64clouds.com/v1/getServiceInfo"
DEFAULT_TIMEOUT = 10
SCAN_INTERVAL = 20  # 轮询间隔（分钟）
