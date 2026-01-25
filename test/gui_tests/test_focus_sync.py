"""Priority 1: Focus Synchronization Tests.

These tests verify that visual focus state matches NavigationManager state
across all UI layers. These are the bug-prone areas where state can get
out of sync.
"""

import unittest
from gui.shortcuts import Section, NavigationMode
from test.gui_tests.base import GUITestCase


class TestFocusSynchronization(GUITestCase):
    """Tests for focus state synchronization across UI layers."""

    def test_mouse_click_syncs_nav_state(self):
        """Clicking a control updates NavigationManager state."""
        # Act - click on a control in Emitter panel
        self.harness.click_control(Section.EMITTER, subsection=0, control=2)

        # Assert NavigationManager state
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.EMITTER)
        self.assertEqual(nav.subsection, 0)
        self.assertEqual(nav.control, 2)
        self.assertEqual(nav.mode, NavigationMode.CONTROL)

        # Assert all layers consistent
        self.harness.assert_state_consistent()

    def test_nav_state_syncs_visual_focus(self):
        """Keyboard navigation updates visual focus."""
        # Navigate to Emitter section
        self.harness.press_shortcut('E')  # Go to Emitter section

        # Verify section is focused
        self.harness.assert_focus(Section.EMITTER)
        self.harness.assert_mode(NavigationMode.SECTION)

        # Enter subsection mode
        self.harness.press_shortcut('F')

        # Verify subsection mode
        self.harness.assert_mode(NavigationMode.SUBSECTION)
        panel = self.harness.get_panel_state(Section.EMITTER)
        self.assertTrue(panel.panel_focused)

        self.harness.assert_state_consistent()

    def test_section_change_clears_previous_focus(self):
        """Changing sections clears visual focus from old section."""
        # Setup: Focus control in Emitter
        self.harness.click_control(Section.EMITTER, 0, 0)
        self.harness.assert_mode(NavigationMode.CONTROL)

        # Act: Navigate to Global
        self.harness.press_shortcut('G')

        # Assert: Emitter panel unfocused
        emitter = self.harness.get_panel_state(Section.EMITTER)
        self.assertFalse(emitter.panel_focused)
        self.assertFalse(emitter.in_control_mode)

        # Assert: Global panel focused
        global_panel = self.harness.get_panel_state(Section.GLOBAL)
        self.assertTrue(global_panel.panel_focused)

        # Assert: Mode reset
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.mode, NavigationMode.SECTION)

        self.harness.assert_state_consistent()

    def test_subsection_change_updates_panel_state(self):
        """Navigate subsections - panel state matches."""
        # Setup: Navigate to Global section
        self.harness.press_shortcut('G')
        self.harness.press_shortcut('F')  # Enter subsection mode

        # Navigate through subsections
        self.harness.press_shortcut('S')  # Next subsection (should be Reverb)

        nav = self.harness.get_nav_state()
        panel = self.harness.get_panel_state(Section.GLOBAL)

        # Subsection should match
        self.assertEqual(panel.focused_subsection, nav.subsection)
        self.harness.assert_state_consistent()

    def test_click_different_section_control(self):
        """Clicking control in different section switches sections."""
        # Setup: Focus Emitter
        self.harness.press_shortcut('E')

        # Act: Click on Global control
        self.harness.click_control(Section.GLOBAL, subsection=0, control=0)

        # Assert: Section switched to Global
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.GLOBAL)
        self.assertEqual(nav.mode, NavigationMode.CONTROL)

        # Emitter should be unfocused
        emitter = self.harness.get_panel_state(Section.EMITTER)
        self.assertFalse(emitter.panel_focused)

        self.harness.assert_state_consistent()

    def test_multiple_clicks_same_control(self):
        """Multiple clicks on same control maintain consistent state."""
        # Click same control multiple times
        for _ in range(3):
            self.harness.click_control(Section.EMITTER, subsection=0, control=1)
            self.harness.assert_state_consistent()

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.EMITTER)
        self.assertEqual(nav.subsection, 0)
        self.assertEqual(nav.control, 1)

    def test_click_while_in_control_mode_different_group(self):
        """Click on control in different subsection updates focus."""
        # Setup: Focus control in first group
        self.harness.click_control(Section.EMITTER, subsection=0, control=0)

        # Act: Click control in second group
        self.harness.click_control(Section.EMITTER, subsection=1, control=0)

        # Assert
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.subsection, 1)
        self.assertEqual(nav.control, 0)
        self.harness.assert_state_consistent()


class TestSectionFocusStyles(GUITestCase):
    """Tests for visual focus styling at section level."""

    def test_emitter_section_focus_style(self):
        """Emitter section shows focus styling when active."""
        self.harness.press_shortcut('E')

        panel = self.harness.get_panel_state(Section.EMITTER)
        self.assertTrue(panel.panel_focused)
        # Check stylesheet contains focus color
        from gui.styles import SECTION_ACTIVE_BORDER
        self.assertIn(SECTION_ACTIVE_BORDER, panel.stylesheet)

    def test_global_section_focus_style(self):
        """Global section shows focus styling when active."""
        self.harness.press_shortcut('G')

        panel = self.harness.get_panel_state(Section.GLOBAL)
        self.assertTrue(panel.panel_focused)
        from gui.styles import SECTION_ACTIVE_BORDER
        self.assertIn(SECTION_ACTIVE_BORDER, panel.stylesheet)

    def test_tracks_section_focus_style(self):
        """Tracks section shows focus styling when active."""
        self.harness.press_shortcut('T')

        panel = self.harness.get_panel_state(Section.TRACKS)
        self.assertTrue(panel.panel_focused)
        from gui.styles import SECTION_ACTIVE_BORDER
        self.assertIn(SECTION_ACTIVE_BORDER, panel.stylesheet)


if __name__ == '__main__':
    unittest.main()
