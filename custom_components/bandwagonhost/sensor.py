from __future__ import annotations

from dataclasses import dataclass
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BandwagonHostCoordinator

@dataclass(frozen=True, kw_only=True)
class BwhSensorDescription(SensorEntityDescription):
  value_key: str

SENSORS: tuple[BwhSensorDescription, ...] = (
  BwhSensorDescription(key="vps_state", name="VPS State", value_key="vps_state"),
  BwhSensorDescription(key="ram_used", name="RAM Used", value_key="ram_used"),
  BwhSensorDescription(key="disk_used", name="Disk Used", value_key="disk_used"),
  # TODO: 按你 API 返回字段补齐
)

async def async_setup_entry(
  hass: HomeAssistant,
  entry: ConfigEntry,
  async_add_entities: AddEntitiesCallback,
) -> None:
  coordinator: BandwagonHostCoordinator = hass.data[DOMAIN][entry.entry_id]
  async_add_entities(
    BandwagonHostSensor(coordinator, entry, description) for description in SENSORS
  )

class BandwagonHostSensor(CoordinatorEntity[BandwagonHostCoordinator], SensorEntity):
  def __init__(
    self,
    coordinator: BandwagonHostCoordinator,
    entry: ConfigEntry,
    description: BwhSensorDescription,
  ) -> None:
    super().__init__(coordinator)
    self.entity_description = description
    self._attr_unique_id = f"{entry.unique_id}_{description.key}"
    self._attr_device_info = {
      "identifiers": {(DOMAIN, entry.unique_id)},
      "name": f"BandwagonHost {entry.unique_id}",
      "manufacturer": "BandwagonHost",
    }

  @property
  def native_value(self):
    data = self.coordinator.data or {}
    return data.get(self.entity_description.value_key)
