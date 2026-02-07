"""
Modified PicoClient that uses shared transport for multiple devices
"""

import logging
import asyncio
import json
import time
from typing import Optional, Dict, Any, Union

from .enums.device_mode_enum import DeviceModeEnum
from .enums.target_humidity_enum import TargetHumidityEnum
from .exceptions.not_supported_error import NotSupportedError
from .exceptions.pico_device_error import PicoDeviceError
from .models.command_response_model import CommandResponseModel
from .models.pico_device_model import PicoDeviceModel
from .shared_transport_manager import SharedTransportManager
from .utils.constants import HUMIDITY_SELECTOR_PRESET_MODES, MODULAR_FAN_SPEED_PRESET_MODES

_LOGGER = logging.getLogger(__name__)
__version__ = "2.1.0"

class PicoClient:
    """
    Pico device client using shared UDP transport.

    Multiple instances can coexist without port conflicts by sharing
    a single UDP socket and routing responses via IDP ranges.
    """

    def __init__(
            self,
            ip: str,
            pin: str,
            device_id: Optional[str] = None,
            device_port: int = 40070,
            local_port: int = 40069,
            timeout: float = 5,
            retry_attempts: int = 3,
            retry_delay: float = 2.0,
            verbose: bool = False,
            use_shared_transport: bool = True
    ):
        self.ip = ip
        self.pin = pin
        self.device_port = device_port
        self.local_port = local_port
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.verbose = verbose
        self.use_shared_transport = use_shared_transport

        # Generate device_id if not provided
        self.device_id = device_id or f"{ip}:{device_port}"

        # Shared transport
        self._transport_manager = None

        # IDP management
        self._idp_counter = 1
        self._idp_range_start = 1
        self._idp_range_size = 10000

        self._response_queue = asyncio.Queue()
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

    async def reset_idp(self) -> None:
        """
        Manually reset IDP counter to start of range.

        Useful when device communication is stuck due to IDP mismatch.
        This can happen if the device was restarted or lost power.
        """
        await self._reset_idp_counter()
        if self.verbose:
            _LOGGER.debug(f"✓ [{self.device_id}] IDP counter manually reset")

    async def connect(self) -> None:
        """
        Connect to the Pico device

        If use_shared_transport is True, registers with SharedTransportManager.
        Otherwise, creates a dedicated socket (legacy mode).
        """
        if self._connected:
            return

        try:
            if self.use_shared_transport:
                # Get shared transport manager
                self._transport_manager = await SharedTransportManager.get_instance()

                # Initialize if needed
                if not self._transport_manager.is_initialized:
                    await self._transport_manager.initialize(
                        local_port=self.local_port,
                        verbose=self.verbose
                    )

                # Register this device
                self._idp_range_start, self._idp_range_size = await self._transport_manager.register_device(
                    device_id=self.device_id,
                    ip=self.ip,
                    port=self.device_port,
                    response_queue=self._response_queue,
                    event_callbacks=self._event_callbacks
                )

                # Reset IDP counter to start of range
                self._idp_counter = self._idp_range_start

                if self.verbose:
                    _LOGGER.debug(f"✓ Connected '{self.device_id}' to {self.ip}:{self.device_port} (shared transport)")
                    _LOGGER.debug(f"  IDP range: {self._idp_range_start} - {self._idp_range_start + self._idp_range_size - 1}")

            else:
                # Legacy mode: dedicated socket (not recommended for multiple devices)
                raise NotImplementedError("Legacy mode not implemented in this version. Use shared transport.")

            self._connected = True

        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the Pico"""
        if not self._connected:
            return

        if self.use_shared_transport and self._transport_manager:
            await self._transport_manager.unregister_device(self.device_id)

        self._connected = False

        if self.verbose:
            _LOGGER.debug(f"✓ Disconnected '{self.device_id}'")

    # ----------------------------
    # PUBLIC API METHODS
    # ----------------------------

    async def get_status(self, retry: bool = True) -> PicoDeviceModel:
        """Get device status"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        cmd = {
            "cmd": "stato_sync",
            "frm": "app",
            "pin": self.pin
        }

        response = await self._execute_command_with_retry(cmd, retry)
        if not response:
            raise TimeoutError("Failed to get device status")

        try:
            return PicoDeviceModel.from_dict(response)
        except Exception as e:
            raise PicoDeviceError(f"Failed to parse device status: {e}")

    async def turn_on(self, retry: bool = True) -> CommandResponseModel:
        """Turn the device on"""
        return await self._set_on_off(True, retry)

    async def turn_off(self, retry: bool = True) -> CommandResponseModel:
        """Turn the device off"""
        return await self._set_on_off(False, retry)

    async def change_operating_mode(self, mode: Union[DeviceModeEnum, int], retry: bool = True) -> CommandResponseModel:
        """Change the device operating mode"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        mode_value = int(mode)

        cmd = {
            "mod": mode_value,
            "on_off": 1,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        result = await self._execute_command_with_retry(cmd, retry)
        return CommandResponseModel.from_dict(result)

    async def change_fan_speed(self, percentage: int, retry: bool = True, force=False) -> CommandResponseModel:
        """Change the fan speed"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        if not force:
            current_status = await self.get_status(retry=retry)
            if current_status.operating.mode not in MODULAR_FAN_SPEED_PRESET_MODES and percentage != 100:
                raise NotSupportedError(
                    f"Current mode {current_status.operating.mode} does not support fan speed control! {percentage}")

        cmd = {
            "spd_row": percentage,
            "speed": 0,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        result = await self._execute_command_with_retry(cmd, retry)
        return CommandResponseModel.from_dict(result)

    async def set_night_mode(self, enable: bool, retry: bool = True, force=False) -> CommandResponseModel:
        """Set night mode"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

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

        result = await self._execute_command_with_retry(cmd, retry)
        return CommandResponseModel.from_dict(result)

    async def set_led_status(self, enable: bool, retry: bool = True) -> CommandResponseModel:
        """Set LED status"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        cmd = {
            "led_on_off_breve": 1 if enable else 2,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        result = await self._execute_command_with_retry(cmd, retry)
        return CommandResponseModel.from_dict(result)

    async def set_target_humidity(self, target_humidity: TargetHumidityEnum, retry: bool = True,
                                  force=False) -> CommandResponseModel:
        """Set target humidity"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        if not force:
            current_status = await self.get_status(retry=retry)
            if current_status.operating.mode not in HUMIDITY_SELECTOR_PRESET_MODES:
                raise NotSupportedError(
                    f"Current mode {current_status.operating.mode} does not support target humidity selection!")

        cmd = {
            "s_umd": target_humidity,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        result = await self._execute_command_with_retry(cmd, retry)
        return CommandResponseModel.from_dict(result)

    async def reset_maintenance(self, retry: bool = True) -> CommandResponseModel:
        """
        Reset maintenance mode on the device.

        Clears the filter maintenance flag (index 0) by sending a reset command
        for that specific unit.
        """
        if not self._connected:
            raise ConnectionError("Not connected to device")

        # Get current status to get existing maintenance array
        current_status = await self.get_status(retry=retry)
        man_status = current_status.device_info.maintenance

        # If maintenance status is not available, we cannot proceed with reset
        if not man_status or len(man_status) == 0:
            raise PicoDeviceError("Maintenance status not available in device info")

        # Build man_reset: set to 1 for units that need reset
        # We only want to reset index 0 (filter maintenance)
        man_reset = [0] * len(man_status)
        if man_status[0] == 1:
            man_reset[0] = 1

        if self.verbose:
            _LOGGER.debug(f"→ [{self.device_id}] Resetting filter maintenance")
            _LOGGER.debug(f"  Current man: {man_status}")
            _LOGGER.debug(f"  Sending man_reset: {man_reset}")

        cmd = {
            "man_reset": man_reset,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        result = await self._execute_command_with_retry(cmd, retry)
        return CommandResponseModel.from_dict(result)

    # ----------------------------
    # INTERNAL METHODS
    # ----------------------------

    async def _get_next_idp(self) -> int:
        """Get next IDP within allocated range"""
        async with self._lock:
            idp = self._idp_counter
            self._idp_counter += 1

            # Wrap around within allocated range
            if self._idp_counter >= (self._idp_range_start + self._idp_range_size):
                self._idp_counter = self._idp_range_start

            return idp

    async def _reset_idp_counter(self) -> None:
        """Reset IDP counter to start of allocated range"""
        async with self._lock:
            old_counter = self._idp_counter
            self._idp_counter = self._idp_range_start
            if self.verbose:
                _LOGGER.debug(f"  ✓ [{self.device_id}] IDP counter reset: {old_counter} → {self._idp_counter}")

    async def _send_udp_packet(self, cmd: Dict[str, Any]) -> bool:
        """Send a raw UDP packet to the device"""
        try:
            data = json.dumps(cmd).encode('utf-8')

            if self.use_shared_transport:
                await self._transport_manager.send_to_device(self.device_id, data)
            else:
                raise NotImplementedError("Legacy mode not supported")

            if self.verbose:
                cmd_name = cmd.get('cmd', 'ACK' if cmd.get('res') == 99 else 'unknown')
                _LOGGER.debug(f"→ [{self.device_id}] SENT: {cmd_name} (idp:{cmd['idp']})")

            return True

        except Exception as e:
            if self.verbose:
                _LOGGER.debug(f"✗ [{self.device_id}] Send error: {e}")
            raise

    async def _execute_command_with_retry(
            self,
            cmd_dict: Dict[str, Any],
            retry: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Execute a command with IDP sync retry logic"""
        max_attempts = self.retry_attempts if retry else 1
        max_idp_sync = 5

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                if self.verbose:
                    _LOGGER.debug(f"↻ [{self.device_id}] Retry {attempt}/{max_attempts}")
                await asyncio.sleep(self.retry_delay)

            for idp_sync_attempt in range(max_idp_sync):
                if idp_sync_attempt > 0 and self.verbose:
                    _LOGGER.debug(f"  ↻ [{self.device_id}] IDP sync attempt {idp_sync_attempt}/{max_idp_sync}")

                idp = await self._get_next_idp()
                cmd = {**cmd_dict, "idp": idp}

                if not await self._send_udp_packet(cmd):
                    continue

                response_timeout = 2.0
                response = await self._wait_for_response(idp, response_timeout)

                if response:
                    if idp_sync_attempt > 0 and self.verbose:
                        _LOGGER.debug(f"  ✓ [{self.device_id}] IDP synchronized after {idp_sync_attempt} increments")
                    return response

                # If no response after 3 seconds, IDP is likely out of sync
                if self.verbose:
                    _LOGGER.debug(f"  ⚠ [{self.device_id}] No response for IDP {idp} - likely out of sync")

            # After all IDP sync attempts failed, reset IDP counter
            if attempt < max_attempts:
                if self.verbose:
                    _LOGGER.debug(f"  ⟲ [{self.device_id}] Resetting IDP counter to range start")
                await self._reset_idp_counter()

        return None

    async def _wait_for_response(self, idp: int, timeout: float) -> Optional[Dict[str, Any]]:
        """Wait for responses matching the given idp"""
        got_ack = False
        end_time = time.time() + timeout
        ack_timeout = 2.0
        ack_received_time = None

        while time.time() < end_time:
            remaining = end_time - time.time()
            if remaining <= 0:
                break

            if got_ack and ack_received_time:
                if time.time() - ack_received_time > ack_timeout:
                    if self.verbose:
                        _LOGGER.debug(f"  ⚠ [{self.device_id}] ACK received but no status - IDP may be out of sync")
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
                        _LOGGER.debug(f"  ✓ [{self.device_id}] ACK received (idp:{idp})")
                    got_ack = True
                    ack_received_time = time.time()

                elif response.get("res") != 99:
                    if self.verbose:
                        _LOGGER.debug(f"  ✓ [{self.device_id}] Response received (idp:{idp})")

                    ack = {"idp": idp, "frm": "app", "res": 99}
                    await self._send_udp_packet(ack)
                    return response

            except asyncio.TimeoutError:
                continue

        return None

    async def _set_on_off(self, turn_on: bool, retry: bool = True) -> CommandResponseModel:
        """Turn the device on or off"""
        if not self._connected:
            raise ConnectionError("Not connected to device")

        cmd = {
            "on_off": 1 if turn_on else 2,
            "cmd": "upd_pico",
            "frm": "app",
            "pin": self.pin
        }

        result = await self._execute_command_with_retry(cmd, retry)
        return CommandResponseModel.from_dict(result)