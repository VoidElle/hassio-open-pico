"""Fan setup for our Integration."""

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import PRESET_MODES
from . import MyConfigEntry
from .base import ExampleBaseEntity
from .coordinator import ExampleCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Fans."""
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: ExampleCoordinator = config_entry.runtime_data.coordinator

    # ----------------------------------------------------------------------------
    # Here we are going to add our fan entity for the fan in our mock data.
    # ----------------------------------------------------------------------------

    # Fans
    fans = [
        ExampleFan(coordinator, device, "state")
        for device in coordinator.data
        if device.get("device_type") == "FAN"
    ]

    # Create the fans.
    async_add_entities(fans)


class ExampleFan(ExampleBaseEntity, FanEntity):
    """Implementation of a simple on/off fan with custom 'Mode' category."""

    _attr_supported_features = (
        FanEntityFeature.TURN_ON |
        FanEntityFeature.TURN_OFF |
        FanEntityFeature.PRESET_MODE
    )
    _attr_speed_count = 1  # Required for basic fan functionality

    _mode_parameter = "mode"  # The device API parameter for mode

    # Define available modes
    _attr_preset_modes = PRESET_MODES

    @property
    def is_on(self) -> bool | None:
        return (
            self.coordinator.get_device_parameter(self.device_id, self.parameter)
            == "ON"
        )

    @property
    def preset_mode(self) -> str | None:
        """Return the current mode."""
        mode = self.coordinator.get_device_parameter(self.device_id, self._mode_parameter)
        return mode if mode in self.preset_modes else None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set a new mode."""
        if preset_mode not in self.preset_modes:
            raise ValueError(f"Invalid mode: {preset_mode}")

        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data,
            self.device_id,
            self._mode_parameter,
            preset_mode,
        )
        await self.coordinator.async_refresh()

    async def async_turn_on(self, percentage: int | None = None, preset_mode: str | None = None, **kwargs):
        """Turn on the fan."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data, self.device_id, self.parameter, "ON"
        )

        # If a preset mode is specified, set it
        if preset_mode and preset_mode in self.preset_modes:
            await self.hass.async_add_executor_job(
                self.coordinator.api.set_data,
                self.device_id,
                self._mode_parameter,
                preset_mode,
            )

        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_data, self.device_id, self.parameter, "OFF"
        )
        await self.coordinator.async_refresh()