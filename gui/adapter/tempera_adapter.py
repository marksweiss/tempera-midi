"""Main adapter between GUI and Tempera library."""

import asyncio
import os
from pathlib import Path
from typing import Callable, Optional

import mido

from tempera import Emitter, EmitterPool, TemperaGlobal, Track
from sequencer import ColumnSequencer, GridSequencer
from gui.adapter.state_manager import StateManager
from gui.adapter.debouncer import Debouncer
from gui.envelope.envelope_manager import EnvelopeManager


class TemperaAdapter:
    """
    Main coordinator between GUI and Tempera library.

    Provides:
    - Connection management (connect/disconnect)
    - Debounced parameter updates
    - Shadow state tracking
    - Undo/redo support
    - Preset management
    """

    def __init__(self, debounce_ms: float = 50.0):
        """
        Initialize the adapter.

        Args:
            debounce_ms: Debounce delay for slider updates in milliseconds.
        """
        self._pool: Optional[EmitterPool] = None
        self._tempera_global: Optional[TemperaGlobal] = None
        self._tracks: dict[int, Track] = {}
        self._emitters_local: dict[int, Emitter] = {}
        self._output: Optional[mido.ports.BaseOutput] = None
        self._connected = False
        self._port_name: Optional[str] = None

        self.state = StateManager()
        self._debouncer = Debouncer(debounce_ms)

        # Sequencer instances
        self._column_sequencer: Optional[ColumnSequencer] = None
        self._grid_sequencer: Optional[GridSequencer] = None
        self._sequencer_task: Optional[asyncio.Task] = None

        # Envelope manager for automation
        self._envelope_manager = EnvelopeManager(bpm=120)
        self._envelope_manager.set_tick_callback(self._on_envelope_tick)

        # Track last sent values to avoid redundant MIDI messages
        self._last_sent_values: dict[str, int] = {}

        # Callback for envelope position updates (for UI playhead)
        self._envelope_position_callback: Optional[Callable[[float], None]] = None

        # Feedback callback for status updates
        self._status_callback: Optional[Callable[[str], None]] = None

        # Setup debouncer callbacks
        self._setup_debouncer()

    def _setup_debouncer(self):
        """Register all parameter callbacks with the debouncer."""
        # Emitter parameters
        for e in range(1, 5):
            for param in ['volume', 'octave', 'effects_send',
                          'grain_length_cell', 'grain_length_note', 'grain_density',
                          'grain_shape', 'grain_shape_attack', 'grain_pan', 'grain_tune_spread',
                          'relative_x', 'relative_y', 'spray_x', 'spray_y',
                          'tone_filter_width', 'tone_filter_center']:
                key = f'emitter.{e}.{param}'
                self._debouncer.register(key, self._make_emitter_callback(e, param))

        # Track volumes
        for t in range(1, 9):
            key = f'track.{t}.volume'
            self._debouncer.register(key, self._make_track_callback(t))

        # Global parameters
        self._debouncer.register('global.modulator.size', self._send_modulator_size)

        for param in ['attack', 'decay', 'sustain', 'release']:
            key = f'global.adsr.{param}'
            self._debouncer.register(key, self._make_global_callback('adsr', param))

        for param in ['size', 'color', 'mix']:
            key = f'global.reverb.{param}'
            self._debouncer.register(key, self._make_global_callback('reverb', param))

        for param in ['feedback', 'time', 'color', 'mix']:
            key = f'global.delay.{param}'
            self._debouncer.register(key, self._make_global_callback('delay', param))

        for param in ['depth', 'speed', 'flange', 'mix']:
            key = f'global.chorus.{param}'
            self._debouncer.register(key, self._make_global_callback('chorus', param))

    def _make_emitter_callback(self, emitter_num: int, param: str):
        """Create a callback for an emitter parameter."""
        async def callback(value: int):
            await self._send_emitter_param(emitter_num, param, value)
        return callback

    def _make_track_callback(self, track_num: int):
        """Create a callback for a track volume."""
        async def callback(value: int):
            await self._send_track_volume(track_num, value)
        return callback

    def _make_global_callback(self, category: str, param: str):
        """Create a callback for a global parameter."""
        async def callback(value: int):
            await self._send_global_param(category, param, value)
        return callback

    def set_status_callback(self, callback: Callable[[str], None]):
        """Set callback for status updates."""
        self._status_callback = callback

    def _notify_status(self, message: str):
        """Send status update to callback if set."""
        if self._status_callback:
            self._status_callback(message)

    def set_envelope_position_callback(self, callback: Optional[Callable[[float], None]]):
        """Set callback for envelope position updates (for UI playhead).

        The callback receives the current position (0.0 to 1.0).
        """
        self._envelope_position_callback = callback

    @property
    def envelope_manager(self) -> EnvelopeManager:
        """Get the envelope manager instance."""
        return self._envelope_manager

    def _on_envelope_tick(self, position: float):
        """Called on each envelope manager tick to apply envelope modulation.

        Args:
            position: Current position in 8-beat cycle (0.0 to 1.0)
        """
        # Notify UI for playhead
        if self._envelope_position_callback:
            self._envelope_position_callback(position)

        if not self._connected:
            return

        # Get all enabled envelopes
        enabled_envelopes = self.state.get_enabled_envelopes()

        for control_key, envelope in enabled_envelopes.items():
            # Get base value from state
            base_value = self._get_base_value(control_key)
            if base_value is None:
                continue

            # Apply envelope modulation
            modulated_value = self._envelope_manager.apply_envelope_to_value(
                base_value, envelope
            )

            # Only send if value changed
            if self._last_sent_values.get(control_key) != modulated_value:
                self._last_sent_values[control_key] = modulated_value
                asyncio.create_task(self._send_modulated_value(control_key, modulated_value))

    def _get_base_value(self, control_key: str) -> Optional[int]:
        """Get the base value for a control from state.

        Args:
            control_key: Control identifier (e.g., 'emitter.1.volume')

        Returns:
            Base value (0-127) or None if not found
        """
        parts = control_key.split('.')

        if parts[0] == 'emitter' and len(parts) >= 3:
            emitter_num = int(parts[1])
            param = parts[2]
            return self.state.get_emitter_param(emitter_num, param)

        elif parts[0] == 'track' and len(parts) >= 3:
            track_num = int(parts[1])
            return self.state.get_track_volume(track_num)

        elif parts[0] == 'global':
            if len(parts) >= 4 and parts[1] == 'modulator':
                # global.modulator.{N}.size - per-modulator envelope
                # All modulators share the current size value from state
                return self.state.get_modulator_size()
            elif len(parts) >= 3 and parts[1] == 'modulator':
                # Legacy: global.modulator.size (for backward compat)
                return self.state.get_modulator_size()
            elif len(parts) >= 3:
                # global.reverb.mix etc
                return self.state.get_global_param(parts[1], parts[2])

        return None

    async def _send_modulated_value(self, control_key: str, value: int):
        """Send a modulated value to hardware.

        Args:
            control_key: Control identifier
            value: Modulated value (0-127)
        """
        parts = control_key.split('.')

        if parts[0] == 'emitter' and len(parts) >= 3:
            emitter_num = int(parts[1])
            param = parts[2]
            await self._send_emitter_param(emitter_num, param, value)

        elif parts[0] == 'track' and len(parts) >= 3:
            track_num = int(parts[1])
            await self._send_track_volume(track_num, value)

        elif parts[0] == 'global':
            if len(parts) >= 4 and parts[1] == 'modulator':
                # global.modulator.{N}.size - send to specific modulator
                mod_num = int(parts[2])
                await self._send_modulator_size_to(mod_num, value)
            elif len(parts) >= 3 and parts[1] == 'modulator':
                # Legacy: global.modulator.size
                await self._send_modulator_size(value)
            elif len(parts) >= 3:
                await self._send_global_param(parts[1], parts[2], value)

    @staticmethod
    def list_midi_ports() -> list[str]:
        """List available MIDI output ports."""
        return mido.get_output_names()

    @staticmethod
    def find_tempera_port() -> Optional[str]:
        """Find Tempera MIDI port by scanning available ports.

        Returns:
            Port name if found, None otherwise.
        """
        ports = mido.get_output_names()
        for port in ports:
            if 'Tempera' in port:
                return port
        return None

    @property
    def is_connected(self) -> bool:
        """Check if connected to Tempera."""
        return self._connected

    @property
    def port_name(self) -> Optional[str]:
        """Get current MIDI port name."""
        return self._port_name

    async def connect(self, port_name: Optional[str] = None) -> bool:
        """
        Connect to Tempera.

        Args:
            port_name: MIDI port name. Uses TEMPERA_PORT env var if not specified.

        Returns:
            True if connection successful, False otherwise.
        """
        if self._connected:
            await self.disconnect()

        # Priority: explicit arg > env var > auto-detect > default
        if port_name:
            self._port_name = port_name
        elif os.environ.get('TEMPERA_PORT'):
            self._port_name = os.environ.get('TEMPERA_PORT')
        else:
            detected = self.find_tempera_port()
            self._port_name = detected or 'Tempera'

        try:
            # Create EmitterPool
            self._pool = EmitterPool(port_name=self._port_name)
            await self._pool.start()

            # Create global and track controllers with separate MIDI port
            self._output = mido.open_output(self._port_name)
            self._tempera_global = TemperaGlobal(midi_channel=1)
            self._tracks = {i: Track(track=i, midi_channel=1) for i in range(1, 9)}
            self._emitters_local = {i: Emitter(emitter=i, midi_channel=2) for i in range(1, 5)}

            self._connected = True
            self._notify_status(f'Connected: {self._port_name}')
            return True

        except Exception as e:
            self._connected = False
            self._notify_status(f'Connection failed: {e}')
            return False

    async def disconnect(self):
        """Disconnect from Tempera."""
        if self._pool:
            await self._pool.stop()
            self._pool = None

        if self._output:
            self._output.close()
            self._output = None

        self._tempera_global = None
        self._tracks = {}
        self._emitters_local = {}
        self._connected = False
        self._port_name = None
        self._notify_status('Disconnected')

    # --- Emitter controls ---

    async def _send_emitter_param(self, emitter_num: int, param: str, value: int):
        """Internal: send emitter parameter to hardware via direct send."""
        if not self._connected or not self._output:
            return

        try:
            emitter = self._emitters_local[emitter_num]
            msgs = []

            if param == 'volume':
                msgs = [emitter.volume(value)]
            elif param == 'octave':
                msgs = [emitter.octave(value)]
            elif param == 'effects_send':
                msgs = [emitter.effects_send(value)]
            elif param.startswith('grain_'):
                grain_param = param[6:]  # Remove 'grain_' prefix
                msgs = emitter.grain(**{grain_param: value})
            elif param.startswith('relative_'):
                axis = param[-1]  # 'x' or 'y'
                msgs = emitter.relative_position(**{axis: value})
            elif param.startswith('spray_'):
                axis = param[-1]  # 'x' or 'y'
                msgs = emitter.spray(**{axis: value})
            elif param.startswith('tone_filter_'):
                tf_param = param[12:]  # Remove 'tone_filter_' prefix
                msgs = emitter.tone_filter(**{tf_param: value})

            # Send messages directly
            if isinstance(msgs, list):
                for msg in msgs:
                    self._output.send(msg)
            else:
                self._output.send(msgs)

            self._notify_status(f'Emitter {emitter_num} {param} → {value}')
        except Exception as e:
            self._notify_status(f'Error: {e}')

    def set_emitter_param(self, emitter_num: int, param: str, value: int,
                          immediate: bool = False):
        """
        Set an emitter parameter (debounced).

        Args:
            emitter_num: Emitter number (1-4)
            param: Parameter name (e.g., 'volume', 'grain_density')
            value: Parameter value (0-127)
            immediate: If True, bypass debouncing
        """
        # Update state (don't record undo for continuous slider movements)
        self.state.set_emitter_param(emitter_num, param, value, record_undo=immediate)

        # Send to hardware
        key = f'emitter.{emitter_num}.{param}'
        if immediate:
            self._debouncer.update_immediate(key, value)
        else:
            self._debouncer.update(key, value)

    async def set_active_emitter(self, emitter_num: int):
        """Set the active emitter."""
        self.state.set_active_emitter(emitter_num)
        if self._connected and self._output:
            msg = self._emitters_local[emitter_num].set_active()
            self._output.send(msg)
            self._notify_status(f'Active emitter: {emitter_num}')

    # --- Cell controls ---

    async def place_in_cell(self, emitter_num: int, column: int, cell: int):
        """Place an emitter in a cell."""
        self.state.place_in_cell(emitter_num, column, cell)
        if self._connected and self._output:
            msg = self._emitters_local[emitter_num].place_in_cell(column, cell)
            self._output.send(msg)
            self._notify_status(f'Emitter {emitter_num} → cell ({column}, {cell})')

    async def remove_from_cell(self, column: int, cell: int):
        """Remove emitter from a cell."""
        emitter_num = self.state.get_cell(column, cell)
        if emitter_num is not None:
            self.state.remove_from_cell(column, cell)
            if self._connected and self._output:
                msg = self._emitters_local[emitter_num].remove_from_cell(column, cell)
                self._output.send(msg)
                self._notify_status(f'Cleared cell ({column}, {cell})')

    async def toggle_cell(self, column: int, cell: int):
        """Toggle emitter placement in a cell.

        If cell is empty, places active emitter. If cell has an emitter, removes it.
        """
        current = self.state.get_cell(column, cell)
        if current is None:
            active = self.state.get_active_emitter()
            await self.place_in_cell(active, column, cell)
        else:
            await self.remove_from_cell(column, cell)

    # --- Track controls ---

    async def _send_track_volume(self, track_num: int, value: int):
        """Internal: send track volume to hardware."""
        if not self._connected or not self._output:
            return
        try:
            msg = self._tracks[track_num].volume(value)
            self._output.send(msg)
            self._notify_status(f'Track {track_num} volume → {value}')
        except Exception as e:
            self._notify_status(f'Error: {e}')

    def set_track_volume(self, track_num: int, value: int, immediate: bool = False):
        """Set track volume (debounced)."""
        self.state.set_track_volume(track_num, value, record_undo=immediate)
        key = f'track.{track_num}.volume'
        if immediate:
            self._debouncer.update_immediate(key, value)
        else:
            self._debouncer.update(key, value)

    async def track_record_on(self, track_num: int):
        """Arm a track for recording."""
        if self._connected and self._output:
            msg = self._tracks[track_num].record_on()
            self._output.send(msg)
            self._notify_status(f'Track {track_num} armed for recording')

    # --- Global controls ---

    async def _send_modulator_size(self, value: int):
        """Internal: send modulator size to hardware."""
        if not self._connected or not self._output:
            return
        try:
            selected = self.state.get_modulator_selected()
            msg = self._tempera_global.modulator_size(selected, value)
            self._output.send(msg)
            self._notify_status(f'Modulator {selected} Size → {value}')
        except Exception as e:
            self._notify_status(f'Error: {e}')

    async def _send_modulator_size_to(self, modulator_num: int, value: int):
        """Internal: send modulator size to a specific modulator.

        Used by envelope automation to send to the correct modulator CC.

        Args:
            modulator_num: Modulator number (1-10)
            value: Size value (0-127)
        """
        if not self._connected or not self._output:
            return
        try:
            msg = self._tempera_global.modulator_size(modulator_num, value)
            self._output.send(msg)
            self._notify_status(f'Modulator {modulator_num} Size → {value}')
        except Exception as e:
            self._notify_status(f'Error: {e}')

    async def _send_global_param(self, category: str, param: str, value: int):
        """Internal: send global parameter to hardware."""
        if not self._connected or not self._output:
            return
        try:
            method = getattr(self._tempera_global, category)
            msgs = method(**{param: value})
            for msg in msgs:
                self._output.send(msg)
            self._notify_status(f'{category.title()} {param} → {value}')
        except Exception as e:
            self._notify_status(f'Error: {e}')

    def set_global_param(self, category: str, param: Optional[str], value: int,
                         immediate: bool = False):
        """Set a global parameter (debounced).

        For effects: set_global_param('reverb', 'mix', value)
        For modulator: use set_modulator_size() and set_modulator_selected() instead.
        """
        self.state.set_global_param(category, param, value, record_undo=immediate)

        key = f'global.{category}.{param}'

        if immediate:
            self._debouncer.update_immediate(key, value)
        else:
            self._debouncer.update(key, value)

    def set_modulator_size(self, value: int, immediate: bool = False):
        """Set modulator size (debounced)."""
        self.state.set_modulator_size(value, record_undo=immediate)
        key = 'global.modulator.size'
        if immediate:
            self._debouncer.update_immediate(key, value)
        else:
            self._debouncer.update(key, value)

    def set_modulator_selected(self, modulator_num: int):
        """Set selected modulator (1-10). Does not send MIDI, just updates state."""
        self.state.set_modulator_selected(modulator_num)

    # --- Playback ---

    async def play_note(self, emitter_nums: Optional[list[int]] = None,
                        note: int = 60, velocity: int = 127, duration: float = 0.5):
        """Play a note on specified emitters.

        Args:
            emitter_nums: List of emitter numbers (1-4). If None, uses active emitter.
            note: MIDI note number.
            velocity: Note velocity.
            duration: Note duration in seconds.
        """
        if not self._connected or not self._pool:
            return

        if emitter_nums is None:
            emitter_nums = [self.state.get_active_emitter()]

        await self._pool.play_all(emitter_nums, note, velocity, duration)
        self._notify_status(f'Note {note} on emitters {emitter_nums}')

    async def transport_start(self):
        """Send MIDI start message."""
        if self._connected and self._output:
            self._output.send(TemperaGlobal.start())
            self._notify_status('Transport: Start')

    async def transport_stop(self):
        """Send MIDI stop message."""
        if self._connected and self._output:
            self._output.send(TemperaGlobal.stop())
            self._notify_status('Transport: Stop')

    async def change_canvas(self, program: int):
        """Change Tempera canvas via program change."""
        if self._connected and self._output:
            msg = self._tempera_global.change_canvas(program)
            self._output.send(msg)
            self._notify_status(f'Canvas → {program}')

    # --- Undo/Redo ---

    async def undo(self) -> bool:
        """Undo last change and sync to hardware."""
        if self.state.undo():
            await self._sync_all_state()
            self._notify_status('Undo')
            return True
        return False

    async def redo(self) -> bool:
        """Redo undone change and sync to hardware."""
        if self.state.redo():
            await self._sync_all_state()
            self._notify_status('Redo')
            return True
        return False

    async def _sync_all_state(self):
        """Sync all state to hardware after undo/redo/preset load."""
        if not self._connected:
            return

        state = self.state.state

        # Sync emitter parameters
        for emitter_num, params in state['emitters'].items():
            for param, value in params.items():
                await self._send_emitter_param(emitter_num, param, value)

        # Sync track volumes
        for track_num, params in state['tracks'].items():
            await self._send_track_volume(track_num, params['volume'])

        # Sync global parameters (modulator size)
        await self._send_modulator_size(state['global']['modulator']['size'])
        for param, value in state['global']['adsr'].items():
            await self._send_global_param('adsr', param, value)
        for param, value in state['global']['reverb'].items():
            await self._send_global_param('reverb', param, value)
        for param, value in state['global']['delay'].items():
            await self._send_global_param('delay', param, value)
        for param, value in state['global']['chorus'].items():
            await self._send_global_param('chorus', param, value)

        # Sync cells - this is trickier as we need to clear old and set new
        # For now, just set all current placements
        for (col, cell), emitter_num in state['cells'].items():
            if self._output and emitter_num in self._emitters_local:
                msg = self._emitters_local[emitter_num].place_in_cell(col, cell)
                self._output.send(msg)

    # --- Preset management ---

    def save_preset(self, filepath: Path):
        """Save current state to a preset file."""
        self.state.save_preset(filepath)
        self._notify_status(f'Preset saved: {filepath.name}')

    async def load_preset(self, filepath: Path):
        """Load state from a preset file and sync to hardware."""
        self.state.load_preset(filepath)
        await self._sync_all_state()
        self._notify_status(f'Preset loaded: {filepath.name}')

    async def reset_to_defaults(self):
        """Reset all parameters to defaults and sync to hardware."""
        self.state.reset_to_defaults()
        await self._sync_all_state()
        self._notify_status('Reset to defaults')

    # --- Sequencer controls ---

    def _ensure_sequencers(self):
        """Create sequencer instances if pool is available."""
        if self._pool and not self._column_sequencer:
            bpm = self.state.get_sequencer_bpm()
            self._column_sequencer = ColumnSequencer(self._pool, bpm=bpm)
            self._grid_sequencer = GridSequencer(self._pool, bpm=bpm)

    def set_sequencer_mode(self, mode: str):
        """Set sequencer mode ('column' or 'grid')."""
        self.state.set_sequencer_mode(mode)
        self._notify_status(f'Sequencer mode: {mode}')

    def set_sequencer_bpm(self, bpm: int):
        """Set sequencer BPM."""
        self.state.set_sequencer_bpm(bpm)
        if self._column_sequencer:
            self._column_sequencer.set_bpm(bpm)
        if self._grid_sequencer:
            self._grid_sequencer.set_bpm(bpm)
        # Also update envelope manager BPM
        self._envelope_manager.bpm = bpm
        self._notify_status(f'Sequencer BPM: {bpm}')

    def set_column_pattern_cell(self, column: int, cell: int, active: bool,
                                 emitter_num: int):
        """Set a cell in a column pattern."""
        if active:
            self.state.set_column_pattern_cell(column, cell, emitter_num)
        else:
            self.state.set_column_pattern_cell(column, cell, None)

    def set_grid_pattern_cell(self, step_index: int, active: bool, emitter_num: int):
        """Set a cell in the grid pattern."""
        if active:
            self.state.set_grid_pattern_cell(step_index, emitter_num)
        else:
            self.state.set_grid_pattern_cell(step_index, None)

    def clear_all_patterns(self):
        """Clear all sequencer patterns."""
        self.state.clear_all_patterns()
        self._notify_status('Patterns cleared')

    async def start_sequencer(self, loops: int = 0):
        """Start the sequencer.

        Args:
            loops: Number of loops (0 = infinite).
        """
        if not self._connected or not self._pool:
            self._notify_status('Cannot start sequencer: not connected')
            return

        # Stop any running sequencer first
        await self.stop_sequencer()

        self._ensure_sequencers()
        mode = self.state.get_sequencer_mode()

        if mode == 'column':
            # Load patterns into column sequencer
            for col in range(1, 9):
                pattern = self.state.get_column_pattern(col)
                await self._column_sequencer.set_column_pattern(col, pattern)
            self._sequencer_task = asyncio.create_task(
                self._column_sequencer.run(loops=loops)
            )
        else:
            # Load pattern into grid sequencer
            pattern = self.state.get_grid_pattern()
            await self._grid_sequencer.set_pattern(pattern)
            self._sequencer_task = asyncio.create_task(
                self._grid_sequencer.run(loops=loops)
            )

        self.state.set_sequencer_running(True)

        # Start envelope manager for automation
        self._envelope_manager.bpm = self.state.get_sequencer_bpm()
        self._envelope_manager.start()

        self._notify_status(f'Sequencer started ({mode} mode)')

    async def stop_sequencer(self):
        """Stop the sequencer."""
        if self._column_sequencer:
            await self._column_sequencer.stop()
            await self._column_sequencer.cleanup()
        if self._grid_sequencer:
            await self._grid_sequencer.stop()
            await self._grid_sequencer.cleanup()

        if self._sequencer_task:
            self._sequencer_task.cancel()
            try:
                await self._sequencer_task
            except asyncio.CancelledError:
                pass
            self._sequencer_task = None

        # Stop envelope manager
        await self._envelope_manager.stop()

        # Clear last sent values so next start sends fresh values
        self._last_sent_values.clear()

        self.state.set_sequencer_running(False)
        self._notify_status('Sequencer stopped')

    async def update_running_column_pattern(self, column: int):
        """Update a column pattern on the running sequencer.

        Args:
            column: Column number (1-8) to update
        """
        if (self._column_sequencer
                and self.state.get_sequencer_running()
                and self.state.get_sequencer_mode() == 'column'):
            pattern = self.state.get_column_pattern(column)
            await self._column_sequencer.set_column_pattern(column, pattern)
            self._notify_status(f'Updated column {column} pattern')

    async def update_running_grid_pattern(self):
        """Update the grid pattern on the running sequencer."""
        if (self._grid_sequencer
                and self.state.get_sequencer_running()
                and self.state.get_sequencer_mode() == 'grid'):
            pattern = self.state.get_grid_pattern()
            await self._grid_sequencer.set_pattern(pattern)
            self._notify_status('Updated grid pattern')
