"""Select setup for our Integration."""
import json
import logging

from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_PIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .utils.device_commands import get_set_target_humidity_command
from . import MyConfigEntry
from .base import BaseEntity
from .coordinator import MainCoordinator
from .const import TARGET_HUMIDITY_OPTIONS, REVERSED_TARGET_HUMIDITY_OPTIONS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Selects."""

    coordinator: MainCoordinator = config_entry.runtime_data.coordinator
    device_pin = config_entry.data.get(CONF_PIN)

    # Define the select types for FAN devices
    select_types = [
        # Mode selection dropdown
        "target_humidity",
    ]

    # Create selects
    selects = [
        Select(coordinator, device, select_type, device_pin)
        for device in coordinator.data
        if device.get("device_type") == "FAN"
        for select_type in select_types
    ]

    # Create the selects.
    async_add_entities(selects)


class Select(BaseEntity, SelectEntity):
    """Representation of a Select."""

    def __init__(self, coordinator, device, parameter, pin: str):
        super().__init__(coordinator, device, parameter)
        self.pin = pin

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        key = self.device.get("target_humidity")
        return TARGET_HUMIDITY_OPTIONS.get(key)

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return list(TARGET_HUMIDITY_OPTIONS.values())

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        # Ensure that the current mode supports target humidity control
        if self.device.get("selected_mode_supports_target_humidity_control") == "OFF":
            raise HomeAssistantError(
                translation_domain="open_pico",
                translation_key="errors.target_humidity_not_supported_in_current_mode",
            )

        # Execute the set humidity target command
        device_name = self.device.get("device_name")
        device_serial = self.device.get("device_uid")
        device_pin = self.pin

        humidity_target_int = REVERSED_TARGET_HUMIDITY_OPTIONS.get(option)

        command_to_send = get_set_target_humidity_command(humidity_target_int, device_pin)
        command_to_send_dumped = json.dumps(command_to_send)

        await self.hass.async_add_executor_job(
            self.coordinator.api.execute_command, device_name, device_serial, device_pin, command_to_send_dumped
        )

        await self.coordinator.async_refresh()