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


class TestSliderVisualFocus(GUITestCase):
    """Tests verifying slider blue glow after mouse clicks.

    These tests specifically verify that clicking on a slider shows the
    visual blue focus indicator (not just updating NavigationManager state).
    """

    def test_click_emitter_control_shows_blue_glow(self):
        """Clicking slider shows blue focus indicator."""
        self.harness.click_control(Section.EMITTER, 0, 0)  # Basic > Volume

        # Verify NavigationManager state
        self.harness.assert_mode(NavigationMode.CONTROL)

        # Verify visual focus styling - focused_index should be set
        group_state = self.harness.get_slider_group_state(Section.EMITTER, 0)
        self.assertEqual(group_state.focused_index, 0)

    def test_click_different_slider_transfers_focus(self):
        """Clicking different slider transfers blue glow."""
        self.harness.click_control(Section.EMITTER, 0, 0)  # Volume
        self.harness.click_control(Section.EMITTER, 0, 1)  # Octave

        group_state = self.harness.get_slider_group_state(Section.EMITTER, 0)
        self.assertEqual(group_state.focused_index, 1)  # Now on Octave

    def test_click_slider_in_different_group_moves_focus(self):
        """Clicking slider in different group moves visual focus to new group."""
        # Focus Volume in Basic group
        self.harness.click_control(Section.EMITTER, 0, 0)
        basic_state = self.harness.get_slider_group_state(Section.EMITTER, 0)
        self.assertTrue(basic_state.group_focused)
        self.assertEqual(basic_state.focused_index, 0)

        # Click slider in Grain group
        self.harness.click_control(Section.EMITTER, 2, 0)

        # Basic group should no longer be the focused group
        # (focused_index may persist for return navigation)
        basic_state = self.harness.get_slider_group_state(Section.EMITTER, 0)
        self.assertFalse(basic_state.group_focused)

        # Grain group should now be focused with its slider
        grain_state = self.harness.get_slider_group_state(Section.EMITTER, 2)
        self.assertTrue(grain_state.group_focused)
        self.assertEqual(grain_state.focused_index, 0)

    def test_focus_persists_after_click(self):
        """Focus remains until another control is selected."""
        self.harness.click_control(Section.EMITTER, 0, 0)

        # Process additional events (simulate time passing)
        self.harness.process_events()

        # Focus should still be on the clicked control
        group_state = self.harness.get_slider_group_state(Section.EMITTER, 0)
        self.assertEqual(group_state.focused_index, 0)

    def test_global_slider_click_shows_focus(self):
        """Clicking Global panel slider shows blue focus."""
        self.harness.click_control(Section.GLOBAL, 1, 0)  # Reverb > Size

        group_state = self.harness.get_slider_group_state(Section.GLOBAL, 1)
        self.assertEqual(group_state.focused_index, 0)
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
