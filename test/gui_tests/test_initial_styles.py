"""Tests for initial stylesheet setup to prevent layout shifts.

These tests verify that panels and their nested widgets have explicit
stylesheets set at initialization, preventing layout jumps on first
focus/unfocus transitions.
"""

import unittest
from test.gui_tests.base import GUITestCase
from gui.styles import get_section_focus_style, get_subsection_focus_style, get_slider_focus_style, get_combobox_focus_style


class TestPanelInitialStyles(GUITestCase):
    """Tests that panels have explicit stylesheets set at initialization."""

    def test_global_panel_has_initial_style(self):
        """GlobalPanel has explicit unfocused stylesheet set."""
        panel = self.harness._window._global_panel
        stylesheet = panel.styleSheet()
        expected = get_section_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "GlobalPanel should have unfocused style at init")

    def test_track_panel_has_initial_style(self):
        """TrackPanel has explicit unfocused stylesheet set."""
        panel = self.harness._window._track_panel
        stylesheet = panel.styleSheet()
        expected = get_section_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "TrackPanel should have unfocused style at init")

    def test_emitter_panel_has_initial_style(self):
        """EmitterPanel has explicit unfocused stylesheet set."""
        panel = self.harness._window._emitter_panel
        stylesheet = panel.styleSheet()
        expected = get_section_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "EmitterPanel should have unfocused style at init")


class TestGlobalPanelNestedStyles(GUITestCase):
    """Tests that GlobalPanel nested widgets have explicit stylesheets."""

    def test_adsr_group_has_initial_style(self):
        """ADSR group has explicit unfocused stylesheet set."""
        panel = self.harness._window._global_panel
        group = panel._adsr_group
        stylesheet = group.styleSheet()
        expected = get_subsection_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "ADSR group should have unfocused style at init")

    def test_effects_group_has_initial_style(self):
        """Effects group has explicit unfocused stylesheet set."""
        panel = self.harness._window._global_panel
        group = panel._effects_group
        stylesheet = group.styleSheet()
        expected = get_subsection_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "Effects group should have unfocused style at init")

    def test_modulator_group_has_initial_style(self):
        """Modulator group has explicit unfocused stylesheet set."""
        panel = self.harness._window._global_panel
        group = panel._modulator_group
        stylesheet = group.styleSheet()
        expected = get_subsection_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "Modulator group should have unfocused style at init")

    def test_modulator_slider_has_initial_style(self):
        """Modulator slider has explicit unfocused stylesheet set."""
        panel = self.harness._window._global_panel
        slider = panel._modulator_slider
        stylesheet = slider.styleSheet()
        expected = get_slider_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "Modulator slider should have unfocused style at init")

    def test_modulator_selector_has_initial_style(self):
        """Modulator selector dropdown has explicit unfocused stylesheet set."""
        panel = self.harness._window._global_panel
        selector = panel._modulator_selector
        stylesheet = selector.styleSheet()
        expected = get_combobox_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "Modulator selector should have unfocused style at init")


class TestEmitterPanelNestedStyles(GUITestCase):
    """Tests that EmitterPanel nested widgets have explicit stylesheets."""

    def test_basic_group_has_initial_style(self):
        """Basic group has explicit unfocused stylesheet set."""
        panel = self.harness._window._emitter_panel
        group = panel._basic_group
        stylesheet = group.styleSheet()
        expected = get_subsection_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "Basic group should have unfocused style at init")

    def test_grain_group_has_initial_style(self):
        """Grain group has explicit unfocused stylesheet set."""
        panel = self.harness._window._emitter_panel
        group = panel._grain_group
        stylesheet = group.styleSheet()
        expected = get_subsection_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "Grain group should have unfocused style at init")

    def test_position_group_has_initial_style(self):
        """Position group has explicit unfocused stylesheet set."""
        panel = self.harness._window._emitter_panel
        group = panel._position_group
        stylesheet = group.styleSheet()
        expected = get_subsection_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "Position group should have unfocused style at init")

    def test_filter_group_has_initial_style(self):
        """Filter group has explicit unfocused stylesheet set."""
        panel = self.harness._window._emitter_panel
        group = panel._filter_group
        stylesheet = group.styleSheet()
        expected = get_subsection_focus_style(False)
        self.assertEqual(stylesheet.strip(), expected.strip(),
                         "Filter group should have unfocused style at init")


class TestTrackPanelNestedStyles(GUITestCase):
    """Tests that TrackPanel nested widgets have explicit stylesheets."""

    def test_track_sliders_have_initial_style(self):
        """All track sliders have explicit unfocused stylesheet set."""
        panel = self.harness._window._track_panel
        expected = get_slider_focus_style(False)

        for track_num in range(1, 9):
            slider = panel._sliders[track_num]
            stylesheet = slider.styleSheet()
            self.assertEqual(stylesheet.strip(), expected.strip(),
                             f"Track {track_num} slider should have unfocused style at init")


class TestStyleConsistencyOnFocusChange(GUITestCase):
    """Tests that styles remain consistent through focus transitions."""

    def test_global_panel_no_shift_on_first_focus(self):
        """GlobalPanel border doesn't change size on first focus."""
        panel = self.harness._window._global_panel
        initial_style = panel.styleSheet()

        # Focus the panel
        self.harness.press_shortcut('G')
        self.harness.process_events()

        # The border width should remain 2px (only color changes)
        focused_style = panel.styleSheet()
        self.assertIn('border: 2px', focused_style,
                      "Focused GlobalPanel should have 2px border")

    def test_global_panel_no_shift_on_first_unfocus(self):
        """GlobalPanel nested groups don't shift on first unfocus."""
        panel = self.harness._window._global_panel

        # Focus the panel
        self.harness.press_shortcut('G')
        self.harness.process_events()

        # Unfocus by going to Tracks
        self.harness.press_shortcut('T')
        self.harness.process_events()

        # Verify nested groups still have 2px borders
        for group in [panel._adsr_group, panel._effects_group, panel._modulator_group]:
            style = group.styleSheet()
            self.assertIn('border: 2px', style,
                          f"{group.title()} should maintain 2px border after unfocus")

    def test_track_panel_no_shift_on_first_focus(self):
        """TrackPanel border doesn't change size on first focus."""
        panel = self.harness._window._track_panel

        # Focus the panel
        self.harness.press_shortcut('T')
        self.harness.process_events()

        # The border width should remain 2px
        focused_style = panel.styleSheet()
        self.assertIn('border: 2px', focused_style,
                      "Focused TrackPanel should have 2px border")

    def test_emitter_panel_no_shift_on_first_focus(self):
        """EmitterPanel border doesn't change size on first focus."""
        panel = self.harness._window._emitter_panel

        # Focus the panel
        self.harness.press_shortcut('E')
        self.harness.process_events()

        # The border width should remain 2px
        focused_style = panel.styleSheet()
        self.assertIn('border: 2px', focused_style,
                      "Focused EmitterPanel should have 2px border")


if __name__ == '__main__':
    unittest.main()
