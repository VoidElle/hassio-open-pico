"""Fan setup for our Integration."""
import json
import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.const import CONF_PIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .utils.parsers import parse_device_mode_from_preset_to_int
from .utils.device_commands import get_on_off_command, get_change_mode_command, get_change_speed_command
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

    coordinator: ExampleCoordinator = config_entry.runtime_data.coordinator
    device_pin = config_entry.data.get(CONF_PIN)

    # Fans
    fans = [
        Fan(coordinator, device, "state", device_pin)
        for device in coordinator.data
        if device.get("device_type") == "FAN"
    ]

    # Create the fans.
    async_add_entities(fans)


class Fan(ExampleBaseEntity, FanEntity):

    def __init__(self, coordinator, device, parameter, pin: str):
        super().__init__(coordinator, device, parameter)
        self.pin = pin

    _attr_supported_features = (
        FanEntityFeature.TURN_ON |
        FanEntityFeature.TURN_OFF |
        FanEntityFeature.PRESET_MODE |
        FanEntityFeature.SET_SPEED
    )

    # The device API parameter for mode
    _mode_parameter = "mode"

    # Define available preset modes
    _attr_preset_modes = PRESET_MODES

    # The device API parameter for speed
    _attr_speed_count = 100
    _attr_percentage_step = 1

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

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""

        raw_speed = self.coordinator.get_device_parameter(self.device_id, "speed")
        if raw_speed is None:
            return None

        return int(raw_speed * 100 / self._attr_speed_count)

    # Function that will be called when a percentage is set to the device
    async def async_set_percentage(self, percentage: int) -> None:

        """Set speed based on percentage slider."""
        if percentage == 0:
            await self.async_turn_off()
            return

        # We turn on the device if it is currently off
        if self.device.get("state") == "OFF":
            await self.async_turn_on()

        # Execute the set percentage command
        device_name = self.device.get("device_name")
        device_serial = self.device.get("device_uid")
        device_pin = self.pin

        command_to_send = get_change_speed_command(percentage, device_pin)
        command_to_send_dumped = json.dumps(command_to_send)

        await self.hass.async_add_executor_job(
            self.coordinator.api.execute_command, device_name, device_serial, device_pin, command_to_send_dumped
        )

        self.device["speed"] = percentage

        await self.coordinator.async_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set a new mode."""

        if preset_mode not in self.preset_modes:
            raise ValueError(f"Invalid mode: {preset_mode}")

        device_name = self.device.get("device_name")
        device_serial = self.device.get("device_uid")
        device_pin = self.pin

        parsed_preset_mode_to_int = parse_device_mode_from_preset_to_int(preset_mode)
        command_preset_mode_to_send = get_change_mode_command(parsed_preset_mode_to_int, device_pin)
        command_preset_mode_to_send_dumped = json.dumps(command_preset_mode_to_send)

        await self.hass.async_add_executor_job(
            self.coordinator.api.execute_command, device_name, device_serial, device_pin, command_preset_mode_to_send_dumped
        )

        await self.coordinator.async_refresh()

    # Function that will be called when the device is TURNED ON
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

            parsed_preset_mode_to_int = parse_device_mode_from_preset_to_int(preset_mode)
            command_preset_mode_to_send = get_change_mode_command(parsed_preset_mode_to_int, device_pin)
            command_preset_mode_to_send_dumped = json.dumps(command_preset_mode_to_send)

            await self.hass.async_add_executor_job(
                self.coordinator.api.execute_command, device_name, device_serial, device_pin, command_preset_mode_to_send_dumped
            )

        await self.coordinator.async_refresh()

    # Function that will be called when the device is TURNED OFF
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