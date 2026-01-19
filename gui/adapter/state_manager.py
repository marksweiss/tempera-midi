"""State management for Tempera GUI with undo/redo and preset support."""

import copy
import json
from pathlib import Path
from typing import Any, Callable, Optional


def _default_emitter_state() -> dict:
    """Default state for a single emitter."""
    return {
        'volume': 100,
        'octave': 64,
        'effects_send': 0,
        'grain_length_cell': 64,
        'grain_length_note': 64,
        'grain_density': 64,
        'grain_shape': 64,
        'grain_shape_attack': 64,
        'grain_pan': 64,
        'grain_tune_spread': 64,
        'relative_x': 64,
        'relative_y': 64,
        'spray_x': 0,
        'spray_y': 0,
        'tone_filter_width': 127,
        'tone_filter_center': 64,
    }


def _default_track_state() -> dict:
    """Default state for a single track."""
    return {'volume': 100}


def _default_global_state() -> dict:
    """Default state for global parameters."""
    return {
        'modwheel': 0,
        'adsr': {
            'attack': 0,
            'decay': 0,
            'sustain': 127,
            'release': 64,
        },
        'reverb': {
            'size': 64,
            'color': 64,
            'mix': 0,
        },
        'delay': {
            'feedback': 64,
            'time': 64,
            'color': 64,
            'mix': 0,
        },
        'chorus': {
            'depth': 64,
            'speed': 64,
            'flange': 64,
            'mix': 0,
        },
    }


def _default_state() -> dict:
    """Create a fresh default state."""
    return {
        'emitters': {i: _default_emitter_state() for i in range(1, 5)},
        'tracks': {i: _default_track_state() for i in range(1, 9)},
        'global': _default_global_state(),
        'cells': {},  # (column, cell) -> emitter_num
        'active_emitter': 1,
    }


