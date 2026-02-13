"""Transport panel tests.

Tests for the transport panel widget and its integration with sequencer controls.
"""

import unittest
from gui.shortcuts import Section, NavigationMode
from test.gui_tests.base import GUITestCase


class TestTransportPanelSignals(GUITestCase):
    """Tests for transport panel signal emissions."""

    def test_play_button_exists(self):
        """Play button exists and is clickable."""
        transport = self.harness.window._transport
        self.assertIsNotNone(transport._play_btn)

    def test_stop_button_exists(self):
        """Stop button exists and is clickable."""
        transport = self.harness.window._transport
        self.assertIsNotNone(transport._stop_btn)

    def test_bpm_spinbox_default(self):
        """BPM spinbox has correct default value."""
        transport = self.harness.window._transport
        self.assertEqual(transport.get_bpm(), 120)

    def test_bpm_spinbox_range(self):
        """BPM spinbox has correct range."""
        transport = self.harness.window._transport
        self.assertEqual(transport._bpm_spinbox.minimum(), 20)
        self.assertEqual(transport._bpm_spinbox.maximum(), 300)


class TestSequencerSelection(GUITestCase):
    """Tests for sequencer type selection buttons."""

    def test_no_sequencer_selected_initially(self):
        """No sequencer is selected initially."""
        transport = self.harness.window._transport
        self.assertIsNone(transport.get_sequencer())

    def test_select_8track(self):
        """Selecting 8 Track Seq sets sequencer to 'column'."""
        transport = self.harness.window._transport
        transport._seq_8track_btn.click()
        self.harness.process_events()
        self.assertEqual(transport.get_sequencer(), 'column')

    def test_select_1track(self):
        """Selecting 1 Track Seq sets sequencer to 'grid'."""
        transport = self.harness.window._transport
        transport._seq_1track_btn.click()
        self.harness.process_events()
        self.assertEqual(transport.get_sequencer(), 'grid')

    def test_mutual_exclusivity(self):
        """Selecting one sequencer deselects the other."""
        transport = self.harness.window._transport

        # Select 8 track
        transport._seq_8track_btn.click()
        self.harness.process_events()
        self.assertTrue(transport._seq_8track_btn.isChecked())
        self.assertFalse(transport._seq_1track_btn.isChecked())

        # Select 1 track - should deselect 8 track
        transport._seq_1track_btn.click()
        self.harness.process_events()
        self.assertFalse(transport._seq_8track_btn.isChecked())
        self.assertTrue(transport._seq_1track_btn.isChecked())
        self.assertEqual(transport.get_sequencer(), 'grid')

    def test_deselect_returns_none(self):
        """Deselecting a sequencer returns None."""
        transport = self.harness.window._transport

        # Select then deselect
        transport._seq_8track_btn.click()
        self.harness.process_events()
        self.assertEqual(transport.get_sequencer(), 'column')

        transport._seq_8track_btn.click()
        self.harness.process_events()
        self.assertIsNone(transport.get_sequencer())

    def test_set_sequencer_without_signal(self):
        """set_sequencer() updates state without emitting signals."""
        transport = self.harness.window._transport
        transport.set_sequencer('column')
        self.assertEqual(transport.get_sequencer(), 'column')
        self.assertTrue(transport._seq_8track_btn.isChecked())
        self.assertFalse(transport._seq_1track_btn.isChecked())

    def test_set_sequencer_none(self):
        """set_sequencer(None) clears selection."""
        transport = self.harness.window._transport
        transport.set_sequencer('grid')
        transport.set_sequencer(None)
        self.assertIsNone(transport.get_sequencer())
        self.assertFalse(transport._seq_8track_btn.isChecked())
        self.assertFalse(transport._seq_1track_btn.isChecked())


class TestBPMControl(GUITestCase):
    """Tests for BPM spinbox behavior."""

    def test_set_bpm(self):
        """Setting BPM updates the spinbox."""
        transport = self.harness.window._transport
        transport.set_bpm(140)
        self.assertEqual(transport.get_bpm(), 140)

    def test_bpm_clamped_to_range(self):
        """BPM is clamped to valid range."""
        transport = self.harness.window._transport
        transport.set_bpm(10)  # Below minimum
        self.assertEqual(transport.get_bpm(), 20)  # Clamped to minimum

        transport.set_bpm(500)  # Above maximum
        self.assertEqual(transport.get_bpm(), 300)  # Clamped to maximum


