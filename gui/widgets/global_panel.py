"""Global effects and modulator controls panel."""

from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QKeyEvent, QFocusEvent, QMouseEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTabWidget, QSlider, QLabel, QApplication, QComboBox
)

from gui.widgets.slider_group import SliderGroup
from gui.styles import get_section_focus_style, get_slider_focus_style, get_combobox_focus_style


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

FILTER_PARAMS = [
    {'name': 'cutoff', 'label': 'Cutoff', 'default': 64},
    {'name': 'resonance', 'label': 'Resonance', 'default': 64},
]

CHORUS_PARAMS = [
    {'name': 'depth', 'label': 'Depth', 'default': 64},
    {'name': 'speed', 'label': 'Speed', 'default': 64},
    {'name': 'flange', 'label': 'Flange', 'default': 64},
    {'name': 'mix', 'label': 'Mix', 'default': 0},
]


class GlobalPanel(QGroupBox):
    """
    Panel for global Tempera controls: ADSR envelope, effects, and modulator size.

    Features:
    - ADSR envelope controls
    - Tabbed effects (Reverb, Delay, Chorus)
    - Modulator size slider with modulator selector (1-10)

    This panel is purely REACTIVE to NavigationManager signals. It does not
    track navigation state itself - it queries NavigationManager when needed.

    Signals:
        modulatorSizeChanged(int): Emitted when modulator size changes
        modulatorSizeSet(int): Emitted when modulator size slider released
        modulatorSelected(int): Emitted when modulator selection changes
        parameterChanged(str, str, int): Emitted on slider change (category, param, value)
        parameterSet(str, str, int): Emitted on slider release (category, param, value)
        controlFocusRequested(int, int): Emitted when a control is clicked (subsection_index, control_index)
        sectionClicked(): Emitted when panel background is clicked
        subsectionFocusRequested(int): Emitted when a subsection header is clicked
    """

    modulatorSizeChanged = Signal(int)
    modulatorSizeSet = Signal(int)
    modulatorSelected = Signal(int)
    parameterChanged = Signal(str, str, int)
    parameterSet = Signal(str, str, int)
    controlFocusRequested = Signal(int, int)
    # Signals for mouse click focus
    sectionClicked = Signal()  # Emitted when panel background is clicked
    subsectionFocusRequested = Signal(int)  # Emitted when a subsection header is clicked

    def __init__(self, parent: QWidget = None):
        super().__init__('Global', parent)

        self._panel_focused = False
        # Visual state - tracks which subsection/control is visually highlighted
        # This is set by MainWindow in response to NavigationManager signals
        self._visual_subsection = -1  # 0=ADSR, 1=Reverb, 2=Delay, 3=Filter, 4=Chorus, 5=Modulator
        self._visual_control = -1  # Currently highlighted control (-1 = none)
        self._modulator_control_index = 0  # 0=dropdown, 1=slider (for modulator subsection)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 4, 8, 4)

        # ADSR controls (left) - wrapped in container with top spacing to align with Effects sliders
        self._adsr_group = SliderGroup('ADSR Envelope', ADSR_PARAMS, label_width=70)
        self._adsr_group.set_group_focused(False)  # Set initial style to avoid layout shift
        self._adsr_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('adsr', p, v)
        )
        self._adsr_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('adsr', p, v)
        )
        # Wrap ADSR in container with top spacing to push sliders down to align with Effects
        adsr_container = QWidget()
        adsr_layout = QVBoxLayout(adsr_container)
        adsr_layout.setContentsMargins(0, 0, 0, 0)
        adsr_layout.setSpacing(0)
        adsr_layout.addSpacing(32)  # Space to align with Effects sliders below tabs
        adsr_layout.addWidget(self._adsr_group)
        adsr_layout.addStretch()
        layout.addWidget(adsr_container)

        # Effects group with tabs (center)
        self._effects_group = QGroupBox('Effects')
        self._effects_group.setStyleSheet(get_section_focus_style(False))  # Set initial style
        effects_layout = QVBoxLayout(self._effects_group)
        effects_layout.setContentsMargins(4, 0, 4, 4)
        effects_layout.setSpacing(0)

        self._effects_tabs = QTabWidget()

        # Helper to wrap slider group in container (minimal padding)
        def _wrap_in_container(slider_group: SliderGroup) -> QWidget:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)
            container_layout.addWidget(slider_group)
            container_layout.addStretch()  # Push SliderGroup to top
            return container

        # Reverb tab
        self._reverb_group = SliderGroup('', REVERB_PARAMS, label_width=70)
        self._reverb_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('reverb', p, v)
        )
        self._reverb_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('reverb', p, v)
        )
        self._effects_tabs.addTab(_wrap_in_container(self._reverb_group), 'Reverb')

        # Delay tab
        self._delay_group = SliderGroup('', DELAY_PARAMS, label_width=70)
        self._delay_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('delay', p, v)
        )
        self._delay_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('delay', p, v)
        )
        self._effects_tabs.addTab(_wrap_in_container(self._delay_group), 'Delay')

        # Filter tab
        self._filter_group = SliderGroup('', FILTER_PARAMS, label_width=70)
        self._filter_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('filter', p, v)
        )
        self._filter_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('filter', p, v)
        )
        self._effects_tabs.addTab(_wrap_in_container(self._filter_group), 'Filter')

        # Chorus tab
        self._chorus_group = SliderGroup('', CHORUS_PARAMS, label_width=70)
        self._chorus_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('chorus', p, v)
        )
        self._chorus_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('chorus', p, v)
        )
        self._effects_tabs.addTab(_wrap_in_container(self._chorus_group), 'Chorus')

        effects_layout.addWidget(self._effects_tabs)
        layout.addWidget(self._effects_group)

        # Right side: Modulator group (like other subsections)
        self._modulator_group = QGroupBox('Modulator')
        self._modulator_group.setStyleSheet(get_section_focus_style(False))  # Set initial style
        modulator_layout = QVBoxLayout(self._modulator_group)
        modulator_layout.setSpacing(0)
        modulator_layout.setContentsMargins(4, 4, 4, 4)

        self._modulator_size_value = QLabel('0')
        self._modulator_size_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        modulator_layout.addWidget(self._modulator_size_value)

        self._modulator_slider = QSlider(Qt.Orientation.Vertical)
        self._modulator_slider.setMinimum(0)
        self._modulator_slider.setMaximum(127)
        self._modulator_slider.setValue(0)
        self._modulator_slider.setTracking(True)
        self._modulator_slider.setFixedWidth(32)
        self._modulator_slider.setStyleSheet(get_slider_focus_style(False))  # Set initial style
        # Slider expands to fill available space
        modulator_layout.addWidget(self._modulator_slider, stretch=1, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._modulator_slider.valueChanged.connect(self._on_modulator_size_changed)
        self._modulator_slider.sliderReleased.connect(self._on_modulator_size_released)

        # 5px spacer between slider and dropdown
        modulator_layout.addSpacing(5)

        # Modulator selector dropdown (1-10) at bottom
        self._modulator_selector = QComboBox()
        for i in range(1, 11):
            self._modulator_selector.addItem(f'Mod {i}', i)
        self._modulator_selector.setFixedWidth(80)
        self._modulator_selector.setStyleSheet(get_combobox_focus_style(False))  # Set initial style
        self._modulator_selector.currentIndexChanged.connect(self._on_modulator_selected)
        modulator_layout.addWidget(self._modulator_selector, alignment=Qt.AlignmentFlag.AlignCenter)

        # Install event filter on modulator controls and group for click detection
        self._modulator_slider.installEventFilter(self)
        self._modulator_selector.installEventFilter(self)
        self._modulator_group.installEventFilter(self)

        layout.addWidget(self._modulator_group)

        # Connect click signals for mouse focus
        # Subsections: 0=ADSR, 1=Reverb, 2=Delay, 3=Filter, 4=Chorus, 5=Modulator
        self._adsr_group.controlClicked.connect(
            lambda ctrl_idx, name: self.controlFocusRequested.emit(0, ctrl_idx)
        )
        self._reverb_group.controlClicked.connect(
            lambda ctrl_idx, name: self.controlFocusRequested.emit(1, ctrl_idx)
        )
        self._delay_group.controlClicked.connect(
            lambda ctrl_idx, name: self.controlFocusRequested.emit(2, ctrl_idx)
        )
        self._filter_group.controlClicked.connect(
            lambda ctrl_idx, name: self.controlFocusRequested.emit(3, ctrl_idx)
        )
        self._chorus_group.controlClicked.connect(
            lambda ctrl_idx, name: self.controlFocusRequested.emit(4, ctrl_idx)
        )

        # Connect subsection click signals (clicking on group header/empty space)
        self._adsr_group.subsectionClicked.connect(
            lambda: self.subsectionFocusRequested.emit(0)
        )
        self._reverb_group.subsectionClicked.connect(
            lambda: self.subsectionFocusRequested.emit(1)
        )
        self._delay_group.subsectionClicked.connect(
            lambda: self.subsectionFocusRequested.emit(2)
        )
        self._filter_group.subsectionClicked.connect(
            lambda: self.subsectionFocusRequested.emit(3)
        )
        self._chorus_group.subsectionClicked.connect(
            lambda: self.subsectionFocusRequested.emit(4)
        )

        # Set initial unfocused style on panel to avoid layout shift on first focus change
        self.setStyleSheet(get_section_focus_style(False))

    def _on_modulator_size_changed(self, value: int):
        """Handle modulator size value change."""
        self._modulator_size_value.setText(str(value))
        self.modulatorSizeChanged.emit(value)

    def _on_modulator_size_released(self):
        """Handle modulator size slider release."""
        self.modulatorSizeSet.emit(self._modulator_slider.value())

    def _on_modulator_selected(self, index: int):
        """Handle modulator selection change."""
        modulator_num = self._modulator_selector.itemData(index)
        self.modulatorSelected.emit(modulator_num)

    def get_modulator_size(self) -> int:
        """Get modulator size value."""
        return self._modulator_slider.value()

    def set_modulator_size(self, value: int):
        """Set modulator size value without emitting signals."""
        self._modulator_slider.blockSignals(True)
        self._modulator_slider.setValue(value)
        self._modulator_size_value.setText(str(value))
        self._modulator_slider.blockSignals(False)

    def get_modulator_selected(self) -> int:
        """Get currently selected modulator (1-10)."""
        return self._modulator_selector.currentData()

    def set_modulator_selected(self, modulator_num: int):
        """Set selected modulator (1-10) without emitting signals."""
        self._modulator_selector.blockSignals(True)
        self._modulator_selector.setCurrentIndex(modulator_num - 1)
        self._modulator_selector.blockSignals(False)

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
            'filter': self._filter_group,
            'chorus': self._chorus_group,
        }.get(category)

    def set_all_parameters(self, values: dict):
        """Set all parameter values.

        Args:
            values: Dict with structure:
                {
                    'modulator': {'selected': int, 'size': int},
                    'adsr': {'attack': int, ...},
                    'reverb': {'size': int, ...},
                    ...
                }
        """
        if 'modulator' in values:
            mod = values['modulator']
            if 'selected' in mod:
                self.set_modulator_selected(mod['selected'])
            if 'size' in mod:
                self.set_modulator_size(mod['size'])

        for category in ['adsr', 'reverb', 'delay', 'filter', 'chorus']:
            if category in values:
                group = self._get_group(category)
                if group:
                    group.set_all_values(values[category])

    def get_all_parameters(self) -> dict:
        """Get all parameter values."""
        return {
            'modulator': {
                'selected': self.get_modulator_selected(),
                'size': self._modulator_slider.value(),
            },
            'adsr': self._adsr_group.get_all_values(),
            'reverb': self._reverb_group.get_all_values(),
            'delay': self._delay_group.get_all_values(),
            'filter': self._filter_group.get_all_values(),
            'chorus': self._chorus_group.get_all_values(),
        }

    # --- Keyboard navigation ---

    # Subsections: 0=ADSR, 1=Reverb, 2=Delay, 3=Filter, 4=Chorus, 5=Modulator
    SUBSECTION_NAMES = ['ADSR', 'Reverb', 'Delay', 'Filter', 'Chorus', 'Modulator']

    @property
    def slider_groups(self) -> list[SliderGroup]:
        """Get list of slider groups (excludes modulator)."""
        return [self._adsr_group, self._reverb_group, self._delay_group, self._filter_group, self._chorus_group]

    def set_subsection_focus(self, index: int):
        """Visually highlight a specific subsection.

        Called by MainWindow in response to NavigationManager.subsectionChanged signal.

        Args:
            index: 0=ADSR, 1=Reverb, 2=Delay, 3=Filter, 4=Chorus, 5=Modulator, or -1 to clear all
        """
        self._visual_subsection = index
        self._visual_control = -1  # Clear control focus when subsection changes
        groups = self.slider_groups

        # Clear all group focus
        for group in groups:
            group.set_group_focused(False)
            group.clear_control_focus()

        # Clear modulator focus (group, slider, and dropdown)
        self._modulator_group.setStyleSheet(get_section_focus_style(False))
        self._modulator_slider.setStyleSheet(get_slider_focus_style(False))
        self._modulator_selector.setStyleSheet(get_combobox_focus_style(False))

        # Clear effects group highlight (will be set below if needed)
        self._effects_group.setStyleSheet(get_section_focus_style(False))

        if index == 5:
            # Highlight modulator group (like ADSR), not individual controls
            self._modulator_group.setStyleSheet(get_section_focus_style(True))
        elif index == 0:
            # ADSR group has a title, so set_group_focused works
            groups[index].set_group_focused(True)
        elif 1 <= index <= 4:
            # Effects tabs (Reverb, Delay, Filter, Chorus) - highlight the Effects container
            # since the individual SliderGroups have no titles
            self._effects_group.setStyleSheet(get_section_focus_style(True))
            # Switch to the appropriate tab
            self._effects_tabs.setCurrentIndex(index - 1)

    def get_visual_subsection(self) -> int:
        """Get currently highlighted subsection index."""
        return self._visual_subsection

    def adjust_modulator_size(self, delta: int):
        """Adjust modulator size value."""
        new_value = self._modulator_slider.value() + delta
        new_value = max(0, min(127, new_value))
        if new_value != self._modulator_slider.value():
            self._modulator_slider.setValue(new_value)
            self._modulator_size_value.setText(str(new_value))
            self.modulatorSizeChanged.emit(new_value)
            self.modulatorSizeSet.emit(new_value)

    def adjust_modulator_selection(self, delta: int):
        """Adjust modulator selection."""
        current = self._modulator_selector.currentIndex()
        new_index = current + delta
        new_index = max(0, min(9, new_index))  # 0-9 for modulators 1-10
        if new_index != current:
            self._modulator_selector.setCurrentIndex(new_index)

    def get_navigation_path(self) -> str:
        """Get current navigation path string."""
        subsection = self._visual_subsection if self._visual_subsection >= 0 else 0
        path = f"Global > {self.SUBSECTION_NAMES[subsection]}"

        if subsection == 5:
            # Modulator
            mod_num = self.get_modulator_selected()
            path += f" (Mod {mod_num}): {self._modulator_slider.value()}"
        elif subsection < 5:
            group = self.slider_groups[subsection]
            if group.focused_name:
                label = group.get_control_label(group.focused_index)
                value = group.get_value(group.focused_name)
                path += f" > {label}: {value}"

        return path

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for value adjustment only.

        Navigation (W/S keys) is now handled by NavigationManager.
        This method only handles value adjustment (A/D keys) when a control is focused.
        """
        key = event.key()
        groups = self.slider_groups

        # Only handle value adjustment if a control is visually focused
        if self._visual_control >= 0:
            if self._visual_subsection == 5:
                # Modulator subsection: handle dropdown or slider
                if key in (Qt.Key.Key_Left, Qt.Key.Key_A):
                    if self._modulator_control_index == 0:
                        # On dropdown: decrease selection
                        self.adjust_modulator_selection(-1)
                    else:
                        # On slider: decrease value
                        delta = -10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else -1
                        self.adjust_modulator_size(delta)
                elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
                    if self._modulator_control_index == 0:
                        # On dropdown: increase selection
                        self.adjust_modulator_selection(1)
                    else:
                        # On slider: increase value
                        delta = 10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
                        self.adjust_modulator_size(delta)
                elif key in (Qt.Key.Key_X, Qt.Key.Key_Delete):
                    # Reset modulator size to 0
                    self._modulator_slider.setValue(0)
                    self._modulator_size_value.setText('0')
                    self.modulatorSizeChanged.emit(0)
                    self.modulatorSizeSet.emit(0)
                else:
                    super().keyPressEvent(event)
            elif 0 <= self._visual_subsection < len(groups):
                group = groups[self._visual_subsection]
                if key in (Qt.Key.Key_Left, Qt.Key.Key_A):
                    # Adjust value down
                    delta = -10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else -1
                    group.adjust_focused_value(delta)
                elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
                    # Adjust value up
                    delta = 10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
                    group.adjust_focused_value(delta)
                elif key in (Qt.Key.Key_X, Qt.Key.Key_Delete):
                    # Reset control to default
                    group.reset_focused_to_default()
                else:
                    super().keyPressEvent(event)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def enter_control_mode(self, control_index: int = 0):
        """Visually highlight a specific control within the current subsection.

        Called by MainWindow in response to NavigationManager entering CONTROL mode.

        Args:
            control_index: The control index to highlight (default 0).
                For modulator subsection: 0=dropdown, 1=slider.
        """
        self._visual_control = control_index
        if self._visual_subsection == 5:
            # Modulator subsection: track which control is focused (0=dropdown, 1=slider)
            self._modulator_control_index = control_index
            # Update visual highlighting for modulator controls
            if control_index == 0:
                # Dropdown is focused
                self._modulator_selector.setStyleSheet(get_combobox_focus_style(True))
                self._modulator_slider.setStyleSheet(get_slider_focus_style(False))
            else:
                # Slider is focused
                self._modulator_selector.setStyleSheet(get_combobox_focus_style(False))
                self._modulator_slider.setStyleSheet(get_slider_focus_style(True))
        else:
            groups = self.slider_groups
            if 0 <= self._visual_subsection < len(groups):
                groups[self._visual_subsection].set_control_focus(control_index)

    def exit_control_mode(self):
        """Clear control highlighting, returning to subsection-level visual state.

        Called by MainWindow in response to NavigationManager exiting CONTROL mode.
        """
        self._visual_control = -1
        if self._visual_subsection == 5:
            # Modulator subsection: clear control highlights, restore group highlight
            self._modulator_selector.setStyleSheet(get_combobox_focus_style(False))
            self._modulator_slider.setStyleSheet(get_slider_focus_style(False))
            self._modulator_group.setStyleSheet(get_section_focus_style(True))
        else:
            groups = self.slider_groups
            if 0 <= self._visual_subsection < len(groups):
                groups[self._visual_subsection].clear_control_focus()

    def set_panel_focused(self, focused: bool):
        """Set whether this panel is the active section."""
        self._panel_focused = focused
        self.setStyleSheet(get_section_focus_style(focused))
        # Always explicitly set subsection styles to prevent Qt stylesheet cascade
        # When focused=True: ensure subsections don't inherit panel's blue border
        # When focused=False: clear all highlights
        for group in self.slider_groups:
            group.set_group_focused(False)
        # Set explicit unfocused style on Effects container and Modulator group
        self._effects_group.setStyleSheet(get_section_focus_style(False))
        self._modulator_group.setStyleSheet(get_section_focus_style(False))
        if not focused:
            for group in self.slider_groups:
                group.clear_control_focus()
            self._modulator_slider.setStyleSheet(get_slider_focus_style(False))
            self._modulator_selector.setStyleSheet(get_combobox_focus_style(False))
            self._visual_subsection = -1
            self._visual_control = -1

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse click on panel background to focus the section."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Only emit if click was directly on panel, not on a child widget
            child = self.childAt(event.pos())
            if child is None:
                self.sectionClicked.emit()
        super().mousePressEvent(event)

    def focusInEvent(self, event: QFocusEvent):
        """Handle Qt focus - do NOT update visual state here.

        Visual state is controlled exclusively by NavigationManager signals
        through MainWindow. Qt focus events are ignored for highlighting.
        """
        super().focusInEvent(event)
        # NO-OP: Visual state managed by app.py handlers

    def focusOutEvent(self, event: QFocusEvent):
        """Handle Qt focus lost - do NOT update visual state here.

        Visual state is controlled exclusively by NavigationManager signals
        through MainWindow. Qt focus events are ignored for highlighting.
        """
        super().focusOutEvent(event)
        # NO-OP: Visual state managed by app.py handlers

    def eventFilter(self, obj, event):
        """Filter events to detect modulator control and group clicks."""
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                if obj == self._modulator_slider:
                    # Modulator slider is subsection 5, control 1
                    self.controlFocusRequested.emit(5, 1)
                elif obj == self._modulator_selector:
                    # Modulator dropdown is subsection 5, control 0
                    self.controlFocusRequested.emit(5, 0)
                elif obj == self._modulator_group:
                    # Clicking on modulator group header/empty space focuses subsection 5
                    self.subsectionFocusRequested.emit(5)
        return super().eventFilter(obj, event)
