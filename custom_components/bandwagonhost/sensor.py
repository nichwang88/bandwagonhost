"""支持 BandwagonHost 传感器。"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from.const import DOMAIN
from.coordinator import BandwagonHostCoordinator

@dataclass
class BandwagonHostSensorDescription(SensorEntityDescription):
    """自定义传感器描述符，增加取值函数。"""
    value_fn: Callable[[dict[str, Any]], StateType] = lambda _: None

SENSOR_TYPES: tuple = (
    BandwagonHostSensorDescription(
        key="data_counter",
        name="流量已用",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("data_counter"),
    ),
    BandwagonHostSensorDescription(
        key="plan_monthly_data",
        name="流量配额",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        value_fn=lambda data: data.get("plan_monthly_data"),
    ),
    BandwagonHostSensorDescription(
        key="plan_ram",
        name="内存配额",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        value_fn=lambda data: data.get("plan_ram"),
    ),
    BandwagonHostSensorDescription(
        key="vm_type",
        name="虚拟化类型",
        icon="mdi:server",
        value_fn=lambda data: data.get("vm_type"),
    ),
    BandwagonHostSensorDescription(
        key="os",
        name="操作系统",
        icon="mdi:linux",
        value_fn=lambda data: data.get("os"),
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置传感器平台。"""
    coordinator: BandwagonHostCoordinator = hass.data[entry.entry_id]
    async_add_entities(
        BandwagonHostSensor(coordinator, description)
        for description in SENSOR_TYPES
    )

class BandwagonHostSensor(CoordinatorEntity, SensorEntity):
    """BandwagonHost 传感器实体。"""
    
    entity_description: BandwagonHostSensorDescription

    def __init__(
        self,
        coordinator: BandwagonHostCoordinator,
        description: BandwagonHostSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.veid}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.veid)},
            "name": f"VPS {coordinator.veid}",
            "manufacturer": "BandwagonHost",
            "model": "KVM VPS",
            "configuration_url": "https://kiwivm.64clouds.com/",
        }

    @property
    def native_value(self) -> StateType:
        return self.entity_description.value_fn(self.coordinator.data)
