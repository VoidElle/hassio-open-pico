"""DataUpdateCoordinator for Open Pico integration."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .open_pico_local_api.models.pico_device_model import PicoDeviceModel
from .open_pico_local_api.enums.device_mode_enum import DeviceModeEnum

from .pico_manager import PicoClientManager
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MainCoordinator(DataUpdateCoordinator):
    """The main coordinator for Open Pico devices."""

    data: PicoDeviceModel | None

    def __init__(self, hass: HomeAssistant, pico_ip: str, pin: str, manager: PicoClientManager) -> None:
        """Initialize coordinator from YAML config."""

        # Store the pico IP and PIN
        self.pico_ip = pico_ip
        self.pin = pin
        self.manager = manager

        # Initialize DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({pico_ip})",
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def async_update_data(self) -> PicoDeviceModel:
        """Fetch data from API endpoint."""
        try:
            _LOGGER.debug("Starting data update for device %s", self.pico_ip)

            # Get the device status via shared manager
            status = await self.manager.get_status(self.pico_ip)

            if status is None:
                raise UpdateFailed("Failed to get device status")

            _LOGGER.debug(
                "Device %s status: ON=%s, Mode=%s, Temp=%.1f°C, Humidity=%.1f%%",
                self.pico_ip,
                status.is_on,
                status.operating.mode.name,
                status.sensors.temperature,
                status.sensors.humidity
            )

            return status

        except Exception as err:
            _LOGGER.error("Error communicating with device %s: %s", self.pico_ip, err, exc_info=True)
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown is handled by the manager."""
        pass

    # Helper properties for entities
    @property
    def is_on(self) -> bool:
        """Check if device is on."""
        return self.data.is_on if self.data else False

    @property
    def temperature(self) -> float:
        """Get current temperature."""
        return self.data.sensors.temperature if self.data else 0.0

    @property
    def humidity(self) -> float:
        """Get current humidity."""
        return self.data.sensors.humidity if self.data else 0.0

    @property
    def current_mode(self) -> DeviceModeEnum | None:
        """Get current operating mode."""
        return self.data.operating.mode if self.data else None

    @property
    def fan_speed(self) -> int:
        """Get current fan speed percentage."""
        return self.data.operating.speed_row if self.data else 0

    @property
    def night_mode_enabled(self) -> bool:
        """Check if night mode is enabled."""
        return self.data.operating.night_mode == 1 if self.data else False

    @property
    def supports_fan_speed(self) -> bool:
        """Check if device supports fan speed control."""
        return self.data.support_fan_speed_control if self.data else False

    @property
    def supports_night_mode(self) -> bool:
        """Check if device supports night mode."""
        return self.data.support_night_mode_toggle if self.data else False

    @property
    def supports_target_humidity(self) -> bool:
        """Check if device supports target humidity selection."""
        return self.data.support_target_humidity_selection if self.data else False

    # Control methods
    async def async_turn_on(self) -> None:
        """Turn the device on."""
        await self.manager.send_command(
            self.pico_ip,
            self.manager._client.turn_on,
            retry=True
        )
        await self.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the device off."""
        await self.manager.send_command(
            self.pico_ip,
            self.manager._client.turn_off,
            retry=True
        )
        await self.async_request_refresh()

    async def async_set_mode(self, mode: DeviceModeEnum | int) -> None:
        """Set operating mode."""
        await self.manager.send_command(
            self.pico_ip,
            self.manager._client.change_operating_mode,
            mode,
            retry=True
        )
        await self.async_request_refresh()

    async def async_set_fan_speed(self, percentage: int) -> None:
        """Set fan speed percentage."""
        await self.manager.send_command(
            self.pico_ip,
            self.manager._client.change_fan_speed,
            percentage,
            retry=True
        )
        await self.async_request_refresh()

    async def async_set_night_mode(self, enable: bool) -> None:
        """Set night mode."""
        await self.manager.send_command(
            self.pico_ip,
            self.manager._client.set_night_mode,
            enable,
            retry=True
        )
        await self.async_request_refresh()

    async def async_set_led_status(self, enable: bool) -> None:
        """Set LED status."""
        await self.manager.send_command(
            self.pico_ip,
            self.manager._client.set_led_status,
            enable,
            retry=True
        )
        await self.async_request_refresh()

    async def async_set_target_humidity(self, target: int) -> None:
        """Set target humidity."""
        await self.manager.send_command(
            self.pico_ip,
            self.manager._client.set_target_humidity,
            target,
            retry=True
        )
        await self.async_request_refresh()