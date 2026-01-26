"""Labeled slider widget with value display."""

from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider

from gui.styles import get_slider_focus_style


class LabeledSlider(QWidget):
    """
    A horizontal slider with a label on the left and value display on the right.

    Supports keyboard focus indication for one-handed navigation.

    Signals:
        valueChanged(int): Emitted when value changes during drag
        valueSet(int): Emitted when slider is released (final value)
        clicked(): Emitted when the slider is clicked (for mouse focus)
    """

    valueChanged = Signal(int)
    valueSet = Signal(int)
    clicked = Signal()

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

        # Install event filter to detect clicks on the internal slider
        self._slider.installEventFilter(self)

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

    def set_focused(self, focused: bool):
        """Set visual focus state for keyboard navigation.

        Args:
            focused: Whether this slider should appear focused
        """
        self._slider.setStyleSheet(get_slider_focus_style(focused))

    def adjust_value(self, delta: int):
        """Adjust value by delta, clamping to range.

        Args:
            delta: Amount to add to current value (positive or negative)
        """
        new_value = self._slider.value() + delta
        new_value = max(self._slider.minimum(), min(self._slider.maximum(), new_value))
        if new_value != self._slider.value():
            self._slider.setValue(new_value)
            self._value_label.setText(str(new_value))
            self.valueChanged.emit(new_value)
            self.valueSet.emit(new_value)

    def get_default_value(self) -> int:
        """Get the default/initial value."""
        # Default is typically the midpoint or a stored value
        return getattr(self, '_default_value', 64)

    def set_default_value(self, value: int):
        """Store the default value for reset functionality."""
        self._default_value = value

    def reset_to_default(self):
        """Reset slider to its default value."""
        default = self.get_default_value()
        if self._slider.value() != default:
            self._slider.setValue(default)
            self._value_label.setText(str(default))
            self.valueChanged.emit(default)
            self.valueSet.emit(default)

    @property
    def slider(self) -> QSlider:
        """Get the underlying QSlider widget."""
        return self._slider

    def mousePressEvent(self, event):
        """Handle mouse press to emit clicked signal for focus management."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def eventFilter(self, obj, event):
        """Filter events to detect clicks on the internal slider.

        QSlider consumes mouse events, so we use an event filter to detect
        clicks and emit the clicked signal for focus management.
        """
        if obj == self._slider and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit()
        return super().eventFilter(obj, event)
