"""Tests for the sequencer.sequencer module."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from sequencer.sequencer import BaseSequencer, GridSequencer, ColumnSequencer
from tempera import EmitterPool


def create_mock_pool():
    """Create a properly mocked EmitterPool with all async methods mocked."""
    pool = MagicMock(spec=EmitterPool)
    pool.place_in_cell = AsyncMock()
    pool.remove_from_cell = AsyncMock()
    pool.play_all = AsyncMock()
    return pool


class TestBaseSequencerTiming(unittest.TestCase):
    """Test timing calculations in BaseSequencer."""

    def test_step_duration_default(self):
        """Default step duration is 0.5 seconds."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        self.assertEqual(sequencer.step_duration, 0.5)

    def test_step_duration_explicit(self):
        """Explicit step_duration is used."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool, step_duration=0.25)
        self.assertEqual(sequencer.step_duration, 0.25)

    def test_bpm_calculation(self):
        """BPM is converted to step_duration correctly."""
        pool = create_mock_pool()
        # 120 BPM = 0.5 seconds per beat
        sequencer = GridSequencer(pool, bpm=120)
        self.assertEqual(sequencer.step_duration, 0.5)

    def test_bpm_with_steps_per_beat(self):
        """BPM with steps_per_beat divides correctly."""
        pool = create_mock_pool()
        # 120 BPM, 2 steps per beat = 0.25 seconds per step
        sequencer = GridSequencer(pool, bpm=120, steps_per_beat=2)
        self.assertEqual(sequencer.step_duration, 0.25)

    def test_bpm_and_step_duration_conflict(self):
        """Cannot specify both bpm and step_duration."""
        pool = create_mock_pool()
        with self.assertRaises(ValueError):
            GridSequencer(pool, bpm=120, step_duration=0.5)

    def test_set_bpm(self):
        """set_bpm updates step_duration."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        sequencer.set_bpm(60)  # 60 BPM = 1 second per beat
        self.assertEqual(sequencer.step_duration, 1.0)

    def test_set_bpm_with_steps_per_beat(self):
        """set_bpm with steps_per_beat divides correctly."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        sequencer.set_bpm(60, steps_per_beat=4)  # 60 BPM, 4 steps = 0.25 sec
        self.assertEqual(sequencer.step_duration, 0.25)


class TestGridSequencerPattern(unittest.IsolatedAsyncioTestCase):
    """Test GridSequencer pattern management."""

    async def test_set_pattern(self):
        """set_pattern stores the pattern."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        pattern = {0: 1, 4: 2, 8: 3}
        await sequencer.set_pattern(pattern)
        self.assertEqual(sequencer._pattern, pattern)

    async def test_set_pattern_copies(self):
        """set_pattern makes a copy of the pattern."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        pattern = {0: 1, 4: 2}
        await sequencer.set_pattern(pattern)
        pattern[8] = 3  # Modify original
        self.assertNotIn(8, sequencer._pattern)

    async def test_clear(self):
        """clear removes all pattern entries."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        await sequencer.set_pattern({0: 1, 4: 2})
        await sequencer.clear()
        self.assertEqual(sequencer._pattern, {})

    async def test_get_state(self):
        """get_state returns current state."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        await sequencer.set_pattern({0: 1})
        state = sequencer.get_state()
        self.assertIn('pattern', state)
        self.assertIn('current_step', state)
        self.assertIn('loop_count', state)
        self.assertIn('running', state)
        self.assertIn('paused', state)

    def test_total_steps_empty_pattern(self):
        """GridSequencer with empty pattern defaults to 8 steps (column count)."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        self.assertEqual(sequencer._get_total_steps(), 8)

    def test_total_steps_from_pattern(self):
        """GridSequencer total steps is max pattern key + 1."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        sequencer._pattern = {0: 1, 8: 2}
        self.assertEqual(sequencer._get_total_steps(), 9)  # max(0, 8) + 1


class TestColumnSequencerPattern(unittest.IsolatedAsyncioTestCase):
    """Test ColumnSequencer pattern management."""

    async def test_set_column_pattern(self):
        """set_column_pattern stores pattern for column."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        pattern = {1: 1, 3: 2, 5: 1}
        await sequencer.set_column_pattern(1, pattern)
        self.assertEqual(sequencer._patterns[1], pattern)

    async def test_set_column_pattern_copies(self):
        """set_column_pattern makes a copy."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        pattern = {1: 1, 3: 2}
        await sequencer.set_column_pattern(1, pattern)
        pattern[5] = 3  # Modify original
        self.assertNotIn(5, sequencer._patterns[1])

    async def test_set_column_pattern_invalid_column(self):
        """set_column_pattern raises for invalid column."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        with self.assertRaises(ValueError):
            await sequencer.set_column_pattern(0, {1: 1})
        with self.assertRaises(ValueError):
            await sequencer.set_column_pattern(9, {1: 1})

    async def test_clear_column(self):
        """clear_column removes pattern for column."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        await sequencer.set_column_pattern(1, {1: 1, 3: 2})
        await sequencer.clear_column(1)
        self.assertEqual(sequencer._patterns[1], {})

    def test_mute_column(self):
        """mute_column sets muted state."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        sequencer.mute_column(1)
        self.assertTrue(sequencer._muted[1])

    def test_unmute_column(self):
        """unmute_column clears muted state."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        sequencer.mute_column(1)
        sequencer.unmute_column(1)
        self.assertFalse(sequencer._muted[1])

    def test_set_mute_pattern(self):
        """set_mute_pattern stores pattern."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        sequencer.set_mute_pattern(1, [1, 0, 1, 0])
        self.assertEqual(sequencer._mute_patterns[1], [True, False, True, False])

    async def test_get_column_state(self):
        """get_column_state returns column state."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        await sequencer.set_column_pattern(1, {1: 1})
        sequencer.mute_column(1)
        sequencer.set_mute_pattern(1, [1, 0])
        state = sequencer.get_column_state(1)
        self.assertEqual(state['pattern'], {1: 1})
        self.assertTrue(state['muted'])
        self.assertEqual(state['mute_pattern'], [True, False])

    def test_total_steps(self):
        """ColumnSequencer has 8 total steps."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        self.assertEqual(sequencer._get_total_steps(), 8)


