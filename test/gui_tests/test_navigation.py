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
        """Global subsection navigation includes modulator (subsection 5)."""
        # Navigate to Global
        self.harness.press_shortcut('G')
        self.harness.press_shortcut('F')

        # Navigate to modulator (subsection 5)
        for _ in range(5):
            self.harness.press_shortcut('S')

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.subsection, 5)
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

    def test_track_navigation_with_ws(self):
        """Track panel uses W/S for navigation through tracks (via NavigationManager)."""
        # Navigate to Tracks section
        self.harness.press_shortcut('T')
        self.harness.press_shortcut('F')  # Subsection mode

        initial = self.harness.get_nav_state().subsection

        # Navigate to next track with S key (now handled by NavigationManager)
        self.harness.press_shortcut('S')

        nav = self.harness.get_nav_state()
        # Should move to next track (subsection)
        self.assertEqual(nav.subsection, initial + 1)
        self.harness.assert_state_consistent()

    def test_track_navigation_in_control_mode(self):
        """W/S navigates between tracks even in CONTROL mode (since each track has 1 control)."""
        # Navigate to Tracks section and enter control mode
        self.harness.press_shortcut('T')
        self.harness.press_shortcut('F')  # Subsection mode
        self.harness.press_shortcut('F')  # Control mode
        self.harness.assert_mode(NavigationMode.CONTROL)

        initial = self.harness.get_nav_state().subsection

        # Navigate to next track with S key - should work even in CONTROL mode
        self.harness.press_shortcut('S')

        nav = self.harness.get_nav_state()
        # Should move to next track (subsection) even in CONTROL mode
        self.assertEqual(nav.subsection, initial + 1)
        # Mode should still be CONTROL
        self.harness.assert_mode(NavigationMode.CONTROL)

    def test_track_navigation_wraps_in_control_mode(self):
        """W/S wraps around tracks in CONTROL mode."""
        # Navigate to Tracks section, go to last track
        self.harness.press_shortcut('T')
        self.harness.press_shortcut('F')  # Subsection mode
        # Navigate to last track
        for _ in range(7):
            self.harness.press_shortcut('S')
        self.assertEqual(self.harness.get_nav_state().subsection, 7)

        self.harness.press_shortcut('F')  # Control mode

        # Try to go to next track - should stay at track 8 (clamped, not wrapped)
        self.harness.press_shortcut('S')
        self.assertEqual(self.harness.get_nav_state().subsection, 7)  # Still at last track


class TestMouseClickFocusHighlighting(GUITestCase):
    """Tests for mouse click vs keyboard focus highlighting."""

    def test_click_on_emitter_highlights_only_panel(self):
        """Clicking on Emitter section should highlight only panel, not subsections."""
        # Click on emitter panel (not on a specific control)
        self.harness.click_section(Section.EMITTER)

        # Verify panel is highlighted
        panel_state = self.harness.get_panel_state(Section.EMITTER)
        self.assertTrue(panel_state.panel_focused)

        # Verify NO subsections are highlighted
        subsection_states = self.harness.get_all_subsection_focused(Section.EMITTER)
        for i, is_focused in enumerate(subsection_states):
            self.assertFalse(is_focused, f"Subsection {i} should not be focused")

    def test_click_on_global_highlights_only_panel(self):
        """Clicking on Global section should highlight only panel, not subsections."""
        self.harness.click_section(Section.GLOBAL)

        panel_state = self.harness.get_panel_state(Section.GLOBAL)
        self.assertTrue(panel_state.panel_focused)

        subsection_states = self.harness.get_all_subsection_focused(Section.GLOBAL)
        for i, is_focused in enumerate(subsection_states):
            self.assertFalse(is_focused, f"Subsection {i} should not be focused")

    def test_keyboard_e_same_as_click_on_emitter(self):
        """Keyboard 'E' and mouse click should produce identical subsection states."""
        # Get state after keyboard
        self.harness.press_shortcut('E')
        keyboard_subsections = self.harness.get_all_subsection_focused(Section.EMITTER)

        # Reset to Grid
        self.harness.press_shortcut('Q')

        # Get state after mouse click
        self.harness.click_section(Section.EMITTER)
        mouse_subsections = self.harness.get_all_subsection_focused(Section.EMITTER)

        # All subsections should be unfocused in both cases
        self.assertEqual(keyboard_subsections, mouse_subsections)
        self.assertEqual(keyboard_subsections, [False, False, False, False])

    def test_click_on_fresh_state(self):
        """Clicking on section from fresh state should not highlight subsections."""
        # No prior navigation - this is the key test case for the bug
        self.harness.click_section(Section.EMITTER)

        subsection_states = self.harness.get_all_subsection_focused(Section.EMITTER)
        self.assertEqual(subsection_states, [False, False, False, False])

    def test_click_on_global_effects_container_not_highlighted(self):
        """Effects container QGroupBox should not inherit panel's blue border."""
        self.harness.click_section(Section.GLOBAL)

        # Verify panel is highlighted
        panel_state = self.harness.get_panel_state(Section.GLOBAL)
        self.assertTrue(panel_state.panel_focused)

        # Verify Effects container is NOT highlighted (has unfocused style)
        effects_group = self.harness.window._global_panel._effects_group
        stylesheet = effects_group.styleSheet()
        # Should have unfocused style (gray border), not empty or blue
        self.assertIn('#404040', stylesheet)  # Gray border color from unfocused style
        self.assertNotIn('#5AA0E9', stylesheet)  # Should NOT have blue border


