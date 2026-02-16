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

    def set_modulator_selected(self, modulator_num: int):
        """Set selected modulator (1-10)."""
        self._record_call('set_modulator_selected', modulator_num)
        self.state.set_modulator_selected(modulator_num)

    def set_modulator_size(self, value: int, immediate: bool = False):
        """Set modulator size."""
        self._record_call('set_modulator_size', value, immediate=immediate)
        self.state.set_modulator_size(value)

    # Sequencer methods
    def set_sequencer_mode(self, mode: str):
        """Set sequencer mode."""
        self._record_call('set_sequencer_mode', mode)
        self.state.set_sequencer_mode(mode)

    def set_sequencer_bpm(self, bpm: int):
        """Set sequencer BPM."""
        self._record_call('set_sequencer_bpm', bpm)
        self.state.set_sequencer_bpm(bpm)

    async def start_sequencer(self, loops: int = 0):
        """Mock start sequencer."""
        self._record_call('start_sequencer', loops=loops)

    async def stop_sequencer(self):
        """Mock stop sequencer."""
        self._record_call('stop_sequencer')

    async def play_note(self, emitter_nums=None, note=60, velocity=127, duration=0.5):
        """Mock play note."""
        self._record_call('play_note', emitter_nums=emitter_nums, note=note,
                          velocity=velocity, duration=duration)

    async def transport_start(self):
        """Mock transport start."""
        self._record_call('transport_start')

    async def transport_stop(self):
        """Mock transport stop."""
        self._record_call('transport_stop')

    def set_column_pattern_cell(self, column, cell, active, emitter):
        """Set column pattern cell."""
        self._record_call('set_column_pattern_cell', column, cell, active, emitter)
        if active:
            self.state.set_column_pattern_cell(column, cell, emitter)
        else:
            self.state.set_column_pattern_cell(column, cell, None)

    def set_grid_pattern_cell(self, step_index, active, emitter):
        """Set grid pattern cell."""
        self._record_call('set_grid_pattern_cell', step_index, active, emitter)
        if active:
            self.state.set_grid_pattern_cell(step_index, emitter)
        else:
            self.state.set_grid_pattern_cell(step_index, None)

    async def update_running_column_pattern(self, column):
        """Mock update running column pattern."""
        self._record_call('update_running_column_pattern', column)

    async def update_running_grid_pattern(self):
        """Mock update running grid pattern."""
        self._record_call('update_running_grid_pattern')

    async def remove_from_cell(self, column, cell):
        """Mock remove from cell."""
        self._record_call('remove_from_cell', column, cell)
        self.state.remove_from_cell(column, cell)

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

    # Canvas methods
    def save_canvas(self, name, grid_mode):
        """Mock save canvas."""
        self._record_call('save_canvas', name, grid_mode)
        from gui.canvas_manager import save_canvas
        state_dict = self.state.serialize_state()
        metadata = {'grid_mode': grid_mode}
        return save_canvas(name, state_dict, metadata)

    async def load_canvas(self, name):
        """Mock load canvas."""
        self._record_call('load_canvas', name)
        from gui.canvas_manager import load_canvas
        state_dict, metadata = load_canvas(name)
        self.state._push_undo()
        self.state._state = StateManager.deserialize_state(state_dict)
        self.state._notify('*', self.state._state)
        return metadata

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
