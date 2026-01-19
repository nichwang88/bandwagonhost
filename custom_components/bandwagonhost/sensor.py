"""BandwagonHost sensor platform."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfInformation,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BandwagonHostCoordinator


@dataclass(frozen=True, kw_only=True)
class BwhSensorEntityDescription(SensorEntityDescription):
    """Describes BandwagonHost sensor entity."""

    value_fn: Callable[[dict[str, Any]], StateType] = lambda x: None
    available_fn: Callable[[dict[str, Any]], bool] = lambda x: True


SENSOR_DESCRIPTIONS: tuple[BwhSensorEntityDescription, ...] = (
    # VPS Status
    BwhSensorEntityDescription(
        key="vps_state",
        translation_key="vps_state",
        icon="mdi:server",
        value_fn=lambda data: data.get("vps_state"),
    ),
    # Bandwidth sensors
    BwhSensorEntityDescription(
        key="bandwidth_used",
        translation_key="bandwidth_used",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:upload-network",
        value_fn=lambda data: data.get("data_counter_gb"),
    ),
    BwhSensorEntityDescription(
        key="bandwidth_remaining",
        translation_key="bandwidth_remaining",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:download-network",
        value_fn=lambda data: data.get("bandwidth_remaining_gb"),
    ),
    BwhSensorEntityDescription(
        key="bandwidth_total",
        translation_key="bandwidth_total",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:network",
        value_fn=lambda data: data.get("plan_monthly_data_gb"),
    ),
    BwhSensorEntityDescription(
        key="bandwidth_used_percent",
        translation_key="bandwidth_used_percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
        value_fn=lambda data: data.get("bandwidth_used_percent"),
    ),
    # Disk sensors
    BwhSensorEntityDescription(
        key="disk_used",
        translation_key="disk_used",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:harddisk",
        value_fn=lambda data: data.get("ve_used_disk_space_gb"),
        available_fn=lambda data: "ve_used_disk_space_gb" in data,
    ),
    BwhSensorEntityDescription(
        key="disk_total",
        translation_key="disk_total",
        native_unit_of_measurement=UnitOfInformation.GIGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:harddisk",
        value_fn=lambda data: data.get("plan_disk_gb"),
    ),
    BwhSensorEntityDescription(
        key="disk_used_percent",
        translation_key="disk_used_percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:harddisk",
        value_fn=lambda data: data.get("disk_used_percent"),
        available_fn=lambda data: "disk_used_percent" in data,
    ),
    # Memory sensors
    BwhSensorEntityDescription(
        key="ram_total",
        translation_key="ram_total",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        icon="mdi:memory",
        value_fn=lambda data: data.get("plan_ram_mb"),
    ),
    BwhSensorEntityDescription(
        key="ram_used",
        translation_key="ram_used",
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
        value_fn=lambda data: data.get("mem_used_mb"),
        available_fn=lambda data: "mem_used_mb" in data,
    ),
    BwhSensorEntityDescription(
        key="ram_used_percent",
        translation_key="ram_used_percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:memory",
        value_fn=lambda data: data.get("mem_used_percent"),
        available_fn=lambda data: "mem_used_percent" in data,
    ),
    # System info
    BwhSensorEntityDescription(
        key="hostname",
        translation_key="hostname",
        icon="mdi:server",
        value_fn=lambda data: data.get("hostname"),
    ),
    BwhSensorEntityDescription(
        key="os",
        translation_key="os",
        icon="mdi:linux",
        value_fn=lambda data: data.get("os"),
    ),
    BwhSensorEntityDescription(
        key="node_location",
        translation_key="node_location",
        icon="mdi:map-marker",
        value_fn=lambda data: data.get("node_location"),
    ),
    BwhSensorEntityDescription(
        key="ip_address",
        translation_key="ip_address",
        icon="mdi:ip-network",
        value_fn=lambda data: data.get("ip_addresses", [""])[0] if data.get("ip_addresses") else None,
    ),
    BwhSensorEntityDescription(
        key="load_average",
        translation_key="load_average",
        icon="mdi:gauge",
        value_fn=lambda data: data.get("load_average"),
        available_fn=lambda data: "load_average" in data,
    ),
    # Status flags
    BwhSensorEntityDescription(
        key="cpu_throttled",
        translation_key="cpu_throttled",
        icon="mdi:speedometer-slow",
        value_fn=lambda data: "Yes" if data.get("is_cpu_throttled") else "No",
    ),
    BwhSensorEntityDescription(
        key="suspended",
        translation_key="suspended",
        icon="mdi:pause-circle",
        value_fn=lambda data: "Yes" if data.get("suspended") else "No",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BandwagonHost sensors based on a config entry."""
    coordinator: BandwagonHostCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        BandwagonHostSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class BandwagonHostSensor(CoordinatorEntity[BandwagonHostCoordinator], SensorEntity):
    """Representation of a BandwagonHost sensor."""

    entity_description: BwhSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BandwagonHostCoordinator,
        entry: ConfigEntry,
        description: BwhSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            name=f"BandwagonHost {entry.unique_id}",
            manufacturer="BandwagonHost",
            model=coordinator.data.get("plan", "VPS") if coordinator.data else "VPS",
            sw_version=coordinator.data.get("os", "") if coordinator.data else None,
            configuration_url="https://bandwagonhost.com/clientarea.php",
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not super().available or self.coordinator.data is None:
            return False
        return self.entity_description.available_fn(self.coordinator.data)
