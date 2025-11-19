"""Shared socket manager for multiple Pico devices."""
import asyncio
import logging

from .open_pico_local_api.pico_client import PicoClient
from .open_pico_local_api.utils.pico_protocol import PicoProtocol

_LOGGER = logging.getLogger(__name__)


class PicoClientManager:
    """Manages shared UDP socket for multiple Pico devices."""

    _instance = None
    _transport = None
    _protocol = None
    _response_queue = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """Initialize shared UDP socket."""
        if self._transport is not None:
            return

        loop = asyncio.get_running_loop()
        self._response_queue = asyncio.Queue()

        self._transport, self._protocol = await loop.create_datagram_endpoint(
            lambda: PicoProtocol(self._response_queue, {}, False),
            local_addr=("0.0.0.0", 40069)
        )
        _LOGGER.debug("Initialized shared UDP socket on port 40069")

    def create_client(self, ip: str, pin: str) -> PicoClient:
        """Create a PicoClient that uses the shared socket."""
        if self._transport is None:
            raise RuntimeError("Manager not initialized")

        # Create client with shared transport
        client = PicoClient(
            ip=ip,
            pin=pin,
            device_port=40070,
            local_port=40069,
            timeout=15,
            retry_attempts=3,
            retry_delay=2.0,
            verbose=True,
            auto_reconnect=True,
            max_reconnect_attempts=3,
            reconnect_delay=2.0,
            shared_transport=self._transport,
            shared_protocol=self._protocol,
        )

        # Override response queue to use shared one
        client._response_queue = self._response_queue

        _LOGGER.debug("Created client for device %s", ip)
        return client

    async def shutdown(self):
        """Shutdown manager."""
        if self._transport:
            self._transport.close()
            self._transport = None
        self._response_queue = None
        self._protocol = None
        _LOGGER.debug("Shutdown complete")