class TestGridSequencerAsync(unittest.IsolatedAsyncioTestCase):
    """Async tests for GridSequencer."""

    async def test_execute_step_places_cell(self):
        """_execute_step calls place_in_cell for pattern entries."""
        pool = create_mock_pool()

        sequencer = GridSequencer(pool)
        await sequencer.set_pattern({0: 1})  # Step 0, emitter 1

        await sequencer._execute_step(0, 0)

        pool.place_in_cell.assert_called_once_with(1, 1, 1)  # emitter, column, cell

    async def test_execute_step_removes_previous(self):
        """_execute_step removes cells no longer in pattern."""
        pool = create_mock_pool()

        sequencer = GridSequencer(pool)
        await sequencer.set_pattern({0: 1})

        # Execute step 0 (places cell)
        await sequencer._execute_step(0, 0)
        pool.place_in_cell.assert_called_with(1, 1, 1)

        # Execute step 0 again without pattern - should remove
        await sequencer.set_pattern({})
        await sequencer._execute_step(0, 0)
        pool.remove_from_cell.assert_called_with(1, 1, 1)

    async def test_run_limited_loops(self):
        """run with loops parameter stops after N loops."""
        pool = create_mock_pool()

        sequencer = GridSequencer(pool, step_duration=0.001)
        await sequencer.set_pattern({0: 1})

        await sequencer.run(loops=1)

        self.assertEqual(sequencer._loop_count, 1)
        self.assertFalse(sequencer._running)

    async def test_stop(self):
        """stop terminates the run loop."""
        pool = create_mock_pool()

        sequencer = GridSequencer(pool, step_duration=0.01)
        await sequencer.set_pattern({0: 1})

        async def stop_after_delay():
            await asyncio.sleep(0.05)
            await sequencer.stop()

        asyncio.create_task(stop_after_delay())
        await sequencer.run(loops=0)  # Infinite

        self.assertFalse(sequencer._running)

    async def test_pause_resume(self):
        """pause and resume control execution."""
        pool = create_mock_pool()

        sequencer = GridSequencer(pool, step_duration=0.01)
        await sequencer.set_pattern({0: 1})

        async def pause_resume_stop():
            await asyncio.sleep(0.02)
            await sequencer.pause()
            self.assertTrue(sequencer._paused)
            await asyncio.sleep(0.02)
            await sequencer.resume()
            self.assertFalse(sequencer._paused)
            await asyncio.sleep(0.02)
            await sequencer.stop()

        asyncio.create_task(pause_resume_stop())
        await sequencer.run(loops=0)

    async def test_dispatch_set_pattern(self):
        """dispatch handles set_pattern action."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)

        await sequencer.dispatch({'action': 'set_pattern', 'pattern': {0: 1, 4: 2}})

        self.assertEqual(sequencer._pattern, {0: 1, 4: 2})

    async def test_dispatch_clear(self):
        """dispatch handles clear action."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)
        await sequencer.set_pattern({0: 1})

        await sequencer.dispatch({'action': 'clear'})

        self.assertEqual(sequencer._pattern, {})

    async def test_dispatch_set_loops(self):
        """dispatch handles set_loops action."""
        pool = create_mock_pool()
        sequencer = GridSequencer(pool)

        await sequencer.dispatch({'action': 'set_loops', 'loops': 8})

        self.assertEqual(sequencer._target_loops, 8)


