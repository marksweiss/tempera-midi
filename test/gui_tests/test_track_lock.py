"""Track volume lock button tests.

Tests for the Lock button on the Tracks panel that links all 8 track
volume sliders together.
"""

import unittest
from gui.styles import FOCUS_GLOW
from test.gui_tests.base import GUITestCase


class TestLockButton(GUITestCase):
    """Tests for the lock button widget basics."""

    def test_lock_button_exists(self):
        """Lock button exists, is checkable, and starts unchecked."""
        panel = self.harness.window._track_panel
        btn = panel._lock_button
        self.assertIsNotNone(btn)
        self.assertTrue(btn.isCheckable())
        self.assertFalse(btn.isChecked())
        self.assertFalse(panel.is_locked())

    def test_lock_toggles(self):
        """Clicking lock button toggles is_locked()."""
        panel = self.harness.window._track_panel
        panel._lock_button.click()
        self.harness.process_events()
        self.assertTrue(panel.is_locked())

        panel._lock_button.click()
        self.harness.process_events()
        self.assertFalse(panel.is_locked())

    def test_set_locked_programmatic(self):
        """set_locked(True) sets state and button checked."""
        panel = self.harness.window._track_panel
        panel.set_locked(True)
        self.assertTrue(panel.is_locked())
        self.assertTrue(panel._lock_button.isChecked())

        panel.set_locked(False)
        self.assertFalse(panel.is_locked())
        self.assertFalse(panel._lock_button.isChecked())


class TestLockVisualState(GUITestCase):
    """Tests for slider styling when locked."""

    def test_all_sliders_blue_when_locked(self):
        """All 8 slider stylesheets contain focus color when locked."""
        panel = self.harness.window._track_panel
        panel.set_locked(True)
        for t in range(1, 9):
            style = panel._sliders[t].styleSheet()
            self.assertIn(FOCUS_GLOW, style,
                          f"Track {t} slider missing focus color when locked")

    def test_unlock_restores_single_focus(self):
        """Unlocking with track 3 focused makes only track 3 blue."""
        panel = self.harness.window._track_panel
        panel.set_track_focus(3)
        panel.set_locked(True)
        # All should be blue
        for t in range(1, 9):
            self.assertIn(FOCUS_GLOW, panel._sliders[t].styleSheet())

        panel.set_locked(False)
        # Only track 3 should be blue
        self.assertIn(FOCUS_GLOW, panel._sliders[3].styleSheet())
        for t in [1, 2, 4, 5, 6, 7, 8]:
            self.assertNotIn(FOCUS_GLOW, panel._sliders[t].styleSheet(),
                             f"Track {t} should not be blue when unlocked")


class TestLockedSliderSync(GUITestCase):
    """Tests for slider synchronization when locked."""

    def test_drag_syncs_all_sliders(self):
        """Setting one slider value while locked syncs all 8."""
        panel = self.harness.window._track_panel
        panel.set_locked(True)
        # Simulate dragging track 3's slider to 80
        panel._sliders[3].setValue(80)
        self.harness.process_events()
        for t in range(1, 9):
            self.assertEqual(panel._sliders[t].value(), 80,
                             f"Track {t} not synced to 80")

    def test_drag_emits_8_volume_changed(self):
        """Dragging while locked emits volumeChanged 8 times."""
        panel = self.harness.window._track_panel
        panel.set_locked(True)
        received = []
        panel.volumeChanged.connect(lambda t, v: received.append((t, v)))
        panel._sliders[2].setValue(60)
        self.harness.process_events()
        self.assertEqual(len(received), 8)
        for t in range(1, 9):
            self.assertIn((t, 60), received)

    def test_release_emits_8_volume_set(self):
        """Releasing slider while locked emits volumeSet 8 times."""
        panel = self.harness.window._track_panel
        panel.set_locked(True)
        panel._sliders[5].setValue(70)
        self.harness.process_events()
        received = []
        panel.volumeSet.connect(lambda t, v: received.append((t, v)))
        panel._on_slider_released(5)
        self.assertEqual(len(received), 8)
        for t in range(1, 9):
            self.assertIn((t, 70), received)

    def test_all_labels_update(self):
        """After drag, all 8 value labels show same text."""
        panel = self.harness.window._track_panel
        panel.set_locked(True)
        panel._sliders[1].setValue(42)
        self.harness.process_events()
        for t in range(1, 9):
            self.assertEqual(panel._value_labels[t].text(), '42',
                             f"Track {t} label not updated")

    def test_no_snap_on_activation(self):
        """Enabling lock does not change existing slider values."""
        panel = self.harness.window._track_panel
        # Set different values on each track
        for t in range(1, 9):
            panel.set_volume(t, t * 10)
        panel.set_locked(True)
        # Values should be unchanged
        for t in range(1, 9):
            self.assertEqual(panel._sliders[t].value(), t * 10,
                             f"Track {t} value changed on lock activation")


class TestLockedKeyboard(GUITestCase):
    """Tests for keyboard adjustment when locked."""

    def test_adjust_all_locked(self):
        """adjust_focused_volume(5) while locked moves all 8 sliders."""
        panel = self.harness.window._track_panel
        # Set all to same value first for clean test
        for t in range(1, 9):
            panel.set_volume(t, 50)
        panel.set_track_focus(1)
        panel.set_locked(True)
        panel.adjust_focused_volume(5)
        for t in range(1, 9):
            self.assertEqual(panel._sliders[t].value(), 55,
                             f"Track {t} not adjusted")

    def test_reset_all_locked(self):
        """reset_focused_to_default() while locked resets all 8 to 100."""
        panel = self.harness.window._track_panel
        for t in range(1, 9):
            panel.set_volume(t, 30)
        panel.set_track_focus(1)
        panel.set_locked(True)
        panel.reset_focused_to_default()
        for t in range(1, 9):
            self.assertEqual(panel._sliders[t].value(), 100,
                             f"Track {t} not reset to 100")


class TestLockedMidi(GUITestCase):
    """Tests for MIDI adapter calls when locked."""

    def test_8_debounced_calls_on_drag(self):
        """Dragging while locked emits 8 volumeChanged signals that reach adapter."""
        panel = self.harness.window._track_panel
        # Navigate to tracks section to connect signals
        self.harness.press_shortcut('T')
        self.harness.process_events()

        panel.set_locked(True)
        self.harness.adapter.clear_calls()
        panel._sliders[4].setValue(90)
        self.harness.process_events()
        calls = self.harness.adapter.get_calls('set_track_volume')
        self.assertEqual(len(calls), 8,
                         f"Expected 8 set_track_volume calls, got {len(calls)}")
        # All should be immediate=False (debounced drag)
        for args, kwargs in calls:
            self.assertFalse(kwargs.get('immediate', True))

    def test_8_immediate_calls_on_release(self):
        """Releasing slider while locked sends 8 immediate calls."""
        panel = self.harness.window._track_panel
        self.harness.press_shortcut('T')
        self.harness.process_events()

        panel.set_locked(True)
        panel._sliders[4].setValue(90)
        self.harness.process_events()
        self.harness.adapter.clear_calls()
        panel._on_slider_released(4)
        self.harness.process_events()
        calls = self.harness.adapter.get_calls('set_track_volume')
        self.assertEqual(len(calls), 8,
                         f"Expected 8 set_track_volume calls, got {len(calls)}")
        # All should be immediate=True
        for args, kwargs in calls:
            self.assertTrue(kwargs.get('immediate', False))


if __name__ == '__main__':
    unittest.main()
