"""Emitter controls panel with all parameter sliders."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QFocusEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QButtonGroup,
    QScrollArea, QFrame, QGridLayout, QGroupBox, QApplication
)

from gui.widgets.slider_group import SliderGroup
from gui.styles import get_emitter_button_style, EMITTER_COLORS, get_section_focus_style


# Parameter definitions for each slider group
BASIC_PARAMS = [
    {'name': 'volume', 'label': 'Volume', 'default': 100},
    {'name': 'octave', 'label': 'Octave', 'default': 64},
    {'name': 'effects_send', 'label': 'Effects Send', 'default': 0},
]

GRAIN_PARAMS = [
    {'name': 'grain_length_cell', 'label': 'Length Cell', 'default': 64},
    {'name': 'grain_length_note', 'label': 'Length Note', 'default': 64},
    {'name': 'grain_density', 'label': 'Density', 'default': 64},
    {'name': 'grain_shape', 'label': 'Shape', 'default': 64},
    {'name': 'grain_shape_attack', 'label': 'Shape Attack', 'default': 64},
    {'name': 'grain_pan', 'label': 'Pan', 'default': 64},
    {'name': 'grain_tune_spread', 'label': 'Tune Spread', 'default': 64},
]

POSITION_PARAMS = [
    {'name': 'relative_x', 'label': 'Position X', 'default': 64},
    {'name': 'relative_y', 'label': 'Position Y', 'default': 64},
    {'name': 'spray_x', 'label': 'Spray X', 'default': 0},
    {'name': 'spray_y', 'label': 'Spray Y', 'default': 0},
]

FILTER_PARAMS = [
    {'name': 'tone_filter_width', 'label': 'Filter Width', 'default': 127},
    {'name': 'tone_filter_center', 'label': 'Filter Center', 'default': 64},
]


class EmitterPanel(QGroupBox):
    """
    Panel for controlling all parameters of the 4 emitters.

    Features:
    - Emitter selection buttons (1-4) with color coding
    - Slider groups for basic, grain, position, and filter parameters
    - All sliders update when emitter selection changes

    Signals:
        emitterSelected(int): Emitted when emitter selection changes
        parameterChanged(int, str, int): Emitted on slider change (emitter, param, value)
        parameterSet(int, str, int): Emitted on slider release (emitter, param, value)
        controlFocusRequested(int, int): Emitted when a control is clicked (subsection_index, control_index)
    """

    emitterSelected = Signal(int)
    parameterChanged = Signal(int, str, int)
    parameterSet = Signal(int, str, int)
    controlFocusRequested = Signal(int, int)
    # Signals for keyboard navigation within panel
    subsectionNavigated = Signal(int)  # Emitted when subsection changes via keyboard (new index)
    controlNavigated = Signal(int)  # Emitted when control changes via keyboard (new index)

    def __init__(self, parent: QWidget = None):
        super().__init__('Emitter', parent)

        self._current_emitter = 1
        self._panel_focused = False
        self._focused_subsection = 0  # Currently focused subsection (0-3)
        self._in_control_mode = False  # Whether we're navigating controls within a subsection

        # Store values for all emitters
        self._emitter_values: dict[int, dict[str, int]] = {
            i: self._get_default_values() for i in range(1, 5)
        }

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._setup_ui()

    def _get_default_values(self) -> dict[str, int]:
        """Get default values for all parameters."""
        values = {}
        for param in BASIC_PARAMS + GRAIN_PARAMS + POSITION_PARAMS + FILTER_PARAMS:
            values[param['name']] = param.get('default', 64)
        return values

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Emitter selection buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self._emitter_buttons: dict[int, QPushButton] = {}
        self._button_group = QButtonGroup(self)

        for i in range(1, 5):
            btn = QPushButton(f'{i}')
            btn.setFixedSize(40, 32)
            btn.setCheckable(True)
            btn.setStyleSheet(get_emitter_button_style(i, selected=(i == 1)))
            self._button_group.addButton(btn, i)
            self._emitter_buttons[i] = btn
            button_layout.addWidget(btn)

        self._emitter_buttons[1].setChecked(True)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Scroll area for sliders
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(12)

        # Create slider groups
        self._basic_group = SliderGroup('Basic', BASIC_PARAMS, label_width=90)
        self._grain_group = SliderGroup('Grain', GRAIN_PARAMS, label_width=90)
        self._position_group = SliderGroup('Position / Spray', POSITION_PARAMS, label_width=90)
        self._filter_group = SliderGroup('Tone Filter', FILTER_PARAMS, label_width=90)

        # Arrange in 2x2 grid:
        # Row 1: Basic | Tone Filter
        # Row 2: Grain | Position / Spray
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        grid_layout.addWidget(self._basic_group, 0, 0)
        grid_layout.addWidget(self._filter_group, 0, 1)
        grid_layout.addWidget(self._grain_group, 1, 0)
        grid_layout.addWidget(self._position_group, 1, 1)

        scroll_layout.addLayout(grid_layout)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Connect signals
        self._button_group.idClicked.connect(self._on_emitter_clicked)

        for group in [self._basic_group, self._grain_group,
                      self._position_group, self._filter_group]:
            group.sliderChanged.connect(self._on_slider_changed)
            group.sliderSet.connect(self._on_slider_set)

        # Connect click signals for mouse focus (order matches slider_groups property)
        # Basic=0, Filter=1, Grain=2, Position=3
        self._basic_group.controlClicked.connect(
            lambda ctrl_idx, name: self.controlFocusRequested.emit(0, ctrl_idx)
        )
        self._filter_group.controlClicked.connect(
            lambda ctrl_idx, name: self.controlFocusRequested.emit(1, ctrl_idx)
        )
        self._grain_group.controlClicked.connect(
            lambda ctrl_idx, name: self.controlFocusRequested.emit(2, ctrl_idx)
        )
        self._position_group.controlClicked.connect(
            lambda ctrl_idx, name: self.controlFocusRequested.emit(3, ctrl_idx)
        )

    def _on_emitter_clicked(self, emitter_num: int):
        """Handle emitter button click."""
        if emitter_num == self._current_emitter:
            return

        # Save current emitter values
        self._save_current_values()

        # Update button styles
        self._emitter_buttons[self._current_emitter].setStyleSheet(
            get_emitter_button_style(self._current_emitter, selected=False)
        )
        self._emitter_buttons[emitter_num].setStyleSheet(
            get_emitter_button_style(emitter_num, selected=True)
        )

        # Load new emitter values
        self._current_emitter = emitter_num
        self._load_emitter_values(emitter_num)

        self.emitterSelected.emit(emitter_num)

    def _save_current_values(self):
        """Save current slider values for the current emitter."""
        for group in [self._basic_group, self._grain_group,
                      self._position_group, self._filter_group]:
            for name in group.parameter_names:
                self._emitter_values[self._current_emitter][name] = group.get_value(name)

    def _load_emitter_values(self, emitter_num: int):
        """Load slider values for an emitter."""
        values = self._emitter_values[emitter_num]
        self._basic_group.set_all_values(values)
        self._grain_group.set_all_values(values)
        self._position_group.set_all_values(values)
        self._filter_group.set_all_values(values)

    def _on_slider_changed(self, param: str, value: int):
        """Handle slider value change during drag."""
        self._emitter_values[self._current_emitter][param] = value
        self.parameterChanged.emit(self._current_emitter, param, value)

    def _on_slider_set(self, param: str, value: int):
        """Handle slider release (final value)."""
        self._emitter_values[self._current_emitter][param] = value
        self.parameterSet.emit(self._current_emitter, param, value)

    @property
    def current_emitter(self) -> int:
        """Get currently selected emitter number."""
        return self._current_emitter

    def select_emitter(self, emitter_num: int):
        """Programmatically select an emitter."""
        if 1 <= emitter_num <= 4:
            self._emitter_buttons[emitter_num].click()

    def set_parameter(self, emitter_num: int, param: str, value: int):
        """Set a parameter value without emitting signals.

        Updates stored values and UI if emitter is currently selected.
        """
        self._emitter_values[emitter_num][param] = value

        # Update UI if this is the current emitter
        if emitter_num == self._current_emitter:
            for group in [self._basic_group, self._grain_group,
                          self._position_group, self._filter_group]:
                if param in group.parameter_names:
                    group.set_value(param, value)
                    break

    def get_parameter(self, emitter_num: int, param: str) -> int:
        """Get a parameter value."""
        return self._emitter_values[emitter_num].get(param, 64)

    def set_all_parameters(self, emitter_num: int, values: dict[str, int]):
        """Set all parameters for an emitter."""
        self._emitter_values[emitter_num].update(values)
        if emitter_num == self._current_emitter:
            self._load_emitter_values(emitter_num)

    def get_all_parameters(self, emitter_num: int) -> dict[str, int]:
        """Get all parameters for an emitter."""
        return dict(self._emitter_values[emitter_num])

    # --- Keyboard navigation ---

    @property
    def slider_groups(self) -> list[SliderGroup]:
        """Get list of slider groups in navigation order."""
        return [self._basic_group, self._filter_group, self._grain_group, self._position_group]

    @property
    def subsection_names(self) -> list[str]:
        """Get names of subsections."""
        return ['Basic', 'Tone Filter', 'Grain', 'Position / Spray']

    def set_subsection_focus(self, index: int):
        """Focus a specific subsection (slider group).

        Args:
            index: Subsection index (0-3)
        """
        self._focused_subsection = index
        groups = self.slider_groups
        for i, group in enumerate(groups):
            group.set_group_focused(i == index)
            # Don't call setFocus() on child - keep focus on panel to avoid race condition

    def get_current_subsection(self) -> int:
        """Get currently focused subsection index."""
        groups = self.slider_groups
        for i, group in enumerate(groups):
            if group.hasFocus():
                return i
        return 0

    def get_navigation_path(self) -> str:
        """Get current navigation path string."""
        subsection = self.get_current_subsection()
        group = self.slider_groups[subsection]
        path = f"Emitter {self._current_emitter} > {self.subsection_names[subsection]}"
        if group.focused_name:
            label = group.get_control_label(group.focused_index)
            value = group.get_value(group.focused_name)
            path += f" > {label}: {value}"
        return path

    def set_panel_focused(self, focused: bool):
        """Set whether this panel is the active section.

        Note: This only controls the panel border highlight, not subsection
        highlights. Subsection focus is controlled via set_subsection_focus().
        """
        self._panel_focused = focused
        self.setStyleSheet(get_section_focus_style(focused))
        # Clear all subsection focus and control focus when panel loses focus
        if not focused:
            for group in self.slider_groups:
                group.set_group_focused(False)
                group.clear_control_focus()
            self._in_control_mode = False

    def focusInEvent(self, event: QFocusEvent):
        """Handle focus gained - show panel highlight only."""
        super().focusInEvent(event)
        self.set_panel_focused(True)
        # Don't auto-highlight subsections - NavigationManager controls that

    def focusOutEvent(self, event: QFocusEvent):
        """Handle focus lost - only clear if focus left the panel hierarchy."""
        super().focusOutEvent(event)
        # Only clear if focus went OUTSIDE this panel hierarchy
        new_focus = QApplication.focusWidget()
        if new_focus is None or not self.isAncestorOf(new_focus):
            self.set_panel_focused(False)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for navigation within the panel."""
        key = event.key()
        groups = self.slider_groups
        num_subsections = len(groups)

        # Handle navigation keys
        if key in (Qt.Key.Key_Up, Qt.Key.Key_W):
            if self._in_control_mode:
                # Move to previous control within subsection
                groups[self._focused_subsection].focus_prev_control()
                self.controlNavigated.emit(groups[self._focused_subsection].focused_index)
            else:
                # Move to previous subsection
                new_subsection = max(0, self._focused_subsection - 1)
                if new_subsection != self._focused_subsection:
                    self._focused_subsection = new_subsection
                    self.set_subsection_focus(self._focused_subsection)
                    self.subsectionNavigated.emit(self._focused_subsection)
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            if self._in_control_mode:
                # Move to next control within subsection
                groups[self._focused_subsection].focus_next_control()
                self.controlNavigated.emit(groups[self._focused_subsection].focused_index)
            else:
                # Move to next subsection
                new_subsection = min(num_subsections - 1, self._focused_subsection + 1)
                if new_subsection != self._focused_subsection:
                    self._focused_subsection = new_subsection
                    self.set_subsection_focus(self._focused_subsection)
                    self.subsectionNavigated.emit(self._focused_subsection)
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            if self._in_control_mode:
                # Adjust value down
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    groups[self._focused_subsection].adjust_focused_value(-10)
                else:
                    groups[self._focused_subsection].adjust_focused_value(-1)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            if self._in_control_mode:
                # Adjust value up
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    groups[self._focused_subsection].adjust_focused_value(10)
                else:
                    groups[self._focused_subsection].adjust_focused_value(1)
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Delete):
            if self._in_control_mode:
                # Reset control to default
                groups[self._focused_subsection].reset_focused_to_default()
        else:
            super().keyPressEvent(event)

    def enter_control_mode(self, control_index: int = 0):
        """Enter control mode - start navigating individual controls.

        Args:
            control_index: The control index to focus (default 0)
        """
        self._in_control_mode = True
        groups = self.slider_groups
        if 0 <= self._focused_subsection < len(groups):
            groups[self._focused_subsection].set_control_focus(control_index)

    def exit_control_mode(self):
        """Exit control mode - return to subsection navigation."""
        self._in_control_mode = False
        groups = self.slider_groups
        if 0 <= self._focused_subsection < len(groups):
            groups[self._focused_subsection].clear_control_focus()
