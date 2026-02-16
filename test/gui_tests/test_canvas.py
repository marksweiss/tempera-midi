"""Canvas save/load tests.

Tests for the canvas save and load functionality including:
- StateManager serialize/deserialize refactor
- Canvas file manager operations
- Integration with GUI and adapter
"""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gui.adapter.state_manager import StateManager
from gui.envelope.envelope import Envelope, EnvelopePoint
from gui import canvas_manager
from test.gui_tests.base import GUITestCase


class TestSerializationRefactor(unittest.TestCase):
    """Verify StateManager serialize/deserialize extraction didn't break anything."""

    def test_serialize_roundtrip(self):
        """serialize_state → deserialize_state produces identical state."""
        sm = StateManager()
        # Put some non-default data in
        sm.set_emitter_param(1, 'volume', 80)
        sm.set_track_volume(3, 50)
        sm.set_global_param('reverb', 'mix', 100)
        # place_in_cell(emitter_num, column, cell)
        sm.place_in_cell(1, 2, 3)
        sm.set_column_pattern_cell(1, 5, 2)
        sm.set_grid_pattern_cell(10, 3)

        original = copy.deepcopy(sm._state)
        serialized = sm.serialize_state()
        restored = StateManager.deserialize_state(serialized)

        self.assertEqual(original['emitters'], restored['emitters'])
        self.assertEqual(original['tracks'], restored['tracks'])
        self.assertEqual(original['global'], restored['global'])
        self.assertEqual(original['cells'], restored['cells'])
        self.assertEqual(original['active_emitter'], restored['active_emitter'])
        self.assertEqual(
            original['sequencer']['column_patterns'],
            restored['sequencer']['column_patterns']
        )
        self.assertEqual(
            original['sequencer']['grid_pattern'],
            restored['sequencer']['grid_pattern']
        )

    def test_serialize_envelope_with_metadata(self):
        """Envelope metadata (preset, per_cell) survives serialize/deserialize."""
        sm = StateManager()
        envelope = sm.get_envelope('emitter.1.volume')
        envelope.enabled = True
        envelope.preset = 'TRIANGLE'
        envelope.per_cell = True
        envelope.add_point(0.0, 0.0)
        envelope.add_point(0.5, 1.0)
        envelope.add_point(1.0, 0.0)
        sm.set_envelope('emitter.1.volume', envelope)

        serialized = sm.serialize_state()
        restored = StateManager.deserialize_state(serialized)

        restored_env = restored['envelopes']['emitter.1.volume']
        self.assertEqual(restored_env.preset, 'TRIANGLE')
        self.assertTrue(restored_env.per_cell)
        self.assertTrue(restored_env.enabled)
        self.assertEqual(len(restored_env.points), 3)

    def test_save_preset_still_works(self):
        """Existing save_preset/load_preset work after refactor."""
        sm = StateManager()
        sm.set_emitter_param(2, 'octave', 100)
        sm.set_track_volume(5, 70)
        sm.place_in_cell(1, 1, 1)  # emitter 1, column 1, cell 1

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            filepath = Path(f.name)

        try:
            sm.save_preset(filepath)
            self.assertTrue(filepath.exists())

            # Verify JSON is valid
            with open(filepath) as f:
                data = json.load(f)
            self.assertIn('emitters', data)
            self.assertIn('tracks', data)

            # Load into fresh StateManager
            sm2 = StateManager()
            sm2.load_preset(filepath)
            self.assertEqual(sm2.get_emitter_param(2, 'octave'), 100)
            self.assertEqual(sm2.get_track_volume(5), 70)
            self.assertEqual(sm2.get_cell(1, 1), 1)
        finally:
            filepath.unlink(missing_ok=True)


