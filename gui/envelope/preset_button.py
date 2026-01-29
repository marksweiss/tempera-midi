"""Preset button widget with shape preview."""
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QPainterPath, QColor
from PySide6.QtWidgets import QPushButton, QWidget

from gui.envelope.envelope_presets import EnvelopePreset, generate_preset_points


class PresetButton(QPushButton):
    """Button showing envelope shape preview."""

    BUTTON_SIZE = (40, 30)  # Width, Height

    def __init__(self, preset: EnvelopePreset, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._preset = preset
        self._points = generate_preset_points(preset, per_cell=False)

        self.setCheckable(True)
        self.setFixedSize(*self.BUTTON_SIZE)
        self.setToolTip(preset.value.replace('_', ' ').title())

        # Connect toggled signal to update style
        self.toggled.connect(self._on_toggled)
        self._update_style()

    @property
    def preset(self) -> EnvelopePreset:
        """Get the preset type for this button."""
        return self._preset

    def _on_toggled(self, checked: bool):
        """Handle toggle state change."""
        self._update_style()

    def _update_style(self):
        """Update button background style based on checked state."""
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4A90D9;
                    border: 1px solid #5AA0E9;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #5AA0E9;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    border: 1px solid #505050;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #4A4A4A;
                }
            """)

    def paintEvent(self, event):
        """Draw button background and envelope shape."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw envelope shape
        rect = self.rect().adjusted(6, 6, -6, -6)
        color = QColor('#FFFFFF') if self.isChecked() else QColor('#A0A0A0')
        pen = QPen(color)
        pen.setWidth(2)
        painter.setPen(pen)

        if self._points:
            path = QPainterPath()
            first = self._points[0]
            x = rect.x() + first[0] * rect.width()
            y = rect.y() + (1.0 - first[1]) * rect.height()
            path.moveTo(x, y)

            for time, value in self._points[1:]:
                x = rect.x() + time * rect.width()
                y = rect.y() + (1.0 - value) * rect.height()
                path.lineTo(x, y)

            painter.drawPath(path)

        painter.end()
