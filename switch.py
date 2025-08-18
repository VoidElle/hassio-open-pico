"""Switch setup for our Integration."""
import json
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_PIN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .utils.device_commands import get_set_night_mode_command
from .const import MODULAR_FAN_SPEED_PRESET_MODES
from . import MyConfigEntry
from .base import ExampleBaseEntity
from .coordinator import ExampleCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Switches."""

    coordinator: ExampleCoordinator = config_entry.runtime_data.coordinator
    device_pin = config_entry.data.get(CONF_PIN)

    # Switches
    switches = [
        Switch(coordinator, device, "night_mode", device_pin)
        for device in coordinator.data
        if device.get("device_type") == "FAN"
    ]

    # Create the switches.
    async_add_entities(switches)


class Switch(ExampleBaseEntity, SwitchEntity):
    """Representation of a Switch."""

    def __init__(self, coordinator, device, parameter, pin: str):
        super().__init__(coordinator, device, parameter)
        self.pin = pin

    @property
    def is_on(self) -> bool | None:
        """Return True if switch is on."""
        return (
            self.device.get("night_mode") == "ON"
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""

        # Make only toggle the night mode in presets that support it
        current_mode = self.device.get("mode")
        if current_mode not in MODULAR_FAN_SPEED_PRESET_MODES:
            raise HomeAssistantError(
                f"Cannot set night mode: current mode '{current_mode}' does not support night mode control"
            )

        # Execute the set night mode ON
        device_name = self.device.get("device_name")
        device_serial = self.device.get("device_uid")
        device_pin = self.pin

        command_to_send = get_set_night_mode_command(True, device_pin)
        command_to_send_dumped = json.dumps(command_to_send)

        await self.hass.async_add_executor_job(
            self.coordinator.api.execute_command, device_name, device_serial, device_pin, command_to_send_dumped
        )

        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""

        # Make only toggle the night mode in presets that support it
        current_mode = self.device.get("mode")
        if current_mode not in MODULAR_FAN_SPEED_PRESET_MODES:
            raise HomeAssistantError(
                f"Cannot set night mode: current mode '{current_mode}' does not support night mode control"
            )

        # Execute the set night mode OFF
        device_name = self.device.get("device_name")
        device_serial = self.device.get("device_uid")
        device_pin = self.pin

        command_to_send = get_set_night_mode_command(False, device_pin)
        command_to_send_dumped = json.dumps(command_to_send)

        await self.hass.async_add_executor_job(
            self.coordinator.api.execute_command, device_name, device_serial, device_pin, command_to_send_dumped
        )

        await self.coordinator.async_refresh()