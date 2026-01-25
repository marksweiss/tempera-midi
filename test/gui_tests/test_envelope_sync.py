"""Priority 5: Envelope Panel Synchronization Tests.

Tests for verifying the envelope panel correctly displays the envelope
for the currently focused control.
"""

import unittest
from gui.shortcuts import Section, NavigationMode
from test.gui_tests.base import GUITestCase


class TestEnvelopeShowsFocusedControl(GUITestCase):
    """Tests for envelope panel showing correct control."""

    def test_envelope_shows_focused_emitter_control(self):
        """Envelope panel displays envelope for focused emitter control."""
        # Focus volume slider in Emitter panel
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)

        # Get envelope panel state
        envelope = self.harness.get_envelope_panel_state()

        # Should show emitter 1 volume (default emitter is 1)
        self.assertEqual(envelope.control_key, 'emitter.1.volume')
        self.assertIn('Emitter 1', envelope.display_name)
        self.assertIn('Volume', envelope.display_name)

    def test_envelope_shows_focused_global_control(self):
        """Envelope panel displays envelope for focused global control."""
        # Focus ADSR attack in Global panel
        self.harness.click_control(Section.GLOBAL, subsection=0, control=0)

        envelope = self.harness.get_envelope_panel_state()

        self.assertEqual(envelope.control_key, 'global.adsr.attack')
        self.assertIn('ADSR', envelope.display_name)
        self.assertIn('Attack', envelope.display_name)

    def test_envelope_shows_focused_track_control(self):
        """Envelope panel displays envelope for focused track control."""
        # Focus track 1 volume
        self.harness.click_control(Section.TRACKS, subsection=0, control=0)

        envelope = self.harness.get_envelope_panel_state()

        self.assertEqual(envelope.control_key, 'track.1.volume')
        self.assertIn('Track 1', envelope.display_name)


class TestEnvelopeUpdatesOnFocusChange(GUITestCase):
    """Tests for envelope panel updating when focus changes."""

    def test_envelope_updates_on_control_change(self):
        """Envelope panel updates when navigating to different control."""
        # Focus first control
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)
        first_envelope = self.harness.get_envelope_panel_state()

        # Navigate to next control (S in control mode)
        self.harness.press_shortcut('S')
        second_envelope = self.harness.get_envelope_panel_state()

        # Should be different controls
        self.assertNotEqual(first_envelope.control_key, second_envelope.control_key)

    def test_envelope_updates_on_subsection_change(self):
        """Envelope panel updates when changing subsections."""
        # Focus control in first subsection
        self.harness.click_control(Section.GLOBAL, subsection=0, control=0)
        first_key = self.harness.get_envelope_panel_state().control_key
        self.assertIn('adsr', first_key)

        # Focus control in second subsection (reverb)
        self.harness.click_control(Section.GLOBAL, subsection=1, control=0)
        second_key = self.harness.get_envelope_panel_state().control_key
        self.assertIn('reverb', second_key)

    def test_envelope_updates_on_section_change(self):
        """Envelope panel updates when changing sections."""
        # Focus emitter control
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)
        emitter_key = self.harness.get_envelope_panel_state().control_key
        self.assertIn('emitter', emitter_key)

        # Focus global control
        self.harness.click_control(Section.GLOBAL, subsection=0, control=0)
        global_key = self.harness.get_envelope_panel_state().control_key
        self.assertIn('global', global_key)


class TestEnvelopeControlKeyFormat(GUITestCase):
    """Tests for correct control key format generation."""

    def test_emitter_control_key_format(self):
        """Emitter control keys have correct format."""
        # Test various emitter controls
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)
        envelope = self.harness.get_envelope_panel_state()

        # Should be emitter.{num}.{param}
        parts = envelope.control_key.split('.')
        self.assertEqual(parts[0], 'emitter')
        self.assertIn(parts[1], ['1', '2', '3', '4'])

    def test_track_control_key_format(self):
        """Track control keys have correct format."""
        self.harness.click_control(Section.TRACKS, subsection=2, control=0)
        envelope = self.harness.get_envelope_panel_state()

        # Should be track.{num}.volume
        self.assertEqual(envelope.control_key, 'track.3.volume')

    def test_global_control_key_format(self):
        """Global control keys have correct format."""
        # ADSR
        self.harness.click_control(Section.GLOBAL, subsection=0, control=0)
        envelope = self.harness.get_envelope_panel_state()
        self.assertIn('global.adsr', envelope.control_key)

        # Reverb
        self.harness.click_control(Section.GLOBAL, subsection=1, control=0)
        envelope = self.harness.get_envelope_panel_state()
        self.assertIn('global.reverb', envelope.control_key)


class TestEnvelopeStateConsistency(GUITestCase):
    """Tests for envelope state consistency with navigation."""

    def test_envelope_consistent_after_rapid_navigation(self):
        """Envelope state stays consistent after rapid navigation."""
        # Rapid navigation sequence
        controls = [
            (Section.EMITTER, 0, 0),
            (Section.GLOBAL, 1, 0),
            (Section.TRACKS, 3, 0),
            (Section.EMITTER, 2, 1),
        ]

        for section, subsection, control in controls:
            self.harness.click_control(section, subsection, control)
            # State should be consistent including envelope
            self.harness.assert_state_consistent()

    def test_envelope_consistent_with_keyboard_nav(self):
        """Envelope updates correctly with keyboard navigation."""
        # Enter control mode via keyboard
        self.harness.press_shortcut('Q')  # Emitter
        self.harness.press_shortcut('F')  # Subsection
        self.harness.press_shortcut('F')  # Control

        # Navigate through controls
        for _ in range(3):
            self.harness.press_shortcut('D')
            self.harness.assert_state_consistent()


class TestEnvelopePanelTitle(GUITestCase):
    """Tests for envelope panel title display."""

    def test_emitter_title_format(self):
        """Emitter control displays correct title."""
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)
        envelope = self.harness.get_envelope_panel_state()

        # Title should mention emitter number and parameter
        self.assertIn('Emitter', envelope.display_name)

    def test_track_title_format(self):
        """Track control displays correct title."""
        self.harness.click_control(Section.TRACKS, subsection=4, control=0)
        envelope = self.harness.get_envelope_panel_state()

        self.assertIn('Track 5', envelope.display_name)

    def test_global_title_format(self):
        """Global control displays correct title."""
        self.harness.click_control(Section.GLOBAL, subsection=2, control=0)
        envelope = self.harness.get_envelope_panel_state()

        # Should show parameter type
        self.assertIn('Delay', envelope.display_name)


class TestEnvelopeWithEmitterChange(GUITestCase):
    """Tests for envelope behavior when active emitter changes."""

    def test_envelope_reflects_active_emitter(self):
        """Envelope control key reflects currently active emitter."""
        # Focus emitter control
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)

        envelope1 = self.harness.get_envelope_panel_state()
        self.assertIn('.1.', envelope1.control_key)

        # Change active emitter via keyboard
        self.harness.press_shortcut('2')  # Select emitter 2

        # Re-focus to update envelope (simulating re-selection)
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)

        envelope2 = self.harness.get_envelope_panel_state()
        # Should now show emitter 2
        self.assertIn('.2.', envelope2.control_key)


if __name__ == '__main__':
    unittest.main()
