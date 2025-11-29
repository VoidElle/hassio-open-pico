import asyncio
import json
from typing import Dict, Callable, Any


class PicoProtocol(asyncio.DatagramProtocol):
    """Internal protocol for handling UDP datagrams"""

    def __init__(self, response_queue: asyncio.Queue, event_callbacks: Dict[str, Callable], verbose: bool):
        self.response_queue = response_queue
        self.event_callbacks = event_callbacks
        self.verbose = verbose
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        try:
            response = json.loads(data.decode('utf-8'))
            if self.verbose:
                print(f"← RECV: {response.get('res', response.get('cmd', 'unknown'))}")

            # Put response in queue (async-safe)
            asyncio.create_task(self.response_queue.put((response, addr)))

            # Trigger event callbacks
            cmd = response.get('cmd', '')
            if cmd in self.event_callbacks:
                asyncio.create_task(self._run_callback(cmd, response))

        except json.JSONDecodeError as e:
            if self.verbose:
                print(f"⚠ JSON decode error: {e}")

    async def _run_callback(self, cmd: str, response: Dict[str, Any]):
        """Run callback in async context"""
        try:
            callback = self.event_callbacks[cmd]
            if asyncio.iscoroutinefunction(callback):
                await callback(response)
            else:
                callback(response)
        except Exception as e:
            if self.verbose:
                print(f"⚠ Callback error for {cmd}: {e}")

    def error_received(self, exc):
        if self.verbose:
            print(f"⚠ Protocol error: {exc}")

    def connection_lost(self, exc):
        if self.verbose and exc:
            print(f"⚠ Connection lost: {exc}")