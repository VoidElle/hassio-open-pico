"""Sensor platform for Open Pico integration."""
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    CONCENTRATION_PARTS_PER_MILLION,
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
    """Set up the Sensor platform from YAML."""

    # Get all coordinators from hass.data
    coordinators = hass.data[DOMAIN]["coordinators"]

    # Create sensor entities for each coordinator/device
    sensors = []
    for idx, coordinator in enumerate(coordinators):
        sensors.extend([
            PicoTemperatureSensor(coordinator, idx),
            PicoHumiditySensor(coordinator, idx),
            PicoAirQualitySensor(coordinator, idx),
            PicoTVOCSensor(coordinator, idx),
            PicoECO2Sensor(coordinator, idx),
        ])

    async_add_entities(sensors)


class PicoTemperatureSensor(BaseEntity, SensorEntity):
    """Representation of a Pico Temperature Sensor."""

    _attr_translation_key = "temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_temperature_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.sensors or not self.coordinator.data.sensors.temperature:
            return None
        return self.coordinator.data.sensors.temperature_celsius


class PicoHumiditySensor(BaseEntity, SensorEntity):
    """Representation of a Pico Humidity Sensor."""

    _attr_translation_key = "humidity"
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_humidity_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "Humidity"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.sensors or not self.coordinator.data.sensors.humidity:
            return None
        return self.coordinator.data.sensors.humidity_percent


class PicoAirQualitySensor(BaseEntity, SensorEntity):
    """Representation of a Pico Air Quality (CO2) Sensor."""

    _attr_translation_key = "air_quality"
    _attr_device_class = SensorDeviceClass.CO2
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_air_quality_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "CO2"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.sensors or not self.coordinator.data.sensors.air_quality:
            return None
        return self.coordinator.data.sensors.air_quality


class PicoTVOCSensor(BaseEntity, SensorEntity):
    """Representation of a Pico TVOC (Total Volatile Organic Compounds) Sensor."""

    _attr_translation_key = "tvoc"
    _attr_device_class = SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_tvoc_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "TVOC"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.sensors or not self.coordinator.data.sensors.tvoc:
            return None
        return self.coordinator.data.sensors.tvoc

    @property
    def icon(self) -> str:
        """Return the icon based on TVOC level."""
        if not self.coordinator.data or not self.coordinator.data.sensors or not self.coordinator.data.sensors.tvoc:
            return "mdi:chemical-weapon"

        tvoc = self.coordinator.data.sensors.tvoc

        # TVOC level thresholds (ppb or µg/m³)
        # < 220: Excellent
        # 220-660: Good
        # 660-2200: Moderate
        # 2200-5500: Poor
        # > 5500: Very Poor

        if tvoc < 220:
            return "mdi:air-filter"
        elif tvoc < 660:
            return "mdi:chemical-weapon"
        elif tvoc < 2200:
            return "mdi:alert-circle-outline"
        elif tvoc < 5500:
            return "mdi:alert"
        else:
            return "mdi:alert-octagon"


class PicoECO2Sensor(BaseEntity, SensorEntity):
    """Representation of a Pico eCO2 (equivalent CO2) Sensor."""

    _attr_translation_key = "eco2"
    _attr_device_class = SensorDeviceClass.CO2
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_eco2_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "eCO2"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.sensors or not self.coordinator.data.sensors.eco2:
            return None
        return self.coordinator.data.sensors.eco2

    @property
    def icon(self) -> str:
        """Return the icon based on eCO2 level."""
        if not self.coordinator.data or not self.coordinator.data.sensors or not self.coordinator.data.sensors.eco2:
            return "mdi:molecule-co2"

        eco2 = self.coordinator.data.sensors.eco2

        # eCO2 level thresholds (ppm) - similar to CO2
        # < 600: Excellent
        # 600-1000: Good
        # 1000-1500: Moderate
        # 1500-2000: Poor
        # > 2000: Very Poor

        if eco2 < 600:
            return "mdi:air-filter"
        elif eco2 < 1000:
            return "mdi:molecule-co2"
        elif eco2 < 1500:
            return "mdi:alert-circle-outline"
        elif eco2 < 2000:
            return "mdi:alert"
        else:
            return "mdi:alert-octagon"