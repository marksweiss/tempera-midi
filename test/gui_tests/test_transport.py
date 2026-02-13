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


if __name__ == '__main__':
    unittest.main()