class StateManager:
    """
    Manages shadow state for the Tempera GUI.

    Since the Tempera hardware cannot be queried for its current state,
    the GUI maintains its own state as the source of truth.

    Features:
    - Shadow state tracking for all parameters
    - Undo/redo with configurable history depth
    - Preset save/load to JSON files
    """

    MAX_HISTORY = 50

    def __init__(self):
        self._state = _default_state()
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []
        self._listeners: list[Callable[[str, Any], None]] = []

    @property
    def state(self) -> dict:
        """Current state (read-only copy)."""
        return copy.deepcopy(self._state)

    def add_listener(self, callback: Callable[[str, Any], None]):
        """Add a listener that is called when state changes.

        Callback receives (path, new_value) where path is like
        'emitters.1.volume' or 'cells.(1,2)'.
        """
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[str, Any], None]):
        """Remove a state change listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self, path: str, value: Any):
        """Notify listeners of a state change."""
        for listener in self._listeners:
            listener(path, value)

    def _push_undo(self):
        """Save current state to undo stack."""
        self._undo_stack.append(copy.deepcopy(self._state))
        if len(self._undo_stack) > self.MAX_HISTORY:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> bool:
        """Restore previous state. Returns True if undo was possible."""
        if not self._undo_stack:
            return False
        self._redo_stack.append(copy.deepcopy(self._state))
        self._state = self._undo_stack.pop()
        self._notify('*', self._state)
        return True

    def redo(self) -> bool:
        """Restore undone state. Returns True if redo was possible."""
        if not self._redo_stack:
            return False
        self._undo_stack.append(copy.deepcopy(self._state))
        self._state = self._redo_stack.pop()
        self._notify('*', self._state)
        return True

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    # --- Emitter state ---

    def get_emitter_param(self, emitter_num: int, param: str) -> int:
        """Get an emitter parameter value."""
        return self._state['emitters'][emitter_num][param]

    def set_emitter_param(self, emitter_num: int, param: str, value: int,
                          record_undo: bool = True):
        """Set an emitter parameter value."""
        if record_undo:
            self._push_undo()
        self._state['emitters'][emitter_num][param] = value
        self._notify(f'emitters.{emitter_num}.{param}', value)

    def get_active_emitter(self) -> int:
        """Get the currently active emitter number."""
        return self._state['active_emitter']

    def set_active_emitter(self, emitter_num: int, record_undo: bool = True):
        """Set the active emitter."""
        if record_undo:
            self._push_undo()
        self._state['active_emitter'] = emitter_num
        self._notify('active_emitter', emitter_num)

    # --- Track state ---

    def get_track_volume(self, track_num: int) -> int:
        """Get a track's volume."""
        return self._state['tracks'][track_num]['volume']

    def set_track_volume(self, track_num: int, value: int, record_undo: bool = True):
        """Set a track's volume."""
        if record_undo:
            self._push_undo()
        self._state['tracks'][track_num]['volume'] = value
        self._notify(f'tracks.{track_num}.volume', value)

    # --- Global state ---

    def get_global_param(self, category: str, param: Optional[str] = None) -> Any:
        """Get a global parameter.

        For modwheel, use get_global_param('modwheel').
        For effects, use get_global_param('reverb', 'mix').
        """
        if param is None:
            return self._state['global'][category]
        return self._state['global'][category][param]

    def set_global_param(self, category: str, param: Optional[str], value: int,
                         record_undo: bool = True):
        """Set a global parameter.

        For modwheel, use set_global_param('modwheel', None, value).
        For effects, use set_global_param('reverb', 'mix', value).
        """
        if record_undo:
            self._push_undo()
        if param is None:
            self._state['global'][category] = value
            self._notify(f'global.{category}', value)
        else:
            self._state['global'][category][param] = value
            self._notify(f'global.{category}.{param}', value)

    # --- Cell state ---

    def get_cell(self, column: int, cell: int) -> Optional[int]:
        """Get the emitter placed in a cell, or None if empty."""
        return self._state['cells'].get((column, cell))

    def place_in_cell(self, emitter_num: int, column: int, cell: int,
                      record_undo: bool = True):
        """Place an emitter in a cell."""
        if record_undo:
            self._push_undo()
        self._state['cells'][(column, cell)] = emitter_num
        self._notify(f'cells.({column},{cell})', emitter_num)

    def remove_from_cell(self, column: int, cell: int, record_undo: bool = True):
        """Remove any emitter from a cell."""
        key = (column, cell)
        if key in self._state['cells']:
            if record_undo:
                self._push_undo()
            del self._state['cells'][key]
            self._notify(f'cells.({column},{cell})', None)

    def get_all_cells(self) -> dict[tuple[int, int], int]:
        """Get all cell placements."""
        return dict(self._state['cells'])

    def clear_all_cells(self, record_undo: bool = True):
        """Remove all emitter placements."""
        if self._state['cells']:
            if record_undo:
                self._push_undo()
            self._state['cells'] = {}
            self._notify('cells', {})

    # --- Preset management ---

    def save_preset(self, filepath: Path):
        """Save current state to a JSON file."""
        # Convert tuple keys to strings for JSON
        state_copy = copy.deepcopy(self._state)
        state_copy['cells'] = {
            f'{col},{cell}': emitter
            for (col, cell), emitter in self._state['cells'].items()
        }
        with open(filepath, 'w') as f:
            json.dump(state_copy, f, indent=2)

    def load_preset(self, filepath: Path):
        """Load state from a JSON file."""
        self._push_undo()
        with open(filepath, 'r') as f:
            loaded = json.load(f)

        # Convert string keys back to tuples and ints
        cells = {}
        for key, emitter in loaded.get('cells', {}).items():
            col, cell = map(int, key.split(','))
            cells[(col, cell)] = emitter
        loaded['cells'] = cells

        # Convert string keys to ints for emitters and tracks
        loaded['emitters'] = {int(k): v for k, v in loaded['emitters'].items()}
        loaded['tracks'] = {int(k): v for k, v in loaded['tracks'].items()}

        self._state = loaded
        self._notify('*', self._state)

    def reset_to_defaults(self, record_undo: bool = True):
        """Reset all state to defaults."""
        if record_undo:
            self._push_undo()
        self._state = _default_state()
        self._notify('*', self._state)

    def get_snapshot(self) -> dict:
        """Get a snapshot of current state for external use."""
        return copy.deepcopy(self._state)

    def restore_snapshot(self, snapshot: dict, record_undo: bool = True):
        """Restore state from a snapshot."""
        if record_undo:
            self._push_undo()
        self._state = copy.deepcopy(snapshot)
        self._notify('*', self._state)
