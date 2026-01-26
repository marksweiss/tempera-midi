"""Priority 2-3: Mode Transitions and Signal Chain Tests.

Tests for navigation mode transitions (SECTION -> SUBSECTION -> CONTROL -> VALUE)
and signal chain verification.
"""

import unittest
from gui.shortcuts import Section, NavigationMode
from test.gui_tests.base import GUITestCase


class TestModeTransitions(GUITestCase):
    """Tests for NavigationMode transitions."""

    def test_toggle_focus_enters_subsection_mode(self):
        """F from SECTION mode enters SUBSECTION mode."""
        # Setup: Navigate to Emitter section
        self.harness.press_shortcut('E')
        self.harness.assert_mode(NavigationMode.SECTION)

        # Act: Press F to toggle focus
        self.harness.press_shortcut('F')

        # Assert: Mode is SUBSECTION
        self.harness.assert_mode(NavigationMode.SUBSECTION)
        self.harness.assert_state_consistent()

    def test_toggle_focus_enters_control_mode(self):
        """F from SUBSECTION mode enters CONTROL mode."""
        # Setup: Navigate to subsection mode
        self.harness.press_shortcut('E')  # Emitter section
        self.harness.press_shortcut('F')  # Subsection mode
        self.harness.assert_mode(NavigationMode.SUBSECTION)

        # Act: Press F again
        self.harness.press_shortcut('F')

        # Assert: Mode is CONTROL
        self.harness.assert_mode(NavigationMode.CONTROL)

        # Panel should be in control mode
        panel = self.harness.get_panel_state(Section.EMITTER)
        self.assertTrue(panel.in_control_mode)
        self.harness.assert_state_consistent()

    def test_toggle_focus_exits_control_mode(self):
        """F from CONTROL mode exits back to SUBSECTION mode."""
        # Setup: Enter control mode
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')  # Subsection
        self.harness.press_shortcut('F')  # Control
        self.harness.assert_mode(NavigationMode.CONTROL)

        # Act: Press F to exit
        self.harness.press_shortcut('F')

        # Assert: Mode is SUBSECTION
        self.harness.assert_mode(NavigationMode.SUBSECTION)

        # Panel should not be in control mode
        panel = self.harness.get_panel_state(Section.EMITTER)
        self.assertFalse(panel.in_control_mode)
        self.harness.assert_state_consistent()

    def test_section_change_resets_mode(self):
        """Changing section resets mode to SECTION."""
        # Setup: Enter control mode in Emitter
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')
        self.harness.press_shortcut('F')
        self.harness.assert_mode(NavigationMode.CONTROL)

        # Act: Change to Global section
        self.harness.press_shortcut('G')

        # Assert: Mode reset to SECTION
        self.harness.assert_mode(NavigationMode.SECTION)
        self.harness.assert_focus(Section.GLOBAL)
        self.harness.assert_state_consistent()

    def test_toggle_focus_exits_mode_levels(self):
        """F key toggles back from deeper modes (CONTROL -> SUBSECTION)."""
        # Setup: Enter control mode
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')
        self.harness.press_shortcut('F')
        self.harness.assert_mode(NavigationMode.CONTROL)

        # Act: Press F to toggle back
        self.harness.press_shortcut('F')

        # Should exit to subsection mode
        self.harness.assert_mode(NavigationMode.SUBSECTION)
        self.harness.assert_state_consistent()


class TestSubsectionNavigation(GUITestCase):
    """Tests for navigating within sections (subsections)."""

    def test_emitter_subsection_navigation_down(self):
        """W/S navigates through Emitter subsections."""
        # Navigate to Emitter subsection mode
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')

        initial_subsection = self.harness.get_nav_state().subsection

        # Navigate down
        self.harness.press_shortcut('S')

        nav = self.harness.get_nav_state()
        # Should move to next subsection
        self.assertEqual(nav.subsection, (initial_subsection + 1) % 4)
        self.harness.assert_state_consistent()

    def test_emitter_subsection_navigation_up(self):
        """W navigates up through Emitter subsections."""
        # Navigate to Emitter, go to subsection 1
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')
        self.harness.press_shortcut('S')  # Go to subsection 1

        # Navigate up
        self.harness.press_shortcut('W')

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.subsection, 0)
        self.harness.assert_state_consistent()

    def test_global_subsection_includes_modulator(self):
        """Global subsection navigation includes modulator (subsection 4)."""
        # Navigate to Global
        self.harness.press_shortcut('G')
        self.harness.press_shortcut('F')

        # Navigate to modulator (subsection 4)
        for _ in range(4):
            self.harness.press_shortcut('S')

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.subsection, 4)
        self.harness.assert_state_consistent()


class TestControlNavigation(GUITestCase):
    """Tests for navigating within subsections (controls)."""

    def test_control_navigation_next(self):
        """S/W navigates through controls within a subsection (in control mode)."""
        # Enter control mode in Emitter Basic group
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')
        self.harness.press_shortcut('F')

        initial_control = self.harness.get_nav_state().control

        # Navigate to next control (S in control mode)
        self.harness.press_shortcut('S')

        nav = self.harness.get_nav_state()
        # Should move to next control
        self.assertNotEqual(nav.control, initial_control)
        self.harness.assert_state_consistent()

    def test_control_navigation_wraps(self):
        """Control navigation wraps at boundaries."""
        # Enter control mode
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')
        self.harness.press_shortcut('F')

        # Get slider group to know control count
        group = self.harness.get_slider_group_state(Section.EMITTER, 0)

        # Navigate past end - should wrap (S in control mode)
        for _ in range(group.slider_count + 1):
            self.harness.press_shortcut('S')

        nav = self.harness.get_nav_state()
        # Should have wrapped
        self.assertEqual(nav.control, 1)  # One past the start (0)
        self.harness.assert_state_consistent()


class TestRapidNavigation(GUITestCase):
    """Tests for rapid navigation sequences."""

    def test_rapid_section_navigation(self):
        """Quick section changes maintain consistent state."""
        # Rapid navigation through sections
        sections = ['Q', 'E', 'T', 'G', 'Q', 'G', 'T']

        for shortcut in sections:
            self.harness.press_shortcut(shortcut)
            # State should be consistent after each change
            self.harness.assert_state_consistent()

        # Final state should be Tracks
        self.harness.assert_focus(Section.TRACKS)

    def test_rapid_mode_transitions(self):
        """Quick mode transitions maintain consistent state."""
        self.harness.press_shortcut('E')

        # Rapid F presses
        for _ in range(5):
            self.harness.press_shortcut('F')
            self.harness.assert_state_consistent()


class TestTrackNavigation(GUITestCase):
    """Tests for Track panel navigation specifics."""

    def test_track_horizontal_navigation(self):
        """Track panel uses A/D for horizontal navigation through tracks."""
        # Navigate to Tracks section
        self.harness.press_shortcut('T')
        self.harness.press_shortcut('F')  # Subsection mode
        self.harness.press_shortcut('F')  # Control mode

        initial = self.harness.get_nav_state().subsection

        # Navigate right
        self.harness.press_shortcut('D')

        nav = self.harness.get_nav_state()
        # Should move to next track
        self.assertEqual(nav.subsection, (initial + 1) % 8)
        self.harness.assert_state_consistent()


if __name__ == '__main__':
    unittest.main()
