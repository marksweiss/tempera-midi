"""Global effects and modwheel controls panel."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QFocusEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTabWidget, QSlider, QLabel, QApplication
)

from gui.widgets.slider_group import SliderGroup
from gui.styles import get_section_focus_style, get_slider_focus_style


# Parameter definitions
ADSR_PARAMS = [
    {'name': 'attack', 'label': 'Attack', 'default': 0},
    {'name': 'decay', 'label': 'Decay', 'default': 0},
    {'name': 'sustain', 'label': 'Sustain', 'default': 127},
    {'name': 'release', 'label': 'Release', 'default': 64},
]

REVERB_PARAMS = [
    {'name': 'size', 'label': 'Size', 'default': 64},
    {'name': 'color', 'label': 'Color', 'default': 64},
    {'name': 'mix', 'label': 'Mix', 'default': 0},
]

DELAY_PARAMS = [
    {'name': 'feedback', 'label': 'Feedback', 'default': 64},
    {'name': 'time', 'label': 'Time', 'default': 64},
    {'name': 'color', 'label': 'Color', 'default': 64},
    {'name': 'mix', 'label': 'Mix', 'default': 0},
]

CHORUS_PARAMS = [
    {'name': 'depth', 'label': 'Depth', 'default': 64},
    {'name': 'speed', 'label': 'Speed', 'default': 64},
    {'name': 'flange', 'label': 'Flange', 'default': 64},
    {'name': 'mix', 'label': 'Mix', 'default': 0},
]


class GlobalPanel(QGroupBox):
    """
    Panel for global Tempera controls: ADSR envelope, effects, and modwheel.

    Features:
    - ADSR envelope controls
    - Tabbed effects (Reverb, Delay, Chorus)
    - Prominent modwheel slider

    Signals:
        modwheelChanged(int): Emitted when modwheel changes
        modwheelSet(int): Emitted when modwheel slider released
        parameterChanged(str, str, int): Emitted on slider change (category, param, value)
        parameterSet(str, str, int): Emitted on slider release (category, param, value)
    """

    modwheelChanged = Signal(int)
    modwheelSet = Signal(int)
    parameterChanged = Signal(str, str, int)
    parameterSet = Signal(str, str, int)

    def __init__(self, parent: QWidget = None):
        super().__init__('Global', parent)

        self._panel_focused = False
        self._focused_subsection = 0  # 0=ADSR, 1=Reverb, 2=Delay, 3=Chorus, 4=Modwheel
        self._in_control_mode = False  # Whether we're navigating controls within a subsection
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setSpacing(16)

        # ADSR controls (left)
        self._adsr_group = SliderGroup('ADSR Envelope', ADSR_PARAMS, label_width=70)
        self._adsr_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('adsr', p, v)
        )
        self._adsr_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('adsr', p, v)
        )
        layout.addWidget(self._adsr_group)

        # Effects group with tabs (center)
        effects_group = QGroupBox('Effects')
        effects_layout = QVBoxLayout(effects_group)
        effects_layout.setContentsMargins(8, 8, 8, 8)

        self._effects_tabs = QTabWidget()

        # Reverb tab
        self._reverb_group = SliderGroup('', REVERB_PARAMS, label_width=70)
        self._reverb_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('reverb', p, v)
        )
        self._reverb_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('reverb', p, v)
        )
        self._effects_tabs.addTab(self._reverb_group, 'Reverb')

        # Delay tab
        self._delay_group = SliderGroup('', DELAY_PARAMS, label_width=70)
        self._delay_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('delay', p, v)
        )
        self._delay_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('delay', p, v)
        )
        self._effects_tabs.addTab(self._delay_group, 'Delay')

        # Chorus tab
        self._chorus_group = SliderGroup('', CHORUS_PARAMS, label_width=70)
        self._chorus_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('chorus', p, v)
        )
        self._chorus_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('chorus', p, v)
        )
        self._effects_tabs.addTab(self._chorus_group, 'Chorus')

        effects_layout.addWidget(self._effects_tabs)
        layout.addWidget(effects_group)

        # Right side: Modwheel
        modwheel_layout = QVBoxLayout()
        modwheel_layout.setSpacing(4)

        modwheel_label = QLabel('Mod')
        modwheel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        modwheel_layout.addWidget(modwheel_label)

        self._modwheel_value = QLabel('0')
        self._modwheel_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        modwheel_layout.addWidget(self._modwheel_value)

        self._modwheel = QSlider(Qt.Orientation.Vertical)
        self._modwheel.setMinimum(0)
        self._modwheel.setMaximum(127)
        self._modwheel.setValue(0)
        self._modwheel.setTracking(True)
        self._modwheel.setFixedWidth(32)
        self._modwheel.setMinimumHeight(150)
        modwheel_layout.addWidget(self._modwheel, alignment=Qt.AlignmentFlag.AlignCenter)

        self._modwheel.valueChanged.connect(self._on_modwheel_changed)
        self._modwheel.sliderReleased.connect(self._on_modwheel_released)

        modwheel_layout.addStretch()
        layout.addLayout(modwheel_layout)

    def _on_modwheel_changed(self, value: int):
        """Handle modwheel value change."""
        self._modwheel_value.setText(str(value))
        self.modwheelChanged.emit(value)

    def _on_modwheel_released(self):
        """Handle modwheel slider release."""
        self.modwheelSet.emit(self._modwheel.value())

    def get_modwheel(self) -> int:
        """Get modwheel value."""
        return self._modwheel.value()

    def set_modwheel(self, value: int):
        """Set modwheel value without emitting signals."""
        self._modwheel.blockSignals(True)
        self._modwheel.setValue(value)
        self._modwheel_value.setText(str(value))
        self._modwheel.blockSignals(False)

    def get_parameter(self, category: str, param: str) -> int:
        """Get a parameter value."""
        group = self._get_group(category)
        return group.get_value(param) if group else 0

    def set_parameter(self, category: str, param: str, value: int):
        """Set a parameter value without emitting signals."""
        group = self._get_group(category)
        if group:
            group.set_value(param, value)

    def _get_group(self, category: str) -> SliderGroup:
        """Get the slider group for a category."""
        return {
            'adsr': self._adsr_group,
            'reverb': self._reverb_group,
            'delay': self._delay_group,
            'chorus': self._chorus_group,
        }.get(category)

    def set_all_parameters(self, values: dict):
        """Set all parameter values.

        Args:
            values: Dict with structure:
                {
                    'modwheel': int,
                    'adsr': {'attack': int, ...},
                    'reverb': {'size': int, ...},
                    ...
                }
        """
        if 'modwheel' in values:
            self.set_modwheel(values['modwheel'])

        for category in ['adsr', 'reverb', 'delay', 'chorus']:
            if category in values:
                group = self._get_group(category)
                if group:
                    group.set_all_values(values[category])

    def get_all_parameters(self) -> dict:
        """Get all parameter values."""
        return {
            'modwheel': self._modwheel.value(),
            'adsr': self._adsr_group.get_all_values(),
            'reverb': self._reverb_group.get_all_values(),
            'delay': self._delay_group.get_all_values(),
            'chorus': self._chorus_group.get_all_values(),
        }

    # --- Keyboard navigation ---

    # Subsections: 0=ADSR, 1=Reverb, 2=Delay, 3=Chorus, 4=Modwheel
    SUBSECTION_NAMES = ['ADSR', 'Reverb', 'Delay', 'Chorus', 'Modwheel']

    @property
    def slider_groups(self) -> list[SliderGroup]:
        """Get list of slider groups (excludes modwheel)."""
        return [self._adsr_group, self._reverb_group, self._delay_group, self._chorus_group]

    def set_subsection_focus(self, index: int):
        """Focus a specific subsection.

        Args:
            index: 0=ADSR, 1=Reverb, 2=Delay, 3=Chorus, 4=Modwheel
        """
        self._focused_subsection = index
        groups = self.slider_groups
        # Clear all group focus
        for group in groups:
            group.set_group_focused(False)

        # Clear modwheel focus
        self._modwheel.setStyleSheet(get_slider_focus_style(False))

        if index == 4:
            # Highlight modwheel (don't call setFocus to avoid race condition)
            self._modwheel.setStyleSheet(get_slider_focus_style(True))
        elif 0 <= index < len(groups):
            # Focus a slider group (visual only, don't call setFocus)
            groups[index].set_group_focused(True)
            # For effects tabs, switch to the appropriate tab
            if index >= 1:
                self._effects_tabs.setCurrentIndex(index - 1)

    def get_current_subsection(self) -> int:
        """Get currently focused subsection index."""
        if self._modwheel.hasFocus():
            return 4
        groups = self.slider_groups
        for i, group in enumerate(groups):
            if group.hasFocus():
                return i
        return 0

    def adjust_modwheel(self, delta: int):
        """Adjust modwheel value."""
        new_value = self._modwheel.value() + delta
        new_value = max(0, min(127, new_value))
        if new_value != self._modwheel.value():
            self._modwheel.setValue(new_value)
            self._modwheel_value.setText(str(new_value))
            self.modwheelChanged.emit(new_value)
            self.modwheelSet.emit(new_value)

    def get_navigation_path(self) -> str:
        """Get current navigation path string."""
        subsection = self.get_current_subsection()
        path = f"Global > {self.SUBSECTION_NAMES[subsection]}"

        if subsection == 4:
            # Modwheel
            path += f": {self._modwheel.value()}"
        elif subsection < 4:
            group = self.slider_groups[subsection]
            if group.focused_name:
                label = group.get_control_label(group.focused_index)
                value = group.get_value(group.focused_name)
                path += f" > {label}: {value}"

        return path

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for navigation within the panel."""
        key = event.key()
        groups = self.slider_groups
        num_subsections = 5  # 0=ADSR, 1=Reverb, 2=Delay, 3=Chorus, 4=Modwheel

        # Handle navigation keys
        if key in (Qt.Key.Key_Up, Qt.Key.Key_W):
            if self._in_control_mode:
                if self._focused_subsection == 4:
                    # Modwheel: increase value
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        self.adjust_modwheel(10)
                    else:
                        self.adjust_modwheel(1)
                else:
                    # Move to previous control within subsection
                    groups[self._focused_subsection].focus_prev_control()
            else:
                # Move to previous subsection
                self._focused_subsection = max(0, self._focused_subsection - 1)
                self.set_subsection_focus(self._focused_subsection)
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            if self._in_control_mode:
                if self._focused_subsection == 4:
                    # Modwheel: decrease value
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        self.adjust_modwheel(-10)
                    else:
                        self.adjust_modwheel(-1)
                else:
                    # Move to next control within subsection
                    groups[self._focused_subsection].focus_next_control()
            else:
                # Move to next subsection
                self._focused_subsection = min(num_subsections - 1, self._focused_subsection + 1)
                self.set_subsection_focus(self._focused_subsection)
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            if self._in_control_mode:
                if self._focused_subsection == 4:
                    # Modwheel: decrease value
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        self.adjust_modwheel(-10)
                    else:
                        self.adjust_modwheel(-1)
                else:
                    # Adjust value down
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        groups[self._focused_subsection].adjust_focused_value(-10)
                    else:
                        groups[self._focused_subsection].adjust_focused_value(-1)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            if self._in_control_mode:
                if self._focused_subsection == 4:
                    # Modwheel: increase value
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        self.adjust_modwheel(10)
                    else:
                        self.adjust_modwheel(1)
                else:
                    # Adjust value up
                    if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                        groups[self._focused_subsection].adjust_focused_value(10)
                    else:
                        groups[self._focused_subsection].adjust_focused_value(1)
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Delete):
            if self._in_control_mode:
                if self._focused_subsection == 4:
                    # Reset modwheel to 0
                    self._modwheel.setValue(0)
                    self._modwheel_value.setText('0')
                    self.modwheelChanged.emit(0)
                    self.modwheelSet.emit(0)
                else:
                    # Reset control to default
                    groups[self._focused_subsection].reset_focused_to_default()
        else:
            super().keyPressEvent(event)

    def enter_control_mode(self):
        """Enter control mode - start navigating individual controls."""
        self._in_control_mode = True
        if self._focused_subsection == 4:
            # Modwheel is already focused, no need to set control focus
            pass
        else:
            groups = self.slider_groups
            if 0 <= self._focused_subsection < len(groups):
                groups[self._focused_subsection].set_control_focus(0)

    def exit_control_mode(self):
        """Exit control mode - return to subsection navigation."""
        self._in_control_mode = False
        groups = self.slider_groups
        if 0 <= self._focused_subsection < len(groups):
            groups[self._focused_subsection].clear_control_focus()

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
            self._modwheel.setStyleSheet(get_slider_focus_style(False))
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
