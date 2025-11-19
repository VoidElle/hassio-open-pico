"""Switch platform for Open Pico integration."""
import logging

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
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
    """Set up the Switch platform from YAML."""

    # Get all coordinators from hass.data
    coordinators = hass.data[DOMAIN]["coordinators"]

    # Create switch entities for each coordinator/device
    switches = []
    for idx, coordinator in enumerate(coordinators):
        switches.extend([
            PicoNightModeSwitch(coordinator, idx),
            PicoLEDStatusSwitch(coordinator, idx),
            PicoSupportsNightModeSwitch(coordinator, idx),
            PicoSupportsTargetHumiditySwitch(coordinator, idx),
        ])

    async_add_entities(switches)


class PicoNightModeSwitch(BaseEntity, SwitchEntity):
    """Representation of a Pico Night Mode Switch."""

    _attr_translation_key = "night_mode"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the switch."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_night_mode_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "Night Mode"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Only available if the device supports night mode
        return (
            super().available and
            self.coordinator.supports_night_mode
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if night mode is on."""
        return self.coordinator.night_mode_enabled

    async def async_turn_on(self, **kwargs) -> None:
        """Turn night mode on."""
        if not self.coordinator.supports_night_mode:
            current_mode = self.coordinator.current_mode.name if self.coordinator.current_mode else "Unknown"
            raise HomeAssistantError(
                f"Current mode '{current_mode}' does not support night mode"
            )

        try:
            await self.coordinator.async_set_night_mode(True)
        except Exception as err:
            _LOGGER.error("Failed to turn on night mode: %s", err)
            raise HomeAssistantError(f"Failed to turn on night mode: {err}") from err

    async def async_turn_off(self, **kwargs) -> None:
        """Turn night mode off."""
        if not self.coordinator.supports_night_mode:
            current_mode = self.coordinator.current_mode.name if self.coordinator.current_mode else "Unknown"
            raise HomeAssistantError(
                f"Current mode '{current_mode}' does not support night mode"
            )

        try:
            await self.coordinator.async_set_night_mode(False)
        except Exception as err:
            _LOGGER.error("Failed to turn off night mode: %s", err)
            raise HomeAssistantError(f"Failed to turn off night mode: {err}") from err


class PicoLEDStatusSwitch(BaseEntity, SwitchEntity):
    """Representation of a Pico LED Status Switch."""

    _attr_translation_key = "led_status"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the switch."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_led_status_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "LED Status"

    @property
    def is_on(self) -> bool | None:
        """Return True if LED is on."""
        if not self.coordinator.data:
            return None
        # led_on_off_short: 1 = ON, 2 = OFF
        return self.coordinator.data.operating.led_on_off_short == 1

    async def async_turn_on(self, **kwargs) -> None:
        """Turn LED on."""
        try:
            await self.coordinator.async_set_led_status(True)
        except Exception as err:
            _LOGGER.error("Failed to turn on LED: %s", err)
            raise HomeAssistantError(f"Failed to turn on LED: {err}") from err

    async def async_turn_off(self, **kwargs) -> None:
        """Turn LED off."""
        try:
            await self.coordinator.async_set_led_status(False)
        except Exception as err:
            _LOGGER.error("Failed to turn off LED: %s", err)
            raise HomeAssistantError(f"Failed to turn off LED: {err}") from err


class PicoSupportsNightModeSwitch(BaseEntity, SwitchEntity):
    """Diagnostic switch showing if current mode supports night mode."""

    _attr_translation_key = "supports_night_mode"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the switch."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_supports_night_mode_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "Supports Night Mode"

    @property
    def is_on(self) -> bool | None:
        """Return True if current mode supports night mode."""
        return self.coordinator.supports_night_mode

    async def async_turn_on(self, **kwargs) -> None:
        """This is a read-only diagnostic switch."""
        raise HomeAssistantError("This is a diagnostic switch and cannot be controlled")

    async def async_turn_off(self, **kwargs) -> None:
        """This is a read-only diagnostic switch."""
        raise HomeAssistantError("This is a diagnostic switch and cannot be controlled")


class PicoSupportsTargetHumiditySwitch(BaseEntity, SwitchEntity):
    """Diagnostic switch showing if current mode supports target humidity."""

    _attr_translation_key = "supports_target_humidity"
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: MainCoordinator, device_index: int):
        """Initialize the switch."""
        super().__init__(coordinator, device_index)

        self._attr_unique_id = f"{DOMAIN}_supports_target_humidity_{coordinator.pico_ip.replace('.', '_')}"
        self._attr_name = "Supports Target Humidity"

    @property
    def is_on(self) -> bool | None:
        """Return True if current mode supports target humidity."""
        return self.coordinator.supports_target_humidity

    async def async_turn_on(self, **kwargs) -> None:
        """This is a read-only diagnostic switch."""
        raise HomeAssistantError("This is a diagnostic switch and cannot be controlled")

    async def async_turn_off(self, **kwargs) -> None:
        """This is a read-only diagnostic switch."""
        raise HomeAssistantError("This is a diagnostic switch and cannot be controlled")