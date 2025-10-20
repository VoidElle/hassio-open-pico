"""Switch setup for our Integration."""
import json
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_PIN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .utils.device_commands import get_set_night_mode_command, get_set_led_status_command
from .const import MODULAR_FAN_SPEED_PRESET_MODES
from . import MyConfigEntry
from .base import BaseEntity
from .coordinator import MainCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Switches."""

    coordinator: MainCoordinator = config_entry.runtime_data.coordinator
    device_pin = config_entry.data.get(CONF_PIN)

    # Define the switch types for FAN devices
    switch_types = [

        # Night mode switch
        "night_mode",

        # Switch to indicate if the currently selected mode supports night mode
        "selected_mode_supports_night_mode",

        # Switch to indicate if the currently selected mode supports target humidity control
        "selected_mode_supports_target_humidity_control",

        # LED status switch
        "led_status",
    ]

    # Create switches
    switches = [
        Switch(coordinator, device, switch_type, device_pin)
        for device in coordinator.data
        if device.get("device_type") == "FAN"
        for switch_type in switch_types
    ]

    # Create the switches.
    async_add_entities(switches)


class Switch(BaseEntity, SwitchEntity):
    """Representation of a Switch."""

    def __init__(self, coordinator, device, parameter, pin: str):
        super().__init__(coordinator, device, parameter)
        self.pin = pin

    @property
    def is_on(self) -> bool | None:
        """Return True if switch is on."""
        valid_parameters = [
            "night_mode",
            "led_status",
            "selected_mode_supports_night_mode",
            "selected_mode_supports_target_humidity_control",
        ]

        if self.parameter in valid_parameters:
            return self.device.get(self.parameter) == "ON"

        return None

    def handle_toggle_night_mode(self, new_status: bool) -> str | None:
        """Toggle the night mode."""

        # Return None if the current mode does not support night mode
        current_mode = self.device.get("mode")
        if current_mode not in MODULAR_FAN_SPEED_PRESET_MODES:
            return None

        device_pin = self.pin

        command_to_send = get_set_night_mode_command(new_status, device_pin)
        return json.dumps(command_to_send)

    def handle_toggle_led_status(self, new_status: bool) -> str:
        """Toggle the LED status"""
        device_pin = self.pin
        command_to_send = get_set_led_status_command(new_status, device_pin)
        return json.dumps(command_to_send)


    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""

        # Handle night mode turning ON
        if self.parameter == "night_mode":
            toggle_night_mode_cmd_nullable: str | None = self.handle_toggle_night_mode(True)
            if toggle_night_mode_cmd_nullable is None:
                current_mode = self.device.get("mode")
                raise HomeAssistantError(
                    translation_domain="open_pico",
                    translation_key="errors.unsupported_mode",
                    translation_placeholders={"mode": current_mode},
                )
            else:
                cmd_to_execute = toggle_night_mode_cmd_nullable

        # Handle LED status turning ON
        else:
            cmd_to_execute = self.handle_toggle_led_status(True)

        # Execute the command
        device_name = self.device.get("device_name")
        device_serial = self.device.get("device_uid")
        device_pin = self.pin

        await self.hass.async_add_executor_job(
            self.coordinator.api.execute_command, device_name, device_serial, device_pin, cmd_to_execute
        )

        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""

        # Handle night mode turning OFF
        if self.parameter == "night_mode":
            toggle_night_mode_cmd_nullable: str | None = self.handle_toggle_night_mode(False)
            if toggle_night_mode_cmd_nullable is None:
                current_mode = self.device.get("mode")
                raise HomeAssistantError(
                    translation_domain="open_pico",
                    translation_key="errors.unsupported_mode",
                    translation_placeholders={"mode": current_mode},
                )
            else:
                cmd_to_execute = toggle_night_mode_cmd_nullable

        # Handle LED status turning OFF
        else:
            cmd_to_execute = self.handle_toggle_led_status(False)

        # Execute the command
        device_name = self.device.get("device_name")
        device_serial = self.device.get("device_uid")
        device_pin = self.pin

        await self.hass.async_add_executor_job(
            self.coordinator.api.execute_command, device_name, device_serial, device_pin, cmd_to_execute
        )

        await self.coordinator.async_refresh()