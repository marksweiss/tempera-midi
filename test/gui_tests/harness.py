"""GUI Test Harness for Tempera MIDI Controller.

This module provides the main test orchestrator for testing UI interaction logic.
It enables sending events (keyboard, mouse), inspecting state at all layers,
and asserting state consistency.
"""

from typing import Optional

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from gui.shortcuts import Section, NavigationMode
from gui.styles import SECTION_ACTIVE_BORDER, FOCUS_GLOW
from test.gui_tests.state import NavState, PanelState, SliderGroupState, EnvelopePanelState
from test.gui_tests.mocks import MockTemperaAdapter


class GUITestHarness:
    """Main test orchestrator for GUI testing.

    Provides methods for:
    - Lifecycle management (setup/teardown)
    - Event simulation (keyboard, mouse)
    - State inspection (nav, panel, slider group, envelope)
    - Assertions (focus, mode, consistency)
    """

    def __init__(self):
        self._adapter: Optional[MockTemperaAdapter] = None
        self._window: Optional['MainWindow'] = None

    def setup(self) -> None:
        """Initialize the test environment with a MainWindow and mock adapter."""
        from gui.app import MainWindow

        self._adapter = MockTemperaAdapter()
        self._window = MainWindow(self._adapter)
        self._window.show()
        self.process_events()

    def teardown(self) -> None:
        """Clean up the test environment."""
        if self._window:
            self._window.close()
            self._window.deleteLater()
            self._window = None
        self._adapter = None
        self.process_events()

    # ---- Event Simulation ----

    def press_key(self, key: Qt.Key,
                  modifiers: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier) -> None:
        """Simulate a key press event.

        Args:
            key: The Qt key code to press
            modifiers: Optional keyboard modifiers (Ctrl, Shift, etc.)
        """
        # Create and send key press event
        press_event = QKeyEvent(QEvent.Type.KeyPress, key, modifiers)
        target = QApplication.focusWidget() or self._window
        QApplication.sendEvent(target, press_event)

        # Create and send key release event
        release_event = QKeyEvent(QEvent.Type.KeyRelease, key, modifiers)
        QApplication.sendEvent(target, release_event)

        self.process_events()

    def press_shortcut(self, shortcut: str) -> None:
        """Simulate a keyboard shortcut by string (e.g., "Q", "Ctrl+Z").

        Args:
            shortcut: Shortcut string like "Q", "G", "Ctrl+Z", "Shift+Tab"
        """
        parts = shortcut.upper().split('+')

        modifiers = Qt.KeyboardModifier.NoModifier
        key = None

        for part in parts:
            if part == 'CTRL':
                modifiers |= Qt.KeyboardModifier.ControlModifier
            elif part == 'SHIFT':
                modifiers |= Qt.KeyboardModifier.ShiftModifier
            elif part == 'ALT':
                modifiers |= Qt.KeyboardModifier.AltModifier
            elif part == 'META' or part == 'CMD':
                modifiers |= Qt.KeyboardModifier.MetaModifier
            else:
                # Map common key names
                key_map = {
                    'TAB': Qt.Key.Key_Tab,
                    'RETURN': Qt.Key.Key_Return,
                    'ENTER': Qt.Key.Key_Return,
                    'ESCAPE': Qt.Key.Key_Escape,
                    'ESC': Qt.Key.Key_Escape,
                    'SPACE': Qt.Key.Key_Space,
                    'UP': Qt.Key.Key_Up,
                    'DOWN': Qt.Key.Key_Down,
                    'LEFT': Qt.Key.Key_Left,
                    'RIGHT': Qt.Key.Key_Right,
                    'BACKSPACE': Qt.Key.Key_Backspace,
                    'DELETE': Qt.Key.Key_Delete,
                }

                if part in key_map:
                    key = key_map[part]
                elif len(part) == 1:
                    # Single character - map to Qt.Key
                    key = getattr(Qt.Key, f'Key_{part}', None)
                else:
                    # Try direct mapping
                    key = getattr(Qt.Key, f'Key_{part}', None)

        if key is None:
            raise ValueError(f"Unknown key in shortcut: {shortcut}")

        self.press_key(key, modifiers)

    def click_control(self, section: Section, subsection: int, control: int) -> None:
        """Simulate clicking on a specific control.

        This emits the controlFocusRequested signal which triggers
        NavigationManager.focus_control() to update state.

        Args:
            section: The section containing the control
            subsection: Subsection index within the section (0-based)
            control: Control index within the subsection (0-based)
        """
        panel = self._get_panel(section)
        if panel is None:
            raise ValueError(f"No panel for section: {section}")

        if section == Section.TRACKS:
            # Track panel uses controlFocusRequested signal directly
            # subsection is the track index (0-based), control is always 0
            track_num = subsection + 1  # Convert to 1-based for validation
            if 1 <= track_num <= 8:
                # Emit the signal that track panel would emit on click
                panel.controlFocusRequested.emit(subsection, 0)
        elif section == Section.GLOBAL and subsection == 4:
            # Global modulator - emit controlFocusRequested with the control index
            # control 0 = dropdown, control 1 = slider
            panel.controlFocusRequested.emit(4, control)
        else:
            # Standard panel with slider groups - emit controlFocusRequested
            panel.controlFocusRequested.emit(subsection, control)

        self.process_events()

    def click_section(self, section: Section) -> None:
        """Simulate clicking on a section panel (not on a specific control).

        This triggers panel focus without entering control mode, similar to
        clicking on empty space within a panel.
        """
        panel = self._get_panel(section)
        if panel is None:
            raise ValueError(f"No panel for section: {section}")

        if section == Section.GRID:
            # CellGrid doesn't have sectionClicked signal
            panel.setFocus()
        else:
            # Emit the sectionClicked signal that panel.mousePressEvent would emit
            # This simulates clicking on empty space within the panel
            panel.sectionClicked.emit()
        self.process_events()

    def click_subsection(self, section: Section, subsection: int) -> None:
        """Simulate clicking on a subsection header.

        This triggers subsection focus (SUBSECTION mode), similar to clicking
        on a SliderGroup's header or empty area.

        Args:
            section: The section containing the subsection
            subsection: Subsection index within the section (0-based)
        """
        panel = self._get_panel(section)
        if panel is None:
            raise ValueError(f"No panel for section: {section}")

        if section == Section.TRACKS:
            raise ValueError("TrackPanel does not have subsections with headers")

        # Emit the subsectionFocusRequested signal that SliderGroup.mousePressEvent would emit
        panel.subsectionFocusRequested.emit(subsection)
        self.process_events()

    def get_all_subsection_focused(self, section: Section) -> list[bool]:
        """Get focused state of all subsections in a section.

        Returns a list of booleans indicating which subsections have
        their visual focus style applied (blue border).
        """
        panel = self._get_panel(section)
        if section == Section.TRACKS:
            return []  # Tracks don't have subsection groups

        groups = panel.slider_groups
        return [group._group_focused for group in groups]

    def select_modulator(self, modulator_num: int) -> None:
        """Select a modulator (1-10) in the Global panel.

        This updates the state manager's selected modulator and triggers
        the envelope panel update.

        Args:
            modulator_num: Modulator number (1-10)
        """
        if not 1 <= modulator_num <= 10:
            raise ValueError(f"Modulator number must be 1-10, got {modulator_num}")

        # Update state directly
        self._adapter.state.set_modulator_selected(modulator_num)

        # Trigger envelope panel update through the window's handler
        self._window._on_modulator_selected(modulator_num)

        self.process_events()

    # ---- State Inspection ----

    def get_nav_state(self) -> NavState:
        """Get current NavigationManager state."""
        nav = self._window._nav
        return NavState(
            section=nav.section,
            subsection=nav.subsection,
            control=nav.control,
            mode=nav.mode
        )

    def get_panel_state(self, section: Section) -> PanelState:
        """Get visual state of a panel.

        Args:
            section: The section whose panel state to retrieve
        """
        panel = self._get_panel(section)
        if panel is None:
            raise ValueError(f"No panel for section: {section}")

        # Get common panel state
        panel_focused = getattr(panel, '_panel_focused', False)

        # Handle different panel types
        if section == Section.TRACKS:
            visual_track = getattr(panel, '_visual_track', -1)
            # Convert from 1-based track to 0-based subsection
            visual_subsection = visual_track - 1 if visual_track > 0 else -1
            # TrackPanel doesn't have separate control focus - use -1 as placeholder
            # The harness will skip control mode check for TRACKS section
            visual_control = -1
        else:
            visual_subsection = getattr(panel, '_visual_subsection', -1)
            visual_control = getattr(panel, '_visual_control', -1)

        return PanelState(
            panel_focused=panel_focused,
            visual_subsection=visual_subsection,
            visual_control=visual_control,
            stylesheet=panel.styleSheet()
        )

    def get_slider_group_state(self, section: Section, subsection: int) -> SliderGroupState:
        """Get focus state of a slider group.

        Args:
            section: The section containing the group
            subsection: Subsection index of the group
        """
        panel = self._get_panel(section)
        if panel is None:
            raise ValueError(f"No panel for section: {section}")

        if section == Section.TRACKS:
            # Track panel uses _sliders dict keyed by track number (1-8)
            # and _focused_track to track which is focused
            sliders = panel._sliders  # dict[int, QSlider]
            focused_track = getattr(panel, '_focused_track', -1)
            # Convert 1-based track to 0-based index for consistency
            focused_index = focused_track - 1 if focused_track > 0 else -1
            return SliderGroupState(
                group_focused=panel._panel_focused and panel._in_control_mode,
                focused_index=focused_index,
                slider_count=len(sliders),
                stylesheet=panel.styleSheet()
            )

        if section == Section.GLOBAL and subsection == 4:
            # Modwheel is a single slider, not a group
            modwheel = panel._modwheel
            focused = getattr(modwheel, '_focused', False)
            return SliderGroupState(
                group_focused=panel._panel_focused and panel._focused_subsection == 4,
                focused_index=0 if focused else -1,
                slider_count=1,
                stylesheet=modwheel.styleSheet()
            )

        groups = panel.slider_groups
        if 0 <= subsection < len(groups):
            group = groups[subsection]
            return SliderGroupState(
                group_focused=getattr(group, '_group_focused', False),
                focused_index=getattr(group, '_focused_index', -1),
                slider_count=len(group._sliders),
                stylesheet=group.styleSheet()
            )

        raise ValueError(f"Invalid subsection {subsection} for section {section}")

    def get_envelope_panel_state(self) -> EnvelopePanelState:
        """Get current EnvelopePanel state."""
        envelope_panel = self._window._envelope_panel

        control_key = envelope_panel._current_control_key
        envelope = envelope_panel._current_envelope

        # Get display name from label
        display_name = envelope_panel._label.text()
        if display_name == 'No Control Selected':
            display_name = None

        enabled = envelope_panel._toggle_btn.isChecked() if envelope else False
        has_envelope = envelope is not None and not envelope.is_empty() if envelope else False

        return EnvelopePanelState(
            control_key=control_key,
            display_name=display_name,
            enabled=enabled,
            has_envelope=has_envelope
        )

    # ---- Assertions ----

    def assert_focus(self, section: Section, subsection: int = None,
                     control: int = None) -> None:
        """Assert NavigationManager focus is at the specified location.

        Args:
            section: Expected section
            subsection: Expected subsection (optional)
            control: Expected control (optional)
        """
        nav = self.get_nav_state()

        if nav.section != section:
            raise AssertionError(
                f"Expected section {section}, got {nav.section}"
            )

        if subsection is not None and nav.subsection != subsection:
            raise AssertionError(
                f"Expected subsection {subsection}, got {nav.subsection}"
            )

        if control is not None and nav.control != control:
            raise AssertionError(
                f"Expected control {control}, got {nav.control}"
            )

    def assert_mode(self, mode: NavigationMode) -> None:
        """Assert NavigationManager is in the specified mode."""
        nav = self.get_nav_state()
        if nav.mode != mode:
            raise AssertionError(f"Expected mode {mode}, got {nav.mode}")

    def assert_visual_focus(self, section: Section,
                            group: int = None, slider: int = None) -> None:
        """Assert visual focus styling is applied correctly.

        Args:
            section: Section that should have panel focus styling
            group: Group index that should have focus styling (optional)
            slider: Slider index that should have focus styling (optional)
        """
        panel_state = self.get_panel_state(section)

        # Check panel has focus border
        if SECTION_ACTIVE_BORDER not in panel_state.stylesheet:
            raise AssertionError(
                f"Panel for {section} missing focus border style"
            )

        if group is not None:
            group_state = self.get_slider_group_state(section, group)
            if SECTION_ACTIVE_BORDER not in group_state.stylesheet:
                raise AssertionError(
                    f"Group {group} in {section} missing focus border style"
                )

            if slider is not None:
                # Check slider has focus glow - need to inspect the actual slider
                panel = self._get_panel(section)
                groups = panel.slider_groups
                if 0 <= group < len(groups):
                    grp = groups[group]
                    slider_names = list(grp._sliders.keys())
                    if 0 <= slider < len(slider_names):
                        slider_widget = grp._sliders[slider_names[slider]]
                        slider_style = slider_widget._slider.styleSheet()
                        if FOCUS_GLOW not in slider_style:
                            raise AssertionError(
                                f"Slider {slider} in group {group} missing focus glow"
                            )

    def assert_envelope_shows(self, control_key: str, display_name: str) -> None:
        """Assert the envelope panel is showing the specified control.

        Args:
            control_key: Expected control key (e.g., "emitter.1.volume")
            display_name: Expected display name (e.g., "Emitter 1 - Volume")
        """
        state = self.get_envelope_panel_state()

        if state.control_key != control_key:
            raise AssertionError(
                f"Expected envelope control_key '{control_key}', got '{state.control_key}'"
            )

        if state.display_name != display_name:
            raise AssertionError(
                f"Expected envelope display_name '{display_name}', got '{state.display_name}'"
            )

    def assert_state_consistent(self) -> None:
        """Assert state is consistent across all layers.

        This is the KEY assertion that catches state synchronization bugs.
        Since panels are now purely reactive to NavigationManager signals,
        we verify:
        1. Panel focus matches NavigationManager section
        2. Visual subsection matches NavigationManager subsection (when applicable)
        3. Visual control matches NavigationManager control (when in CONTROL mode)
        4. If in control mode, slider group/slider focus matches
        5. Envelope panel shows the focused control (if in CONTROL mode)
        """
        nav = self.get_nav_state()
        errors = []

        # GRID section is handled differently - it uses CellGrid, not standard panels
        if nav.section == Section.GRID:
            # For GRID section, just verify other panels are not focused
            for other_section in [Section.EMITTER, Section.TRACKS, Section.GLOBAL]:
                try:
                    other_panel = self.get_panel_state(other_section)
                    if other_panel.panel_focused:
                        errors.append(f"Section {other_section} panel focused but nav is GRID")
                except ValueError:
                    pass
            if errors:
                raise AssertionError("State inconsistent:\n" + "\n".join(errors))
            return

        # 1. Panel focus matches section
        panel = self.get_panel_state(nav.section)
        if not panel.panel_focused:
            errors.append(f"Section is {nav.section} but panel not focused")

        # 2. Verify other panels are NOT focused
        for other_section in Section:
            if other_section != nav.section and other_section != Section.GRID:
                try:
                    other_panel = self.get_panel_state(other_section)
                    if other_panel.panel_focused:
                        errors.append(f"Section {other_section} panel focused but nav is {nav.section}")
                except ValueError:
                    pass

        # 3. Visual subsection matches (only check if in subsection/control/value mode)
        if nav.mode in (NavigationMode.SUBSECTION, NavigationMode.CONTROL, NavigationMode.VALUE):
            if panel.visual_subsection != nav.subsection:
                errors.append(
                    f"Nav subsection={nav.subsection}, panel visual_subsection={panel.visual_subsection}"
                )

        # 4. Visual control mode matches (skip for TRACKS - it uses subsection=track model)
        if nav.section != Section.TRACKS:
            expected_in_control = nav.mode in (NavigationMode.CONTROL, NavigationMode.VALUE)
            actual_in_control = panel.visual_control >= 0
            if actual_in_control != expected_in_control:
                errors.append(
                    f"Nav mode={nav.mode}, expected visual_control>=0={expected_in_control}, "
                    f"got visual_control={panel.visual_control}"
                )

        # 5. If in control mode, verify slider group/slider focus
        # (Skip for TRACKS since tracks use subsection=track, not control within track)
        if nav.mode == NavigationMode.CONTROL and nav.section != Section.TRACKS:
            try:
                group = self.get_slider_group_state(nav.section, nav.subsection)
                if group.focused_index != nav.control:
                    errors.append(
                        f"Nav control={nav.control}, group focused_index={group.focused_index}"
                    )
            except (ValueError, AttributeError):
                pass  # Some subsections may not have groups

        # 6. Verify envelope panel shows focused control (if in control mode)
        if nav.mode == NavigationMode.CONTROL:
            envelope = self.get_envelope_panel_state()
            expected_key = self._compute_expected_control_key(nav)
            if expected_key and envelope.control_key != expected_key:
                errors.append(
                    f"Expected envelope for '{expected_key}', got '{envelope.control_key}'"
                )

        if errors:
            raise AssertionError("State inconsistent:\n" + "\n".join(errors))

    # ---- Qt Event Processing ----

    def process_events(self) -> None:
        """Process pending Qt events."""
        QApplication.processEvents()

    # ---- Helper Methods ----

    def _get_panel(self, section: Section):
        """Get the panel widget for a section."""
        if section == Section.EMITTER:
            return self._window._emitter_panel
        elif section == Section.TRACKS:
            return self._window._track_panel
        elif section == Section.GLOBAL:
            return self._window._global_panel
        elif section == Section.GRID:
            return self._window._cell_grid
        return None

    def _compute_expected_control_key(self, nav: NavState) -> Optional[str]:
        """Compute the expected control key for a given nav state.

        This replicates the logic in MainWindow._get_focused_control_key()
        for test verification.
        """
        if nav.section == Section.EMITTER:
            emitter_num = self._adapter.state.get_active_emitter()
            # Map subsection + control to parameter
            # Subsection 0: Basic (volume, octave, effects_send)
            # Subsection 1: Tone Filter (tone_filter_width, tone_filter_center)
            # Subsection 2: Grain (grain_length_cell, grain_length_note, grain_density,
            #                      grain_shape, grain_shape_attack, grain_pan, grain_tune_spread)
            # Subsection 3: Position/Spray (relative_x, relative_y, spray_x, spray_y)
            params_by_subsection = [
                ['volume', 'octave', 'effects_send'],
                ['tone_filter_width', 'tone_filter_center'],
                ['grain_length_cell', 'grain_length_note', 'grain_density',
                 'grain_shape', 'grain_shape_attack', 'grain_pan', 'grain_tune_spread'],
                ['relative_x', 'relative_y', 'spray_x', 'spray_y'],
            ]
            if 0 <= nav.subsection < len(params_by_subsection):
                params = params_by_subsection[nav.subsection]
                if 0 <= nav.control < len(params):
                    return f'emitter.{emitter_num}.{params[nav.control]}'

        elif nav.section == Section.TRACKS:
            track_num = nav.subsection + 1
            if 1 <= track_num <= 8:
                return f'track.{track_num}.volume'

        elif nav.section == Section.GLOBAL:
            # Special handling for modulator subsection (index 4)
            # Both controls (dropdown and slider) show envelope for selected modulator
            if nav.subsection == 4:
                selected_mod = self._adapter.state.get_modulator_selected()
                return f'global.modulator.{selected_mod}.size'

            # Map subsection + control to global parameter
            params_by_subsection = [
                # ADSR
                [('adsr', 'attack'), ('adsr', 'decay'), ('adsr', 'sustain'), ('adsr', 'release')],
                # Reverb
                [('reverb', 'size'), ('reverb', 'color'), ('reverb', 'mix')],
                # Delay
                [('delay', 'feedback'), ('delay', 'time'), ('delay', 'color'), ('delay', 'mix')],
                # Chorus
                [('chorus', 'depth'), ('chorus', 'speed'), ('chorus', 'flange'), ('chorus', 'mix')],
            ]
            if 0 <= nav.subsection < len(params_by_subsection):
                params = params_by_subsection[nav.subsection]
                if 0 <= nav.control < len(params):
                    category, param = params[nav.control]
                    if param:
                        return f'global.{category}.{param}'
                    return f'global.{category}'

        return None

    @property
    def adapter(self) -> MockTemperaAdapter:
        """Get the mock adapter for state inspection."""
        return self._adapter

    @property
    def window(self):
        """Get the main window for direct access if needed."""
        return self._window