class TestSubsectionClickFocus(GUITestCase):
    """Tests for clicking on subsection headers."""

    def test_click_subsection_enters_subsection_mode(self):
        """Clicking subsection header enters SUBSECTION mode."""
        self.harness.click_subsection(Section.EMITTER, 0)
        self.harness.assert_mode(NavigationMode.SUBSECTION)
        self.assertEqual(self.harness.get_nav_state().subsection, 0)

    def test_click_subsection_highlights_only_that_subsection(self):
        """Only clicked subsection is highlighted."""
        self.harness.click_subsection(Section.EMITTER, 2)
        subsections = self.harness.get_all_subsection_focused(Section.EMITTER)
        self.assertEqual(subsections, [False, False, True, False])

    def test_mixed_keyboard_click_sequence(self):
        """E -> click Grain -> F works correctly."""
        self.harness.press_shortcut('E')
        self.harness.click_subsection(Section.EMITTER, 2)  # Grain
        self.harness.assert_mode(NavigationMode.SUBSECTION)

        self.harness.press_shortcut('F')
        self.harness.assert_mode(NavigationMode.CONTROL)

    def test_keyboard_after_subsection_click(self):
        """W after subsection click moves to adjacent subsection."""
        self.harness.click_subsection(Section.EMITTER, 2)
        self.harness.press_shortcut('W')  # Move up
        self.assertEqual(self.harness.get_nav_state().subsection, 1)

    def test_click_different_subsection_changes_focus(self):
        """Clicking a different subsection changes focus."""
        self.harness.click_subsection(Section.EMITTER, 0)  # Basic
        self.assertEqual(self.harness.get_nav_state().subsection, 0)

        self.harness.click_subsection(Section.EMITTER, 3)  # Position
        self.assertEqual(self.harness.get_nav_state().subsection, 3)

        # Verify only Position is highlighted
        subsections = self.harness.get_all_subsection_focused(Section.EMITTER)
        self.assertEqual(subsections, [False, False, False, True])

    def test_click_global_subsection(self):
        """Clicking on Global subsection works correctly."""
        self.harness.click_subsection(Section.GLOBAL, 1)  # Reverb
        self.harness.assert_mode(NavigationMode.SUBSECTION)
        self.harness.assert_focus(Section.GLOBAL, subsection=1)


class TestSectionClickNavigation(GUITestCase):
    """Tests for section clicks updating NavigationManager."""

    def test_click_section_updates_nav_manager(self):
        """Clicking section updates NavigationManager state."""
        self.harness.press_shortcut('G')  # Global
        self.harness.click_section(Section.EMITTER)

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.EMITTER)
        self.harness.assert_mode(NavigationMode.SECTION)

    def test_click_section_resets_from_control_mode(self):
        """Clicking section resets from CONTROL mode."""
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')
        self.harness.press_shortcut('F')
        self.harness.assert_mode(NavigationMode.CONTROL)

        self.harness.click_section(Section.EMITTER)
        self.harness.assert_mode(NavigationMode.SECTION)

    def test_click_same_section_resets_mode(self):
        """Clicking current section resets to SECTION mode."""
        # Enter subsection mode
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')
        self.harness.assert_mode(NavigationMode.SUBSECTION)

        # Click on same section
        self.harness.click_section(Section.EMITTER)
        self.harness.assert_mode(NavigationMode.SECTION)

    def test_click_different_section_changes_focus(self):
        """Clicking different section changes to that section."""
        self.harness.press_shortcut('E')  # Emitter
        self.harness.click_section(Section.GLOBAL)

        nav = self.harness.get_nav_state()
        self.assertEqual(nav.section, Section.GLOBAL)
        self.harness.assert_mode(NavigationMode.SECTION)

    def test_click_section_clears_subsection_highlighting(self):
        """Clicking section clears any subsection highlighting."""
        # First enter subsection mode
        self.harness.press_shortcut('E')
        self.harness.press_shortcut('F')
        # Verify subsection is highlighted
        subsections = self.harness.get_all_subsection_focused(Section.EMITTER)
        self.assertTrue(any(subsections))

        # Click section - should clear subsection highlighting
        self.harness.click_section(Section.EMITTER)
        subsections = self.harness.get_all_subsection_focused(Section.EMITTER)
        self.assertEqual(subsections, [False, False, False, False])