class TestCanvasManager(unittest.TestCase):
    """Tests for canvas_manager.py file operations."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._tmppath = Path(self._tmpdir.name)
        self._patcher = patch.object(
            canvas_manager, 'get_canvas_directory',
            return_value=self._tmppath
        )
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        self._tmpdir.cleanup()

    def test_save_and_load_roundtrip(self):
        """Save a canvas then load it back."""
        state_dict = {'emitters': {'1': {'volume': 80}}, 'tracks': {}}
        metadata = {'grid_mode': 'column'}
        canvas_manager.save_canvas('test1', state_dict, metadata)

        loaded_state, loaded_meta = canvas_manager.load_canvas('test1')
        self.assertEqual(loaded_state, state_dict)
        self.assertEqual(loaded_meta, metadata)

    def test_list_canvases_sorted(self):
        """list_canvases returns sorted names."""
        for name in ['zebra', 'alpha', 'middle']:
            canvas_manager.save_canvas(name, {}, {})
        result = canvas_manager.list_canvases()
        self.assertEqual(result, ['alpha', 'middle', 'zebra'])

    def test_list_canvases_empty(self):
        """Empty directory returns empty list."""
        self.assertEqual(canvas_manager.list_canvases(), [])

    def test_load_nonexistent_raises(self):
        """Loading non-existent canvas raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            canvas_manager.load_canvas('nonexistent')

    def test_canvas_format_has_version(self):
        """Saved JSON includes version field."""
        canvas_manager.save_canvas('versioned', {'x': 1}, {'grid_mode': 'grid'})
        filepath = self._tmppath / 'versioned.json'
        with open(filepath) as f:
            raw = json.load(f)
        self.assertEqual(raw['version'], 1)
        self.assertIn('state', raw)
        self.assertIn('metadata', raw)

    def test_delete_canvas(self):
        """Delete removes canvas and returns True."""
        canvas_manager.save_canvas('to_delete', {}, {})
        self.assertIn('to_delete', canvas_manager.list_canvases())
        result = canvas_manager.delete_canvas('to_delete')
        self.assertTrue(result)
        self.assertNotIn('to_delete', canvas_manager.list_canvases())

    def test_delete_nonexistent_returns_false(self):
        """Deleting non-existent canvas returns False."""
        self.assertFalse(canvas_manager.delete_canvas('nope'))

    def test_legacy_fallback(self):
        """Loading a file without version/state wrapper treats it as raw state."""
        legacy_data = {'emitters': {'1': {}}, 'tracks': {}}
        filepath = self._tmppath / 'legacy.json'
        with open(filepath, 'w') as f:
            json.dump(legacy_data, f)
        state, meta = canvas_manager.load_canvas('legacy')
        self.assertEqual(state, legacy_data)
        self.assertEqual(meta, {})


