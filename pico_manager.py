"""Shared PicoClient manager for multiple devices."""
import logging
from typing import Dict

from .open_pico_local_api.pico_client import PicoClient

_LOGGER = logging.getLogger(__name__)


class PicoClientManager:
    """Manages a single PicoClient instance shared across all devices."""

    _instance = None
    _client: PicoClient | None = None
    _devices: Dict[str, str] = {}  # ip -> pin mapping

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def add_device(self, ip: str, pin: str) -> None:
        """Add a device to be managed."""
        self._devices[ip] = pin

        # Initialize the client on first device
        if self._client is None:
            _LOGGER.debug("Initializing shared PicoClient on port 40069")
            # Use the first device's config to initialize
            self._client = PicoClient(
                ip=ip,  # This will be overridden per request
                pin=pin,
                device_port=40070,
                local_port=40069,  # Shared port for all devices
                timeout=15,
                retry_attempts=3,
                retry_delay=2.0,
                verbose=True,
                auto_reconnect=True,
                max_reconnect_attempts=3,
                reconnect_delay=2.0
            )
            await self._client.connect()
            _LOGGER.debug("Shared PicoClient connected")

    async def get_status(self, ip: str):
        """Get status for a specific device."""
        if self._client is None:
            raise RuntimeError("PicoClient not initialized")

        # Update client IP and PIN for this request
        self._client.ip = ip
        self._client.pin = self._devices.get(ip, "")

        return await self._client.get_status(retry=True)

    async def send_command(self, ip: str, command_method, *args, **kwargs):
        """Send a command to a specific device."""
        if self._client is None:
            raise RuntimeError("PicoClient not initialized")

        # Update client IP and PIN for this request
        self._client.ip = ip
        self._client.pin = self._devices.get(ip, "")

        return await command_method(*args, **kwargs)

    async def shutdown(self) -> None:
        """Shutdown the shared client."""
        if self._client and self._client.connected:
            await self._client.disconnect()
            _LOGGER.debug("Shared PicoClient disconnected")
        self._client = None
        self._devices.clear()

    @property
    def connected(self) -> bool:
        """Check if client is connected."""
        return self._client is not None and self._client.connected