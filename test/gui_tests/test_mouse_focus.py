"""Mouse focus interaction tests.

Tests for focus behavior when clicking on controls with the mouse.
"""

import unittest
from gui.shortcuts import Section, NavigationMode
from test.gui_tests.base import GUITestCase


class TestMouseClickFocus(GUITestCase):
    """Tests for mouse click focus behavior."""

    def test_click_emitter_control(self):
        """Clicking emitter control sets focus correctly."""
        # Click on volume slider (subsection 0, control 0)
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.EMITTER)
        self.assertEqual(nav.subsection, 0)
        self.assertEqual(nav.control, 0)
        self.assertEqual(nav.mode, NavigationMode.CONTROL)
        self.harness.assert_state_consistent()

    def test_click_global_control(self):
        """Clicking global control sets focus correctly."""
        # Click on ADSR attack (subsection 0, control 0)
        self.harness.click_control(Section.GLOBAL, subsection=0, control=0)

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.GLOBAL)
        self.assertEqual(nav.subsection, 0)
        self.assertEqual(nav.control, 0)
        self.harness.assert_state_consistent()

    def test_click_track_slider(self):
        """Clicking track slider sets focus correctly."""
        # Click on track 3 volume (subsection 2 = track 3)
        self.harness.click_control(Section.TRACKS, subsection=2, control=0)

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.TRACKS)
        # Track panel uses subsection as track index
        self.assertEqual(nav.subsection, 2)
        self.harness.assert_state_consistent()

    def test_click_switches_section(self):
        """Clicking control in different section switches sections."""
        # Start in Emitter
        self.harness.press_shortcut('E')

        # Click in Global
        self.harness.click_control(Section.GLOBAL, subsection=1, control=0)

        # Should now be in Global
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.GLOBAL)

        # Emitter should be unfocused
        emitter = self.harness.get_panel_state(Section.EMITTER)
        self.assertFalse(emitter.panel_focused)
        self.harness.assert_state_consistent()

    def test_click_different_group_same_section(self):
        """Clicking control in different group updates subsection."""
        # Click first group
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)

        # Click third group (Grain)
        self.harness.click_control(Section.EMITTER, subsection=2, control=1)

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.subsection, 2)
        self.assertEqual(nav.control, 1)
        self.harness.assert_state_consistent()

    def test_click_different_control_same_group(self):
        """Clicking different control in same group updates control."""
        # Click first control
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)

        # Click second control in same group
        self.harness.click_control(Section.EMITTER, subsection=0, control=1)

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.subsection, 0)
        self.assertEqual(nav.control, 1)
        self.harness.assert_state_consistent()

    def test_click_after_keyboard_nav(self):
        """Click works correctly after keyboard navigation."""
        # Use keyboard to get to a specific state
        self.harness.press_shortcut('G')  # Global
        self.harness.press_shortcut('F')  # Subsection
        self.harness.press_shortcut('S')  # Navigate subsection

        # Now click on Emitter control
        self.harness.click_control(Section.EMITTER, subsection=1, control=0)

        # Should be in Emitter, control mode
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.EMITTER)
        self.assertEqual(nav.mode, NavigationMode.CONTROL)
        self.harness.assert_state_consistent()


class TestClickDuringModes(GUITestCase):
    """Tests for mouse clicks during different navigation modes."""

    def test_click_during_section_mode(self):
        """Click while in SECTION mode enters CONTROL mode."""
        self.harness.press_shortcut('E')
        self.harness.assert_mode(NavigationMode.SECTION)

        self.harness.click_control(Section.EMITTER, subsection=0, control=0)

        self.harness.assert_mode(NavigationMode.CONTROL)
        self.harness.assert_state_consistent()

    def test_click_during_subsection_mode(self):
        """Click while in SUBSECTION mode enters CONTROL mode."""
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')
        self.harness.assert_mode(NavigationMode.SUBSECTION)

        self.harness.click_control(Section.EMITTER, subsection=1, control=0)

        self.harness.assert_mode(NavigationMode.CONTROL)
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.subsection, 1)
        self.harness.assert_state_consistent()

    def test_click_during_control_mode(self):
        """Click while in CONTROL mode changes focused control."""
        # Enter control mode via click
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)

        # Click different control
        self.harness.click_control(Section.EMITTER, subsection=0, control=2)

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.control, 2)
        self.harness.assert_mode(NavigationMode.CONTROL)
        self.harness.assert_state_consistent()


class TestClickConsistency(GUITestCase):
    """Tests for consistent state after various click sequences."""

    def test_alternating_section_clicks(self):
        """Alternating clicks between sections maintains consistency."""
        for _ in range(3):
            self.harness.click_control(Section.EMITTER, subsection=0, control=0)
            self.harness.assert_state_consistent()

            self.harness.click_control(Section.GLOBAL, subsection=0, control=0)
            self.harness.assert_state_consistent()

    def test_click_all_emitter_groups(self):
        """Clicking through all emitter groups maintains consistency."""
        for subsection in range(4):  # 4 groups in Emitter panel
            self.harness.click_control(Section.EMITTER, subsection=subsection, control=0)
            self.harness.assert_state_consistent()

            nav = self.harness.get_nav_state()
            self.assertEqual(nav.subsection, subsection)

    def test_click_all_global_groups(self):
        """Clicking through all global groups maintains consistency."""
        for subsection in range(4):  # 4 standard groups in Global (not modwheel)
            self.harness.click_control(Section.GLOBAL, subsection=subsection, control=0)
            self.harness.assert_state_consistent()

            nav = self.harness.get_nav_state()
            self.assertEqual(nav.subsection, subsection)


if __name__ == '__main__':
    unittest.main()
