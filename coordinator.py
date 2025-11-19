"""DataUpdateCoordinator for Open Pico integration."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .open_pico_local_api.pico_client import PicoClient
from .open_pico_local_api.models.pico_device_model import PicoDeviceModel
from .open_pico_local_api.enums.device_mode_enum import DeviceModeEnum

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MainCoordinator(DataUpdateCoordinator):
    """The main coordinator for Open Pico devices."""

    data: PicoDeviceModel | None

    def __init__(self, hass: HomeAssistant, client: PicoClient) -> None:
        """Initialize coordinator."""
        self.client = client
        self.pico_ip = client.ip

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({client.ip})",
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def async_update_data(self) -> PicoDeviceModel:
        """Fetch data from device."""
        try:
            _LOGGER.debug("Starting data update for device %s", self.pico_ip)

            if not self.client.connected:
                _LOGGER.debug("Connecting to device %s...", self.pico_ip)
                await self.client.connect()

            status = await self.client.get_status()

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
        """Shutdown the coordinator."""
        # Client disconnect is handled by manager
        pass

    # Helper properties
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
        await self.client.turn_on(retry=True)
        await self.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the device off."""
        await self.client.turn_off(retry=True)
        await self.async_request_refresh()

    async def async_set_mode(self, mode: DeviceModeEnum | int) -> None:
        """Set operating mode."""
        await self.client.change_operating_mode(mode, retry=True)
        await self.async_request_refresh()

    async def async_set_fan_speed(self, percentage: int) -> None:
        """Set fan speed percentage."""
        await self.client.change_fan_speed(percentage, retry=True)
        await self.async_request_refresh()

    async def async_set_night_mode(self, enable: bool) -> None:
        """Set night mode."""
        await self.client.set_night_mode(enable, retry=True)
        await self.async_request_refresh()

    async def async_set_led_status(self, enable: bool) -> None:
        """Set LED status."""
        await self.client.set_led_status(enable, retry=True)
        await self.async_request_refresh()

    async def async_set_target_humidity(self, target: int) -> None:
        """Set target humidity."""
        await self.client.set_target_humidity(target, retry=True)
        await self.async_request_refresh()