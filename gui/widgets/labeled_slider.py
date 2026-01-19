"""Labeled slider widget with value display."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider


class LabeledSlider(QWidget):
    """
    A horizontal slider with a label on the left and value display on the right.

    Signals:
        valueChanged(int): Emitted when value changes during drag
        valueSet(int): Emitted when slider is released (final value)
    """

    valueChanged = Signal(int)
    valueSet = Signal(int)

    def __init__(
        self,
        label: str,
        min_value: int = 0,
        max_value: int = 127,
        initial_value: int = 64,
        label_width: int = 100,
        value_width: int = 35,
        parent: QWidget = None
    ):
        """
        Initialize the labeled slider.

        Args:
            label: Text label to display
            min_value: Minimum slider value
            max_value: Maximum slider value
            initial_value: Starting value
            label_width: Fixed width for label
            value_width: Fixed width for value display
            parent: Parent widget
        """
        super().__init__(parent)

        self._label_text = label

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)

        # Label
        self._label = QLabel(label)
        self._label.setFixedWidth(label_width)
        self._label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._label)

        # Slider
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(min_value)
        self._slider.setMaximum(max_value)
        self._slider.setValue(initial_value)
        self._slider.setTracking(True)  # Emit during drag
        layout.addWidget(self._slider, stretch=1)

        # Value display
        self._value_label = QLabel(str(initial_value))
        self._value_label.setFixedWidth(value_width)
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self._value_label)

        # Connect signals
        self._slider.valueChanged.connect(self._on_value_changed)
        self._slider.sliderReleased.connect(self._on_slider_released)

    def _on_value_changed(self, value: int):
        """Handle continuous value changes during drag."""
        self._value_label.setText(str(value))
        self.valueChanged.emit(value)

    def _on_slider_released(self):
        """Handle slider release (final value)."""
        self.valueSet.emit(self._slider.value())

    def value(self) -> int:
        """Get current slider value."""
        return self._slider.value()

    def setValue(self, value: int):
        """Set slider value without emitting signals."""
        self._slider.blockSignals(True)
        self._slider.setValue(value)
        self._value_label.setText(str(value))
        self._slider.blockSignals(False)

    def setRange(self, min_value: int, max_value: int):
        """Set slider range."""
        self._slider.setMinimum(min_value)
        self._slider.setMaximum(max_value)

    def setLabel(self, text: str):
        """Update the label text."""
        self._label_text = text
        self._label.setText(text)

    @property
    def label_text(self) -> str:
        """Get the label text."""
        return self._label_text

    def setEnabled(self, enabled: bool):
        """Enable or disable the slider."""
        super().setEnabled(enabled)
        self._slider.setEnabled(enabled)
        self._label.setEnabled(enabled)
        self._value_label.setEnabled(enabled)
