"""Global effects and modwheel controls panel."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTabWidget, QSlider, QLabel
)

from gui.widgets.slider_group import SliderGroup


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

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setSpacing(16)

        # Left side: ADSR and effects
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)

        # ADSR controls
        self._adsr_group = SliderGroup('ADSR Envelope', ADSR_PARAMS, label_width=70)
        self._adsr_group.sliderChanged.connect(
            lambda p, v: self.parameterChanged.emit('adsr', p, v)
        )
        self._adsr_group.sliderSet.connect(
            lambda p, v: self.parameterSet.emit('adsr', p, v)
        )
        left_layout.addWidget(self._adsr_group)

        # Effects group with tabs
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
        left_layout.addWidget(effects_group)
        layout.addLayout(left_layout)

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
