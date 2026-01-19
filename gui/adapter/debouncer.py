"""Debouncing for rapid slider updates."""

import asyncio
from typing import Any, Callable, Coroutine


class Debouncer:
    """
    Debounces rapid parameter updates to prevent MIDI message flooding.

    When multiple updates for the same parameter arrive within the delay window,
    only the most recent value is sent. This is essential for slider controls
    that can generate many updates per second during drag operations.
    """

    def __init__(self, delay_ms: float = 50.0):
        """
        Initialize debouncer.

        Args:
            delay_ms: Debounce delay in milliseconds.
        """
        self._delay = delay_ms / 1000.0  # Convert to seconds
        self._pending: dict[str, tuple[Any, asyncio.Task]] = {}
        self._callbacks: dict[str, Callable[..., Coroutine]] = {}

    def register(self, key: str, callback: Callable[..., Coroutine]):
        """Register a callback for a parameter key.

        Args:
            key: Unique identifier for the parameter (e.g., 'emitter.1.volume')
            callback: Async function to call with the debounced value
        """
        self._callbacks[key] = callback

    def unregister(self, key: str):
        """Unregister a callback."""
        self._callbacks.pop(key, None)
        # Cancel any pending task
        if key in self._pending:
            _, task = self._pending[key]
            task.cancel()
            del self._pending[key]

    async def _execute_after_delay(self, key: str, value: Any):
        """Wait for delay then execute callback with the value."""
        try:
            await asyncio.sleep(self._delay)
            callback = self._callbacks.get(key)
            if callback:
                await callback(value)
        except asyncio.CancelledError:
            pass
        finally:
            if key in self._pending:
                del self._pending[key]

    def update(self, key: str, value: Any):
        """Schedule a debounced update.

        If called multiple times within the delay window, only the
        last value will be sent when the delay expires.

        Args:
            key: Parameter key (must be registered)
            value: Value to send
        """
        if key not in self._callbacks:
            return

        # Cancel existing pending task for this key
        if key in self._pending:
            _, old_task = self._pending[key]
            old_task.cancel()

        # Schedule new task
        task = asyncio.create_task(self._execute_after_delay(key, value))
        self._pending[key] = (value, task)

    def update_immediate(self, key: str, value: Any):
        """Execute update immediately without debouncing.

        Useful for final values when slider is released.

        Args:
            key: Parameter key (must be registered)
            value: Value to send
        """
        if key not in self._callbacks:
            return

        # Cancel any pending task
        if key in self._pending:
            _, old_task = self._pending[key]
            old_task.cancel()
            del self._pending[key]

        # Execute immediately
        callback = self._callbacks[key]
        asyncio.create_task(callback(value))

    async def flush(self):
        """Execute all pending updates immediately."""
        for key, (value, task) in list(self._pending.items()):
            task.cancel()
            callback = self._callbacks.get(key)
            if callback:
                await callback(value)
        self._pending.clear()

    def cancel_all(self):
        """Cancel all pending updates without executing them."""
        for _, task in self._pending.values():
            task.cancel()
        self._pending.clear()

    @property
    def pending_count(self) -> int:
        """Number of pending updates."""
        return len(self._pending)
