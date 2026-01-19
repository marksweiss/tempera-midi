"""Group of labeled sliders with a title."""

from typing import Callable, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox

from gui.widgets.labeled_slider import LabeledSlider


class SliderGroup(QGroupBox):
    """
    A group box containing multiple labeled sliders.

    Signals:
        sliderChanged(str, int): Emitted when any slider value changes (param_name, value)
        sliderSet(str, int): Emitted when any slider is released (param_name, value)
    """

    sliderChanged = Signal(str, int)
    sliderSet = Signal(str, int)

    def __init__(
        self,
        title: str,
        parameters: list[dict],
        label_width: int = 100,
        parent: QWidget = None
    ):
        """
        Initialize the slider group.

        Args:
            title: Group box title
            parameters: List of parameter dicts, each with:
                - name: Parameter identifier (str)
                - label: Display label (str)
                - min: Minimum value (int, default 0)
                - max: Maximum value (int, default 127)
                - default: Initial value (int, default 64)
            label_width: Fixed width for all labels
            parent: Parent widget
        """
        super().__init__(title, parent)

        self._sliders: dict[str, LabeledSlider] = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        for param in parameters:
            name = param['name']
            label = param.get('label', name.replace('_', ' ').title())
            min_val = param.get('min', 0)
            max_val = param.get('max', 127)
            default = param.get('default', 64)

            slider = LabeledSlider(
                label=label,
                min_value=min_val,
                max_value=max_val,
                initial_value=default,
                label_width=label_width
            )

            # Connect signals with parameter name
            slider.valueChanged.connect(lambda v, n=name: self.sliderChanged.emit(n, v))
            slider.valueSet.connect(lambda v, n=name: self.sliderSet.emit(n, v))

            layout.addWidget(slider)
            self._sliders[name] = slider

    def get_slider(self, name: str) -> Optional[LabeledSlider]:
        """Get a slider by parameter name."""
        return self._sliders.get(name)

    def get_value(self, name: str) -> int:
        """Get a slider's current value."""
        slider = self._sliders.get(name)
        return slider.value() if slider else 0

    def set_value(self, name: str, value: int):
        """Set a slider's value without emitting signals."""
        slider = self._sliders.get(name)
        if slider:
            slider.setValue(value)

    def set_all_values(self, values: dict[str, int]):
        """Set multiple slider values without emitting signals."""
        for name, value in values.items():
            self.set_value(name, value)

    def get_all_values(self) -> dict[str, int]:
        """Get all slider values."""
        return {name: slider.value() for name, slider in self._sliders.items()}

    @property
    def parameter_names(self) -> list[str]:
        """Get list of parameter names."""
        return list(self._sliders.keys())

    def connect_all(self, callback: Callable[[str, int], None], on_change: bool = True):
        """Connect a callback to all sliders.

        Args:
            callback: Function taking (param_name, value)
            on_change: If True, connect to valueChanged; if False, to valueSet
        """
        signal = self.sliderChanged if on_change else self.sliderSet
        signal.connect(callback)
