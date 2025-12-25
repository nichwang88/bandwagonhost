import logging
from datetime import timedelta
import requests
import voluptuous as vol
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required("veid"): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional("monitored_conditions", default=[]): vol.All(cv.ensure_list, [cv.string]),
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    conf = config.get(DOMAIN)
    if not conf:
        return
    coordinator = BandwagonCoordinator(hass, conf)
    await coordinator.async_refresh()

    sensors = [
        BandwagonSensor(coordinator, condition)
        for condition in conf["monitored_conditions"]
    ]
    async_add_entities(sensors, update_before_add=True)

class BandwagonCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, conf):
        super().__init__(
            hass,
            _LOGGER,
            name="Bandwagon Host",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.conf = conf

    async def _async_update_data(self):
        try:
            return await hass.async_add_executor_job(self.fetch_status)
        except Exception as err:
            raise UpdateFailed(err)

    def fetch_status(self):
        url = f"https://api.vultr.com/{self.conf['veid']}"
        headers = {"API-Key": self.conf["api_key"]}
        return requests.get(url, headers=headers).json()

class BandwagonSensor(SensorEntity):
    def __init__(self, coordinator, condition):
        self.coordinator = coordinator
        self.condition = condition

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.condition}"

    @property
    def name(self):
        return f"Bandwagon {self.condition}"

    @property
    def state(self):
        return self.coordinator.data.get(self.condition)

    async def async_update(self):
        await self.coordinator.async_request_refresh()
