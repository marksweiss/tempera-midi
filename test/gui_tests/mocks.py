"""Mock classes for GUI testing without hardware dependencies."""

from typing import Any, Callable, Optional
from unittest.mock import MagicMock

from gui.adapter.state_manager import StateManager


class MockTemperaAdapter:
    """Mock adapter that records all method calls without MIDI hardware.

    This mock provides the same interface as TemperaAdapter but without
    any MIDI port connections. All state changes are tracked via the
    StateManager and method calls are recorded for verification.
    """

    def __init__(self):
        self.state = StateManager()
        self.calls: list[tuple[str, tuple, dict]] = []
        self._connected = False
        self._status_callback: Optional[Callable[[str], None]] = None
        self._envelope_position_callback: Optional[Callable[[float], None]] = None

    def set_status_callback(self, callback: Callable[[str], None]):
        """Set status message callback."""
        self._status_callback = callback

    def set_envelope_position_callback(self, callback: Callable[[float], None]):
        """Set envelope position callback."""
        self._envelope_position_callback = callback

    def _record_call(self, method: str, *args, **kwargs):
        """Record a method call for later verification."""
        self.calls.append((method, args, kwargs))

    def _update_status(self, message: str):
        """Update status if callback is set."""
        if self._status_callback:
            self._status_callback(message)

    # Connection methods (no-op for mock)
    async def connect(self, port_name: str = 'Mock') -> bool:
        """Mock connect - always succeeds."""
        self._record_call('connect', port_name)
        self._connected = True
        self._update_status(f'Connected to {port_name}')
        return True

    async def disconnect(self):
        """Mock disconnect."""
        self._record_call('disconnect')
        self._connected = False
        self._update_status('Disconnected')

    @property
    def connected(self) -> bool:
        return self._connected

    # Emitter methods
    def set_emitter_param(self, emitter_num: int, param: str, value: int,
                          immediate: bool = False):
        """Set emitter parameter value."""
        self._record_call('set_emitter_param', emitter_num, param, value,
                          immediate=immediate)
        self.state.set_emitter_param(emitter_num, param, value)

    async def set_active_emitter(self, emitter_num: int):
        """Set active emitter."""
        self._record_call('set_active_emitter', emitter_num)
        self.state.set_active_emitter(emitter_num)

    # Cell methods
    async def toggle_cell(self, column: int, cell: int):
        """Toggle cell state."""
        self._record_call('toggle_cell', column, cell)
        current = self.state.get_cell(column, cell)
        if current is None:
            self.state.place_in_cell(column, cell, self.state.get_active_emitter())
        else:
            self.state.remove_from_cell(column, cell)

    # Track methods
    def set_track_volume(self, track_num: int, value: int, immediate: bool = False):
        """Set track volume."""
        self._record_call('set_track_volume', track_num, value, immediate=immediate)
        self.state.set_track_volume(track_num, value)

    # Global methods
    def set_global_param(self, category: str, param: str, value: int,
                         immediate: bool = False):
        """Set global parameter."""
        self._record_call('set_global_param', category, param, value,
                          immediate=immediate)
        self.state.set_global_param(category, param, value)

    # Undo/redo
    async def undo(self) -> bool:
        """Undo last state change."""
        self._record_call('undo')
        return self.state.undo()

    async def redo(self) -> bool:
        """Redo last undone change."""
        self._record_call('redo')
        return self.state.redo()

    # Preset methods
    def save_preset(self, filepath):
        """Save current state to file."""
        self._record_call('save_preset', filepath)
        self.state.save_preset(filepath)

    async def load_preset(self, filepath):
        """Load state from file."""
        self._record_call('load_preset', filepath)
        self.state.load_preset(filepath)

    async def reset_to_defaults(self):
        """Reset all parameters to defaults."""
        self._record_call('reset_to_defaults')
        # Reset state to initial values
        self.state._state = StateManager()._state.copy()

    # Test helper methods
    def clear_calls(self):
        """Clear recorded method calls."""
        self.calls.clear()

    def get_calls(self, method: str) -> list[tuple[tuple, dict]]:
        """Get all calls to a specific method."""
        return [(args, kwargs) for m, args, kwargs in self.calls if m == method]

    def assert_called(self, method: str, *args, **kwargs):
        """Assert that a method was called with specific arguments."""
        for m, call_args, call_kwargs in self.calls:
            if m == method:
                if args and call_args != args:
                    continue
                if kwargs:
                    matches = all(call_kwargs.get(k) == v for k, v in kwargs.items())
                    if not matches:
                        continue
                return True
        raise AssertionError(
            f"Expected call {method}({args}, {kwargs}) not found. "
            f"Calls: {self.calls}"
        )
