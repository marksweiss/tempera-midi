"""Group of labeled sliders with a title."""

from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox

from gui.widgets.labeled_slider import LabeledSlider
from gui.styles import get_section_focus_style


class SliderGroup(QGroupBox):
    """
    A group box containing multiple labeled sliders.

    Supports keyboard navigation for one-handed control.

    Signals:
        sliderChanged(str, int): Emitted when any slider value changes (param_name, value)
        sliderSet(str, int): Emitted when any slider is released (param_name, value)
        focusedControlChanged(int, str): Emitted when focused control changes (index, param_name)
        controlClicked(int, str): Emitted when a slider is clicked (index, param_name)
    """

    sliderChanged = Signal(str, int)
    sliderSet = Signal(str, int)
    focusedControlChanged = Signal(int, str)
    controlClicked = Signal(int, str)

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

        # Hide border when title is empty (used inside tabs/other containers)
        if not title:
            self.setFlat(True)
            self.setStyleSheet("QGroupBox { border: none; }")

        self._sliders: dict[str, LabeledSlider] = {}
        self._slider_order: list[str] = []  # Ordered list of parameter names
        self._focused_index = -1  # -1 means no control focused
        self._group_focused = False  # Whether this group is the active section

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
            slider.set_default_value(default)

            # Connect signals with parameter name
            slider.valueChanged.connect(lambda v, n=name: self.sliderChanged.emit(n, v))
            slider.valueSet.connect(lambda v, n=name: self.sliderSet.emit(n, v))
            slider.clicked.connect(lambda n=name: self._on_slider_clicked(n))

            layout.addWidget(slider)
            self._sliders[name] = slider
            self._slider_order.append(name)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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

    def _on_slider_clicked(self, param_name: str):
        """Handle slider click - emit controlClicked with index and name."""
        index = self._slider_order.index(param_name)
        self.controlClicked.emit(index, param_name)

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

    # --- Keyboard navigation ---

    @property
    def control_count(self) -> int:
        """Get number of controls in this group."""
        return len(self._slider_order)

    @property
    def focused_index(self) -> int:
        """Get currently focused control index (-1 if none)."""
        return self._focused_index

    @property
    def focused_name(self) -> Optional[str]:
        """Get name of currently focused control."""
        if 0 <= self._focused_index < len(self._slider_order):
            return self._slider_order[self._focused_index]
        return None

    def set_group_focused(self, focused: bool):
        """Set whether this group is the active section.

        Args:
            focused: Whether this group should show as focused
        """
        self._group_focused = focused
        # Only apply style if we have a title (not flat)
        if self.title():
            self.setStyleSheet(get_section_focus_style(focused))

    def set_control_focus(self, index: int):
        """Set focus to a specific control by index.

        Args:
            index: Control index (0-based), or -1 to unfocus all
        """
        # Clear previous focus
        if self._focused_index >= 0 and self._focused_index < len(self._slider_order):
            old_name = self._slider_order[self._focused_index]
            self._sliders[old_name].set_focused(False)

        # Set new focus
        self._focused_index = max(-1, min(index, len(self._slider_order) - 1))

        if self._focused_index >= 0:
            new_name = self._slider_order[self._focused_index]
            self._sliders[new_name].set_focused(True)
            self.focusedControlChanged.emit(self._focused_index, new_name)

    def focus_next_control(self):
        """Move focus to next control, wrapping at end."""
        if not self._slider_order:
            return
        new_index = (self._focused_index + 1) % len(self._slider_order)
        self.set_control_focus(new_index)

    def focus_prev_control(self):
        """Move focus to previous control, wrapping at start."""
        if not self._slider_order:
            return
        if self._focused_index <= 0:
            new_index = len(self._slider_order) - 1
        else:
            new_index = self._focused_index - 1
        self.set_control_focus(new_index)

    def clear_control_focus(self):
        """Clear focus from all controls."""
        self.set_control_focus(-1)

    def adjust_focused_value(self, delta: int):
        """Adjust value of focused control.

        Args:
            delta: Amount to add (positive or negative)
        """
        if self._focused_index >= 0 and self._focused_index < len(self._slider_order):
            name = self._slider_order[self._focused_index]
            self._sliders[name].adjust_value(delta)

    def reset_focused_to_default(self):
        """Reset focused control to its default value."""
        if self._focused_index >= 0 and self._focused_index < len(self._slider_order):
            name = self._slider_order[self._focused_index]
            self._sliders[name].reset_to_default()

    def get_control_label(self, index: int) -> str:
        """Get the label text for a control by index."""
        if 0 <= index < len(self._slider_order):
            name = self._slider_order[index]
            return self._sliders[name].label_text
        return ''

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input when this group has focus."""
        key = event.key()

        if key in (Qt.Key.Key_Up, Qt.Key.Key_W):
            self.focus_prev_control()
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            self.focus_next_control()
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self.adjust_focused_value(-1)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self.adjust_focused_value(1)
        elif event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            if key in (Qt.Key.Key_Left, Qt.Key.Key_A):
                self.adjust_focused_value(-10)
            elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
                self.adjust_focused_value(10)
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Delete):
            self.reset_focused_to_default()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        """Handle focus gained.

        Note: Visual focus state is controlled by NavigationManager via
        set_group_focused(), not by Qt's focus system.
        """
        super().focusInEvent(event)
        # Don't auto-set visual focus - NavigationManager controls this

    def focusOutEvent(self, event):
        """Handle focus lost.

        Note: Visual focus state is controlled by NavigationManager via
        set_group_focused(), not by Qt's focus system.
        """
        super().focusOutEvent(event)
        # Don't auto-clear visual focus - NavigationManager controls this