class TestClearAllCellsButton(GUITestCase):
    """Tests for the Clear All Cells button."""

    def test_clear_button_exists(self):
        """Clear All Cells button exists and is not checkable."""
        transport = self.harness.window._transport
        btn = transport._clear_cells_btn
        self.assertIsNotNone(btn)
        self.assertFalse(btn.isCheckable())
        self.assertTrue(btn.isEnabled())

    def test_clear_button_emits_signal(self):
        """Clicking Clear All Cells emits clearAllCellsClicked signal."""
        transport = self.harness.window._transport
        received = []
        transport.clearAllCellsClicked.connect(lambda: received.append(True))
        transport._clear_cells_btn.click()
        self.harness.process_events()
        self.assertEqual(len(received), 1)

    def test_clear_button_disabled_during_playback(self):
        """Button is disabled when set_clear_cells_enabled(False) is called."""
        transport = self.harness.window._transport
        transport.set_clear_cells_enabled(False)
        self.assertFalse(transport._clear_cells_btn.isEnabled())
        transport.set_clear_cells_enabled(True)
        self.assertTrue(transport._clear_cells_btn.isEnabled())

    def test_clear_hardware_cells(self):
        """Clear All Cells in hardware mode clears the grid."""
        window = self.harness.window
        state = self.harness.adapter.state

        # Place some cells in hardware state
        state.place_in_cell(1, 1, 1)
        state.place_in_cell(2, 2, 3)
        state.place_in_cell(3, 5, 5)
        window._cell_grid.set_cell(1, 1, 1)
        window._cell_grid.set_cell(2, 3, 2)
        window._cell_grid.set_cell(5, 5, 3)

        # Ensure we're in hardware mode
        self.assertEqual(window._grid_mode, 'hardware')

        # Click clear all cells
        window._transport._clear_cells_btn.click()
        self.harness.process_events()

        # Grid should be empty
        self.assertEqual(window._cell_grid.get_all_cells(), {})

    def test_clear_column_cells(self):
        """Clear All Cells in column mode clears all column patterns."""
        window = self.harness.window
        state = self.harness.adapter.state

        # Switch to column mode
        window._transport._seq_8track_btn.click()
        self.harness.process_events()
        self.assertEqual(window._grid_mode, 'column')

        # Set some column patterns
        state.set_column_pattern_cell(1, 1, 1)
        state.set_column_pattern_cell(1, 5, 2)
        state.set_column_pattern_cell(3, 2, 1)
        window._cell_grid.set_cell(1, 1, 1)
        window._cell_grid.set_cell(1, 5, 2)
        window._cell_grid.set_cell(3, 2, 1)

        # Click clear all cells
        window._transport._clear_cells_btn.click()
        self.harness.process_events()

        # Grid should be empty
        self.assertEqual(window._cell_grid.get_all_cells(), {})
        # All column patterns should be empty
        for col in range(1, 9):
            self.assertEqual(state.get_column_pattern(col), {})

    def test_clear_grid_cells(self):
        """Clear All Cells in grid mode clears the grid pattern."""
        window = self.harness.window
        state = self.harness.adapter.state

        # Switch to grid mode
        window._transport._seq_1track_btn.click()
        self.harness.process_events()
        self.assertEqual(window._grid_mode, 'grid')

        # Set some grid pattern cells
        state.set_grid_pattern_cell(0, 1)
        state.set_grid_pattern_cell(10, 2)
        state.set_grid_pattern_cell(63, 3)
        window._cell_grid.set_cell(1, 1, 1)
        window._cell_grid.set_cell(2, 3, 2)
        window._cell_grid.set_cell(8, 8, 3)

        # Click clear all cells
        window._transport._clear_cells_btn.click()
        self.harness.process_events()

        # Grid should be empty
        self.assertEqual(window._cell_grid.get_all_cells(), {})
        # Grid pattern should be empty
        self.assertEqual(state.get_grid_pattern(), {})


if __name__ == '__main__':
    unittest.main()
