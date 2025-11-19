"""
Open Pico Local API

A Python library for controlling Tecnosystemi Pico IoT devices via UDP communication
using asyncio for asynchronous operations.
"""

import asyncio
import json
import time
from typing import Optional, Dict, Any, Union

from .enums.device_mode_enum import DeviceModeEnum
from .enums.target_humidity_enum import TargetHumidityEnum
from .exceptions.not_supported_error import NotSupportedError
from .exceptions.pico_device_error import PicoDeviceError
from .exceptions.connection_error import ConnectionError
from .exceptions.timeout_error import TimeoutError

from .models.pico_device_model import PicoDeviceModel
from .utils.auto_reconnect import auto_reconnect
from .utils.constants import HUMIDITY_SELECTOR_PRESET_MODES, MODULAR_FAN_SPEED_PRESET_MODES
from .utils.pico_protocol import PicoProtocol

__version__ = "2.0.0"
__all__ = ['PicoClient', 'PicoDeviceError', 'ConnectionError', 'TimeoutError']


class PicoClient:

    def __init__(
            self,
            ip: str,
            pin: str,
            device_port: int = 40070,
            local_port: int = 40069,
            timeout: float = 15,
            retry_attempts: int = 3,
            retry_delay: float = 2.0,
            verbose: bool = False,
            auto_reconnect: bool = False,
            max_reconnect_attempts: int = 3,
            reconnect_delay: float = 2.0
    ):
        self.ip = ip
        self.pin = pin
        self.device_port = device_port
        self.local_port = local_port
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.verbose = verbose

        # Auto-reconnect settings
        self._auto_reconnect = auto_reconnect
        self._max_reconnect_attempts = max_reconnect_attempts
        self._reconnect_delay = reconnect_delay

        self._transport = None
        self._protocol = None
        self._idp_counter = 1
        self._response_queue = asyncio.Queue()
        self._running = False
        self._listen_task = None
        self._lock = asyncio.Lock()
        self._connected = False
        self._event_callbacks = {}

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        return False

    @property
    def connected(self) -> bool:
        """Check if device is connected"""
        return self._connected

    def get_auto_reconnect(self) -> bool:
        """Check if auto-reconnect is enabled"""
        return self._auto_reconnect

    def set_auto_reconnect(self, value: bool):
        """Enable or disable auto-reconnect"""
        self._auto_reconnect = value
        if self.verbose:
            status = "enabled" if value else "disabled"
            print(f"Auto-reconnect {status}")

    async def connect(self) -> None:
        """
        Connect to the Pico

        Raises:
            ConnectionError: If connection fails
        """
        if self._connected:
            return

        try:
            # Using asyncio.get_running_loop() for Home Assistant compatibility
            loop = asyncio.get_running_loop()

            # Create UDP endpoint
            self._transport, self._protocol = await loop.create_datagram_endpoint(
                lambda: PicoProtocol(self._response_queue, self._event_callbacks, self.verbose),
                local_addr=("0.0.0.0", self.local_port)
            )

            self._running = True
            self._connected = True

            if self.verbose:
                print(f"✓ Connected to {self.ip}:{self.device_port}")
                if self._auto_reconnect:
                    print(f"  Auto-reconnect: enabled (max {self._max_reconnect_attempts} attempts)")

        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the Pico"""
        self._running = False

        if self._transport:
            self._transport.close()

        self._connected = False

        if self.verbose:
            print("✓ Disconnected")

    # ----------------------------
    # PUBLIC API METHODS
    # ----------------------------

    @auto_reconnect
    async def get_status(self, retry: bool = True) -> Optional[PicoDeviceModel]:
        """
        Get device status (with auto-reconnect if enabled)

        Args:
            retry: Whether to retry on failure

        Returns:
            PicoDeviceModel instance or None if failed

        Raises:
            ConnectionError: If not connected and when auto-reconnect fails
            TimeoutError: If operation times out
        """
        if not self._connected:
            raise ConnectionError("Not connected to device")

        cmd = {
            "cmd": "stato_sync",
            "frm": "app",
            "pin": self.pin
        }

        response = await self._execute_command_with_retry(cmd, retry)
        if not response:
            return None

        try:
            return PicoDeviceModel.from_dict(response)
        except Exception as e:
            if self.verbose:
                print(f"⚠ Failed to parse PicoDeviceModel: {e}")
            return None

    @auto_reconnect
    async def turn_on(self, retry: bool = True) -> Optional[Dict[str, Any]]:
        """Turn the device on"""
        return await self._set_on_off(True, retry)

    @auto_reconnect
    async def turn_off(self, retry: bool = True) -> Optional[Dict[str, Any]]:
        """Turn the device off"""
        return await self._set_on_off(False, retry)

    @auto_reconnect
    async def change_operating_mode(self, mode: Union[DeviceModeEnum, int], retry: bool = True) -> Optional[Dict[str, Any]]:
        """Change the device operating mode"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        # Convert enum to int if needed
        mode_value = int(mode)

        cmd = {
            "mod": mode_value,
            "on_off": 1,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        return await self._execute_command_with_retry(cmd, retry)

    @auto_reconnect
    async def change_fan_speed(self, percentage: int, retry: bool = True, force=False) -> Optional[Dict[str, Any]]:
        """Change the fan speed"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        # Check if current mode supports fan speed control
        # Force option can be used to skip this check
        if not force:
            current_status = await self.get_status(retry=retry)
            if current_status.operating.mode not in MODULAR_FAN_SPEED_PRESET_MODES:
                raise NotSupportedError(f"Current mode {current_status.operating.mode} does not support fan speed control!")

        cmd = {
            "spd_row": percentage,
            "speed": 0,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        return await self._execute_command_with_retry(cmd, retry)

    @auto_reconnect
    async def set_night_mode(self, enable: bool, retry: bool = True, force=False) -> Optional[Dict[str, Any]]:
        """Set night mode"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        # Check if current mode supports night mode
        # Force option can be used to skip this check
        if not force:
            current_status = await self.get_status(retry=retry)
            if current_status.operating.mode not in MODULAR_FAN_SPEED_PRESET_MODES:
                raise NotSupportedError(f"Current mode {current_status.operating.mode} does not support night mode!")

        cmd = {
            "night_mod": 1 if enable else 2,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        return await self._execute_command_with_retry(cmd, retry)

    @auto_reconnect
    async def set_led_status(self, enable: bool, retry: bool = True) -> Optional[Dict[str, Any]]:
        """Set LED status"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        cmd = {
            "led_on_off_breve": 1 if enable else 2,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        return await self._execute_command_with_retry(cmd, retry)

    @auto_reconnect
    async def set_target_humidity(self, target_humidity: TargetHumidityEnum, retry: bool = True, force=False) -> Optional[Dict[str, Any]]:
        """Set target humidity"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        # Check if current mode supports target humidity selection
        # Force option can be used to skip this check
        if not force:
            current_status = await self.get_status(retry=retry)
            if current_status.operating.mode not in HUMIDITY_SELECTOR_PRESET_MODES:
                raise NotSupportedError(f"Current mode {current_status.operating.mode} does not support target humidity selection!")

        cmd = {
            "s_umd": target_humidity,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        return await self._execute_command_with_retry(cmd, retry)

    # ----------------------------
    # INTERNAL METHODS
    # ----------------------------

    async def _get_next_idp(self) -> int:
        """Thread-safe IDP counter increment"""
        async with self._lock:
            idp = self._idp_counter
            self._idp_counter += 1
            return idp

    async def _send_udp_packet(self, cmd: Dict[str, Any]) -> bool:
        """
        Send a raw UDP packet to the device (internal method - no auto-reconnect)

        This is the low-level method that actually sends data over the socket.
        """
        try:
            data = json.dumps(cmd).encode('utf-8')
            self._transport.sendto(data, (self.ip, self.device_port))
            if self.verbose:
                cmd_name = cmd.get('cmd', 'ACK' if cmd.get('res') == 99 else 'unknown')
                print(f"→ SENT: {cmd_name} (idp:{cmd['idp']})")
            return True
        except Exception as e:
            if self.verbose:
                print(f"✗ Send error: {e}")
            raise  # Re-raise to trigger auto-reconnect at higher level

    async def _execute_command_with_retry(
            self,
            cmd_dict: Dict[str, Any],
            retry: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a command with IDP sync retry logic

        Args:
            cmd_dict: Command dictionary (without idp, will be added)
            retry: Whether to retry on failure

        Returns:
            Device response or None if failed
        """
        max_attempts = self.retry_attempts if retry else 1
        max_idp_sync = 10

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                if self.verbose:
                    print(f"↻ Retry {attempt}/{max_attempts}")
                await asyncio.sleep(self.retry_delay)

            for idp_sync_attempt in range(max_idp_sync):
                if idp_sync_attempt > 0 and self.verbose:
                    print(f"  ↻ IDP sync attempt {idp_sync_attempt}/{max_idp_sync}")
                    await asyncio.sleep(0.5)

                idp = await self._get_next_idp()
                cmd = {**cmd_dict, "idp": idp}

                if not await self._send_udp_packet(cmd):
                    continue

                response = await self._wait_for_response(idp, self.timeout)

                if response:
                    if idp_sync_attempt > 0 and self.verbose:
                        print(f"  ✓ IDP synchronized after {idp_sync_attempt} increments")
                    return response

        return None

    async def _wait_for_response(self, idp: int, timeout: float) -> Optional[Dict[str, Any]]:
        """Wait for responses matching the given idp"""
        got_ack = False
        end_time = time.time() + timeout
        ack_timeout = 3.0
        ack_received_time = None

        while time.time() < end_time:
            remaining = end_time - time.time()
            if remaining <= 0:
                break

            if got_ack and ack_received_time:
                if time.time() - ack_received_time > ack_timeout:
                    if self.verbose:
                        print(f"  ⚠ ACK received but no status - IDP may be out of sync")
                    return None

            try:
                response, addr = await asyncio.wait_for(
                    self._response_queue.get(),
                    timeout=min(remaining, 0.5)
                )

                if response.get("idp") != idp:
                    continue

                if response.get("res") == 99 and response.get("frm") == "mst":
                    if self.verbose:
                        print(f"  ✓ ACK received (idp:{idp})")
                    got_ack = True
                    ack_received_time = time.time()

                elif response.get("res") != 99:
                    if self.verbose:
                        print(f"  ✓ Response received (idp:{idp})")

                    ack = {"idp": idp, "frm": "app", "res": 99}
                    await self._send_udp_packet(ack)
                    return response

            except asyncio.TimeoutError:
                continue

        return None

    async def _set_on_off(self, turn_on: bool, retry: bool = True) -> Optional[Dict[str, Any]]:
        """
        Turn the device on or off (internal implementation)

        Args:
            turn_on: True to turn on, False to turn off
            retry: Whether to retry on failure

        Returns:
            Device response or None if failed

        Raises:
            ConnectionError: If not connected
        """
        if not self._connected:
            raise ConnectionError("Not connected to device")

        cmd = {
            "on_off": 1 if turn_on else 2,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        return await self._execute_command_with_retry(cmd, retry)