class TestCanvasIntegration(GUITestCase):
    """Integration tests for canvas save/load through the GUI stack."""

    def setUp(self):
        super().setUp()
        self._tmpdir = tempfile.TemporaryDirectory()
        self._tmppath = Path(self._tmpdir.name)
        self._patcher = patch.object(
            canvas_manager, 'get_canvas_directory',
            return_value=self._tmppath
        )
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        self._tmpdir.cleanup()
        super().tearDown()

    def test_save_preserves_grid_mode(self):
        """Canvas save includes grid_mode in metadata."""
        adapter = self.harness.adapter
        adapter.save_canvas('test_mode', 'column')

        _, meta = canvas_manager.load_canvas('test_mode')
        self.assertEqual(meta['grid_mode'], 'column')

    def test_load_restores_emitter_params(self):
        """Loading canvas restores emitter parameter values."""
        adapter = self.harness.adapter
        state = adapter.state

        # Set non-default values
        state.set_emitter_param(1, 'volume', 42)
        state.set_emitter_param(2, 'grain_density', 99)
        adapter.save_canvas('emitter_test', 'hardware')

        # Reset to defaults
        state.reset_to_defaults(record_undo=False)
        self.assertEqual(state.get_emitter_param(1, 'volume'), 100)  # default

        # Load canvas (synchronous mock - no hardware sync needed)
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(adapter.load_canvas('emitter_test'))
        finally:
            loop.close()

        self.assertEqual(state.get_emitter_param(1, 'volume'), 42)
        self.assertEqual(state.get_emitter_param(2, 'grain_density'), 99)

    def test_load_restores_track_volumes(self):
        """Loading canvas restores track volumes."""
        adapter = self.harness.adapter
        state = adapter.state

        state.set_track_volume(3, 50)
        state.set_track_volume(7, 20)
        adapter.save_canvas('track_test', 'hardware')

        state.reset_to_defaults(record_undo=False)
        self.assertEqual(state.get_track_volume(3), 100)

        import asyncio
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(adapter.load_canvas('track_test'))
        finally:
            loop.close()

        self.assertEqual(state.get_track_volume(3), 50)
        self.assertEqual(state.get_track_volume(7), 20)

    def test_save_preserves_cells(self):
        """Canvas save includes cell placements."""
        adapter = self.harness.adapter
        state = adapter.state

        # place_in_cell(emitter_num, column, cell)
        state.place_in_cell(1, 1, 1)
        state.place_in_cell(2, 3, 5)
        adapter.save_canvas('cells_test', 'hardware')

        state.reset_to_defaults(record_undo=False)
        self.assertIsNone(state.get_cell(1, 1))

        import asyncio
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(adapter.load_canvas('cells_test'))
        finally:
            loop.close()

        self.assertEqual(state.get_cell(1, 1), 1)
        self.assertEqual(state.get_cell(3, 5), 2)

    def test_save_preserves_sequencer_patterns(self):
        """Canvas save includes both column and grid patterns."""
        adapter = self.harness.adapter
        state = adapter.state

        state.set_column_pattern_cell(1, 3, 2)
        state.set_column_pattern_cell(4, 7, 1)
        state.set_grid_pattern_cell(10, 3)
        state.set_sequencer_bpm(140)
        adapter.save_canvas('seq_test', 'column')

        state.reset_to_defaults(record_undo=False)

        import asyncio
        loop = asyncio.new_event_loop()
        try:
            meta = loop.run_until_complete(adapter.load_canvas('seq_test'))
        finally:
            loop.close()

        self.assertEqual(meta['grid_mode'], 'column')
        self.assertEqual(state.get_column_pattern(1), {3: 2})
        self.assertEqual(state.get_column_pattern(4), {7: 1})
        self.assertEqual(state.get_grid_pattern(), {10: 3})
        self.assertEqual(state.get_sequencer_bpm(), 140)

    def test_load_creates_undo_checkpoint(self):
        """Loading a canvas creates an undo checkpoint."""
        adapter = self.harness.adapter
        state = adapter.state

        # Set initial value
        state.set_emitter_param(1, 'volume', 60)
        adapter.save_canvas('undo_test', 'hardware')

        # Change to different value
        state.set_emitter_param(1, 'volume', 30)

        # Load canvas (replaces state, should push undo first)
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(adapter.load_canvas('undo_test'))
        finally:
            loop.close()

        self.assertEqual(state.get_emitter_param(1, 'volume'), 60)

        # Undo should restore the pre-load state
        state.undo()
        self.assertEqual(state.get_emitter_param(1, 'volume'), 30)

    def test_canvas_json_human_readable(self):
        """Canvas JSON file is indented and human-readable."""
        adapter = self.harness.adapter
        adapter.save_canvas('readable', 'hardware')

        filepath = self._tmppath / 'readable.json'
        content = filepath.read_text()
        # Indented JSON should have newlines and spaces
        self.assertIn('\n', content)
        self.assertIn('  ', content)
        # Should be valid JSON
        data = json.loads(content)
        self.assertEqual(data['version'], 1)

    def test_save_preserves_preset_envelope(self):
        """Canvas save/load preserves envelope preset metadata."""
        adapter = self.harness.adapter
        state = adapter.state

        envelope = state.get_envelope('emitter.1.volume')
        envelope.enabled = True
        envelope.preset = 'RAMP_UP'
        envelope.per_cell = False
        envelope.add_point(0.0, 0.0)
        envelope.add_point(1.0, 1.0)
        state.set_envelope('emitter.1.volume', envelope)

        adapter.save_canvas('preset_test', 'hardware')
        state.reset_to_defaults(record_undo=False)

        import asyncio
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(adapter.load_canvas('preset_test'))
        finally:
            loop.close()

        restored = state.get_envelope('emitter.1.volume')
        self.assertEqual(restored.preset, 'RAMP_UP')
        self.assertFalse(restored.per_cell)
        self.assertEqual(len(restored.points), 2)

    def test_save_preserves_pencil_envelope(self):
        """Canvas save/load preserves pencil (free-draw) envelope metadata."""
        adapter = self.harness.adapter
        state = adapter.state

        envelope = state.get_envelope('emitter.2.grain_density')
        envelope.enabled = True
        envelope.preset = 'pencil'
        envelope.add_point(0.0, 0.3)
        envelope.add_point(0.25, 0.8)
        envelope.add_point(0.5, 0.1)
        envelope.add_point(0.75, 0.9)
        envelope.add_point(1.0, 0.5)
        state.set_envelope('emitter.2.grain_density', envelope)

        adapter.save_canvas('pencil_test', 'hardware')
        state.reset_to_defaults(record_undo=False)

        import asyncio
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(adapter.load_canvas('pencil_test'))
        finally:
            loop.close()

        restored = state.get_envelope('emitter.2.grain_density')
        self.assertEqual(restored.preset, 'pencil')
        self.assertEqual(len(restored.points), 5)

    def test_save_preserves_per_cell(self):
        """Canvas save/load preserves per_cell flag."""
        adapter = self.harness.adapter
        state = adapter.state

        envelope = state.get_envelope('global.reverb.mix')
        envelope.enabled = True
        envelope.preset = 'TRIANGLE'
        envelope.per_cell = True
        envelope.add_point(0.0, 0.0)
        envelope.add_point(0.5, 1.0)
        envelope.add_point(1.0, 0.0)
        state.set_envelope('global.reverb.mix', envelope)

        adapter.save_canvas('percell_test', 'hardware')
        state.reset_to_defaults(record_undo=False)

        import asyncio
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(adapter.load_canvas('percell_test'))
        finally:
            loop.close()

        restored = state.get_envelope('global.reverb.mix')
        self.assertTrue(restored.per_cell)
        self.assertEqual(restored.preset, 'TRIANGLE')

    def test_envelope_backward_compatible(self):
        """Loading canvas without preset/per_cell fields uses defaults."""
        envelope = Envelope.from_dict({
            'points': [{'time': 0.0, 'value': 0.5}, {'time': 1.0, 'value': 1.0}],
            'enabled': True,
        })
        self.assertIsNone(envelope.preset)
        self.assertFalse(envelope.per_cell)
        self.assertTrue(envelope.enabled)
        self.assertEqual(len(envelope.points), 2)

    def test_envelope_enabled_state_roundtrip(self):
        """Envelope enabled state survives save/load."""
        adapter = self.harness.adapter
        state = adapter.state

        envelope = state.get_envelope('track.1.volume')
        envelope.enabled = True
        envelope.add_point(0.0, 1.0)
        envelope.add_point(1.0, 0.0)
        state.set_envelope('track.1.volume', envelope)

        adapter.save_canvas('enabled_test', 'hardware')

        # Reset and verify default
        state.reset_to_defaults(record_undo=False)
        self.assertFalse(state.get_envelope('track.1.volume').enabled)

        import asyncio
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(adapter.load_canvas('enabled_test'))
        finally:
            loop.close()

        restored = state.get_envelope('track.1.volume')
        self.assertTrue(restored.enabled)


if __name__ == '__main__':
    unittest.main()
