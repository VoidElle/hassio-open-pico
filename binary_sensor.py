"""Binary Sensor platform for Open Pico integration."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .base import BaseEntity
from .coordinator import MainCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
):
    """Set up the Binary Sensor platform from YAML."""
    if discovery_info is None:
        return

    # Get all coordinators from hass.data
    coordinators = hass.data[DOMAIN]["coordinators"]

    # Create binary sensor entities for each coordinator/device
    sensors = []
    for idx, coordinator in enumerate(coordinators):
        sensors.append(PicoMaintenanceBinarySensor(coordinator, idx))

    async_add_entities(sensors)
    _LOGGER.info("Added %d binary sensor(s)", len(sensors))


class PicoMaintenanceBinarySensor(BaseEntity, BinarySensorEntity):
    """Binary sensor for filter maintenance status."""

    _attr_translation_key = "filter_maintenance"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_filter_maintenance_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "Filter Maintenance Required"

    @property
    def is_on(self) -> bool | None:
        """Return true if maintenance is required."""
        if not self.coordinator.data or not self.coordinator.data.device_info:
            return None
        return self.coordinator.data.device_info.needs_clean_filters_maintenance

    @property
    def icon(self) -> str:
        """Return the icon based on state."""
        if self.is_on:
            return "mdi:air-filter-remove"
        return "mdi:air-filter"