"""Fan setup for our Integration."""
import json
import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.const import CONF_PIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .utils.device_commands import get_on_off_command
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
    device_pin = config_entry.data.get(CONF_PIN)

    # ----------------------------------------------------------------------------
    # Here we are going to add our fan entity for the fan in our mock data.
    # ----------------------------------------------------------------------------

    # Fans
    fans = [
        ExampleFan(coordinator, device, "state", device_pin)
        for device in coordinator.data
        if device.get("device_type") == "FAN"
    ]

    # Create the fans.
    async_add_entities(fans)


class ExampleFan(ExampleBaseEntity, FanEntity):
    """Implementation of a simple on/off fan with custom 'Mode' category."""

    def __init__(self, coordinator, device, parameter, pin: str):
        super().__init__(coordinator, device, parameter)
        self.pin = pin

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

        device_name = self.device.get("device_name")
        device_serial = self.device.get("device_uid")
        device_pin = self.pin

        command_to_send_to_parse = get_on_off_command(True, device_pin)
        command_to_send_parsed = json.dumps(command_to_send_to_parse)

        await self.hass.async_add_executor_job(
            self.coordinator.api.execute_command, device_name, device_serial, device_pin, command_to_send_parsed
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

        device_name = self.device.get("device_name")
        device_serial = self.device.get("device_uid")
        device_pin = self.pin

        command_to_send_to_parse = get_on_off_command(False, device_pin)
        command_to_send_parsed = json.dumps(command_to_send_to_parse)

        await self.hass.async_add_executor_job(
            self.coordinator.api.execute_command, device_name, device_serial, device_pin, command_to_send_parsed
        )

        await self.coordinator.async_refresh()