class TestColumnSequencerAsync(unittest.IsolatedAsyncioTestCase):
    """Async tests for ColumnSequencer."""

    async def test_execute_step_places_cells_all_columns(self):
        """_execute_step processes all columns."""
        pool = create_mock_pool()

        sequencer = ColumnSequencer(pool)
        await sequencer.set_column_pattern(1, {1: 1})  # Column 1, cell 1, emitter 1
        await sequencer.set_column_pattern(3, {1: 2})  # Column 3, cell 1, emitter 2

        await sequencer._execute_step(0, 0)  # Step 0 = cell 1

        calls = pool.place_in_cell.call_args_list
        self.assertEqual(len(calls), 2)

    async def test_execute_step_respects_mute(self):
        """_execute_step skips muted columns."""
        pool = create_mock_pool()

        sequencer = ColumnSequencer(pool)
        await sequencer.set_column_pattern(1, {1: 1})
        sequencer.mute_column(1)

        await sequencer._execute_step(0, 0)

        pool.place_in_cell.assert_not_called()

    async def test_execute_step_respects_mute_pattern(self):
        """_execute_step uses mute pattern for loop-based muting."""
        pool = create_mock_pool()

        sequencer = ColumnSequencer(pool)
        await sequencer.set_column_pattern(1, {1: 1})
        sequencer.set_mute_pattern(1, [True, False])  # Play on even loops, mute on odd

        # Loop 0 (even) - should play
        await sequencer._execute_step(0, 0)
        self.assertEqual(pool.place_in_cell.call_count, 1)

        pool.place_in_cell.reset_mock()

        # Loop 1 (odd) - should mute
        await sequencer._execute_step(0, 1)
        pool.place_in_cell.assert_not_called()

    async def test_dispatch_set_column_pattern(self):
        """dispatch handles set_column_pattern action."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)

        await sequencer.dispatch({
            'action': 'set_column_pattern',
            'column': 1,
            'pattern': {1: 1, 3: 2}
        })

        self.assertEqual(sequencer._patterns[1], {1: 1, 3: 2})

    async def test_dispatch_mute_column(self):
        """dispatch handles mute_column action."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)

        await sequencer.dispatch({'action': 'mute_column', 'column': 2})

        self.assertTrue(sequencer._muted[2])

    async def test_dispatch_unmute_column(self):
        """dispatch handles unmute_column action."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)
        sequencer.mute_column(2)

        await sequencer.dispatch({'action': 'unmute_column', 'column': 2})

        self.assertFalse(sequencer._muted[2])

    async def test_dispatch_set_mute_pattern(self):
        """dispatch handles set_mute_pattern action."""
        pool = create_mock_pool()
        sequencer = ColumnSequencer(pool)

        await sequencer.dispatch({
            'action': 'set_mute_pattern',
            'column': 1,
            'pattern': [1, 0, 1, 0]
        })

        self.assertEqual(sequencer._mute_patterns[1], [True, False, True, False])


class TestGridSequencerIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for GridSequencer with virtual MIDI port."""

    async def test_sequencer_with_emitter_pool(self):
        """GridSequencer works with real EmitterPool."""
        try:
            async with EmitterPool(port_name='Sequencer Test', virtual=True) as pool:
                sequencer = GridSequencer(pool, step_duration=0.01)
                await sequencer.set_pattern({0: 1, 8: 2})  # Steps in columns 1 and 2

                await sequencer.run(loops=1)

                self.assertEqual(sequencer._loop_count, 1)
        except Exception as e:
            if "Virtual MIDI" in str(e) or "rtmidi" in str(e).lower():
                self.skipTest(f"Virtual MIDI ports not available: {e}")
            raise


class TestColumnSequencerIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for ColumnSequencer with virtual MIDI port."""

    async def test_sequencer_with_emitter_pool(self):
        """ColumnSequencer works with real EmitterPool."""
        try:
            async with EmitterPool(port_name='ColumnSeq Test', virtual=True) as pool:
                sequencer = ColumnSequencer(pool, step_duration=0.01)
                await sequencer.set_column_pattern(1, {1: 1, 5: 1})
                await sequencer.set_column_pattern(2, {2: 2, 6: 2})

                await sequencer.run(loops=1)

                self.assertEqual(sequencer._loop_count, 1)
        except Exception as e:
            if "Virtual MIDI" in str(e) or "rtmidi" in str(e).lower():
                self.skipTest(f"Virtual MIDI ports not available: {e}")
            raise


if __name__ == '__main__':
    unittest.main()
