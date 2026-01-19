"""Emitter controls panel with all parameter sliders."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QButtonGroup,
    QScrollArea, QFrame
)

from gui.widgets.slider_group import SliderGroup
from gui.styles import get_emitter_button_style, EMITTER_COLORS


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


class EmitterPanel(QWidget):
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
    """

    emitterSelected = Signal(int)
    parameterChanged = Signal(int, str, int)
    parameterSet = Signal(int, str, int)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._current_emitter = 1

        # Store values for all emitters
        self._emitter_values: dict[int, dict[str, int]] = {
            i: self._get_default_values() for i in range(1, 5)
        }

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

        scroll_layout.addWidget(self._basic_group)
        scroll_layout.addWidget(self._grain_group)
        scroll_layout.addWidget(self._position_group)
        scroll_layout.addWidget(self._filter_group)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Connect signals
        self._button_group.idClicked.connect(self._on_emitter_clicked)

        for group in [self._basic_group, self._grain_group,
                      self._position_group, self._filter_group]:
            group.sliderChanged.connect(self._on_slider_changed)
            group.sliderSet.connect(self._on_slider_set)

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