class TestValueAdjustment(GUITestCase):
    """Tests for value adjustment via A/D keys."""

    def test_value_adjust_in_control_mode(self):
        """A/D adjusts value when in CONTROL mode."""
        # Navigate to Global > ADSR > Attack
        self.harness.press_shortcut('G')
        self.harness.press_shortcut('F')  # Subsection mode
        self.harness.press_shortcut('F')  # Control mode
        self.harness.assert_mode(NavigationMode.CONTROL)

        # Get initial value
        global_params = self.harness.window._global_panel.get_all_parameters()
        initial_value = global_params['adsr']['attack']

        # Press D to increase
        self.harness.press_shortcut('D')

        # Check value increased
        global_params = self.harness.window._global_panel.get_all_parameters()
        self.assertEqual(global_params['adsr']['attack'], initial_value + 1)

    def test_value_adjust_not_in_subsection_mode(self):
        """A/D does not adjust value when in SUBSECTION mode."""
        # Navigate to Global > ADSR in SUBSECTION mode (not CONTROL)
        self.harness.press_shortcut('G')
        self.harness.press_shortcut('F')  # Subsection mode
        self.harness.assert_mode(NavigationMode.SUBSECTION)

        # Get initial value
        global_params = self.harness.window._global_panel.get_all_parameters()
        initial_value = global_params['adsr']['attack']

        # Press D - should NOT change value
        self.harness.press_shortcut('D')

        # Check value unchanged
        global_params = self.harness.window._global_panel.get_all_parameters()
        self.assertEqual(global_params['adsr']['attack'], initial_value)

    def test_modulator_slider_value_adjust(self):
        """A/D adjusts modulator slider value."""
        # Navigate to Global > Modulator (subsection 5)
        self.harness.press_shortcut('G')
        self.harness.press_shortcut('F')  # Subsection mode
        # Navigate to Modulator (subsection 5)
        for _ in range(5):
            self.harness.press_shortcut('S')
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.subsection, 5)

        # Enter control mode, navigate to slider (control 1)
        self.harness.press_shortcut('F')  # Control mode
        self.harness.press_shortcut('S')  # Move to slider (control 1)
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.control, 1)

        # Get initial size
        initial_size = self.harness.window._global_panel.get_modulator_size()

        # Press D to increase
        self.harness.press_shortcut('D')

        # Check size increased
        self.assertEqual(self.harness.window._global_panel.get_modulator_size(), initial_size + 1)

    def test_modulator_dropdown_value_adjust(self):
        """A/D adjusts modulator dropdown selection."""
        # Navigate to Global > Modulator (subsection 5)
        self.harness.press_shortcut('G')
        self.harness.press_shortcut('F')  # Subsection mode
        # Navigate to Modulator (subsection 5)
        for _ in range(5):
            self.harness.press_shortcut('S')

        # Enter control mode - starts at control 0 (dropdown)
        self.harness.press_shortcut('F')
        nav = self.harness.get_nav_state()
        self.assertEqual(nav.control, 0)

        # Get initial modulator selection
        initial_mod = self.harness.window._global_panel.get_modulator_selected()

        # Press D to increase selection
        self.harness.press_shortcut('D')

        # Check modulator selection increased
        self.assertEqual(self.harness.window._global_panel.get_modulator_selected(), initial_mod + 1)

    def test_track_value_adjust(self):
        """A/D adjusts track volume."""
        # Navigate to Track section
        self.harness.press_shortcut('T')
        self.harness.press_shortcut('F')  # Subsection mode (track 1)
        self.harness.press_shortcut('F')  # Control mode
        self.harness.assert_mode(NavigationMode.CONTROL)

        # Get initial volume
        initial_volume = self.harness.window._track_panel.get_volume(1)

        # Press D to increase
        self.harness.press_shortcut('D')

        # Check volume increased
        self.assertEqual(self.harness.window._track_panel.get_volume(1), initial_volume + 1)


if __name__ == '__main__':
    unittest.main()
