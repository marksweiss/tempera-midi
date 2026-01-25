"""Envelope panel widget for drawing automation curves."""

from typing import Optional

from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPainter, QPen, QPainterPath, QMouseEvent, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)

from gui.envelope.envelope import Envelope, EnvelopePoint
from gui.styles import (
    ENVELOPE_ACTIVE_CYAN, ENVELOPE_INACTIVE_GREY, ENVELOPE_BACKGROUND,
    ENVELOPE_TOGGLE_ON, ENVELOPE_TOGGLE_OFF, ENVELOPE_PLAYHEAD
)


class EnvelopeCanvas(QFrame):
    """Canvas for drawing and displaying envelope curves.

    Signals:
        envelopeChanged(Envelope): Emitted when the envelope is modified by drawing
        drawingStarted(): Emitted when user starts drawing (to auto-enable envelope)
    """

    envelopeChanged = Signal(object)  # Envelope
    drawingStarted = Signal()

    # Canvas dimensions
    MIN_HEIGHT = 80
    PADDING = 8

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._envelope: Optional[Envelope] = None
        self._enabled = False
        self._drawing = False
        self._playhead_position: Optional[float] = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the canvas appearance."""
        self.setMinimumHeight(self.MIN_HEIGHT)
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMouseTracking(True)
        self._update_style()

    def _update_style(self):
        """Update the frame style based on enabled state."""
        border_color = ENVELOPE_ACTIVE_CYAN if self._enabled else ENVELOPE_INACTIVE_GREY
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ENVELOPE_BACKGROUND};
                border: 1px solid {border_color};
                border-radius: 4px;
            }}
        """)

    def set_envelope(self, envelope: Optional[Envelope]):
        """Set the envelope to display/edit."""
        self._envelope = envelope
        self._enabled = envelope.enabled if envelope else False
        self._update_style()
        self.update()

    def set_enabled(self, enabled: bool):
        """Set whether the envelope is enabled (affects color)."""
        self._enabled = enabled
        self._update_style()
        self.update()

    def set_playhead_position(self, position: Optional[float]):
        """Set playhead position (0.0-1.0) or None to hide."""
        self._playhead_position = position
        self.update()

    def clear(self):
        """Clear the envelope points."""
        if self._envelope:
            self._envelope.clear()
            self.envelopeChanged.emit(self._envelope)
            self.update()

    def _canvas_rect(self):
        """Get the drawable area rect."""
        return self.rect().adjusted(self.PADDING, self.PADDING,
                                     -self.PADDING, -self.PADDING)

    def _point_to_canvas(self, time: float, value: float) -> QPointF:
        """Convert envelope coordinates to canvas coordinates."""
        rect = self._canvas_rect()
        x = rect.x() + time * rect.width()
        y = rect.y() + (1.0 - value) * rect.height()  # Flip Y (0 at bottom)
        return QPointF(x, y)

    def _canvas_to_point(self, pos: QPointF) -> tuple[float, float]:
        """Convert canvas coordinates to envelope coordinates."""
        rect = self._canvas_rect()
        time = (pos.x() - rect.x()) / rect.width()
        value = 1.0 - (pos.y() - rect.y()) / rect.height()  # Flip Y
        return max(0.0, min(1.0, time)), max(0.0, min(1.0, value))

    def paintEvent(self, event):
        """Draw the envelope curve and playhead."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self._canvas_rect()

        # Draw grid lines (light grey, subtle)
        grid_pen = QPen(QColor('#333333'))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)

        # Vertical grid (8 divisions = 1 step each, matching 8-step sequencer)
        for i in range(1, 8):
            x = rect.x() + (i / 8) * rect.width()
            painter.drawLine(QPointF(x, rect.y()), QPointF(x, rect.bottom()))

        # Horizontal grid (2 divisions)
        for i in range(1, 2):
            y = rect.y() + (i / 2) * rect.height()
            painter.drawLine(QPointF(rect.x(), y), QPointF(rect.right(), y))

        # Draw envelope curve
        if self._envelope and not self._envelope.is_empty():
            curve_color = QColor(ENVELOPE_ACTIVE_CYAN if self._enabled else ENVELOPE_INACTIVE_GREY)
            pen = QPen(curve_color)
            pen.setWidth(1)
            painter.setPen(pen)

            # Build path from points
            path = QPainterPath()
            points = self._envelope.points

            if points:
                # Start from left edge at the same y-level as the first point
                first_point = points[0]
                left_edge = self._point_to_canvas(0.0, first_point.value)
                path.moveTo(left_edge)

                # Draw lines through all points
                for point in points:
                    pos = self._point_to_canvas(point.time, point.value)
                    path.lineTo(pos)

                # Extend to right edge at the same y-level as the last point
                last_point = points[-1]
                right_edge = self._point_to_canvas(1.0, last_point.value)
                path.lineTo(right_edge)

                painter.drawPath(path)

        # Draw playhead
        if self._playhead_position is not None and 0.0 <= self._playhead_position <= 1.0:
            playhead_pen = QPen(QColor(ENVELOPE_PLAYHEAD))
            playhead_pen.setWidth(2)
            painter.setPen(playhead_pen)
            x = rect.x() + self._playhead_position * rect.width()
            painter.drawLine(QPointF(x, rect.y()), QPointF(x, rect.bottom()))

        painter.end()

    def mousePressEvent(self, event: QMouseEvent):
        """Start drawing envelope on mouse press."""
        if event.button() == Qt.MouseButton.LeftButton and self._envelope:
            self._drawing = True
            # Clear existing points
            self._envelope.clear()

            # Add point at click position
            time, value = self._canvas_to_point(event.position())
            self._envelope.add_point(time, value)

            # Signal that drawing started (to auto-enable envelope)
            self.drawingStarted.emit()
            self.envelopeChanged.emit(self._envelope)
            self.update()
        elif event.button() == Qt.MouseButton.RightButton and self._envelope:
            # Right-click to clear
            self.clear()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Continue drawing envelope on mouse drag."""
        if self._drawing and self._envelope:
            time, value = self._canvas_to_point(event.position())

            # Only add points that move forward in time
            if self._envelope.points and time > self._envelope.points[-1].time:
                self._envelope.add_point(time, value)
                self.envelopeChanged.emit(self._envelope)
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stop drawing on mouse release."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drawing = False


class EnvelopePanel(QWidget):
    """Panel containing envelope label, toggle button, and drawing canvas.

    Signals:
        envelopeChanged(str, Envelope): Emitted when envelope is modified (control_key, envelope)
        enabledToggled(str, bool): Emitted when envelope enabled state changes (control_key, enabled)
    """

    envelopeChanged = Signal(str, object)  # control_key, Envelope
    enabledToggled = Signal(str, bool)  # control_key, enabled

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_control_key: Optional[str] = None
        self._current_envelope: Optional[Envelope] = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the panel layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Top bar: Label (left) + Toggle button (right)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel('No Control Selected')
        self._label.setStyleSheet('color: #A0A0A0; font-size: 12px;')
        top_bar.addWidget(self._label)

        top_bar.addStretch()

        self._toggle_btn = QPushButton('ENV')
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setFixedSize(50, 24)
        self._toggle_btn.setToolTip('Toggle envelope (R)')
        self._toggle_btn.clicked.connect(self._on_toggle_clicked)
        self._update_toggle_style()
        top_bar.addWidget(self._toggle_btn)

        layout.addLayout(top_bar)

        # Canvas
        self._canvas = EnvelopeCanvas()
        self._canvas.envelopeChanged.connect(self._on_canvas_changed)
        self._canvas.drawingStarted.connect(self._on_drawing_started)
        layout.addWidget(self._canvas)

    def _update_toggle_style(self):
        """Update toggle button style based on state."""
        if self._toggle_btn.isChecked():
            self._toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ENVELOPE_TOGGLE_ON};
                    border: 1px solid {ENVELOPE_TOGGLE_ON};
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: #5AA0E9;
                }}
            """)
        else:
            self._toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ENVELOPE_TOGGLE_OFF};
                    border: 1px solid #505050;
                    border-radius: 4px;
                    color: #A0A0A0;
                    font-weight: bold;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: #505050;
                }}
            """)

    def set_control(self, control_key: Optional[str], envelope: Optional[Envelope],
                    display_name: Optional[str] = None):
        """Set the current control to display/edit.

        Args:
            control_key: Control identifier (e.g., 'emitter.1.volume')
            envelope: The envelope for this control
            display_name: Human-readable name to show (defaults to control_key)
        """
        self._current_control_key = control_key
        self._current_envelope = envelope

        if control_key and envelope:
            self._label.setText(display_name or self._format_control_name(control_key))
            self._toggle_btn.setChecked(envelope.enabled)
            self._toggle_btn.setEnabled(True)
            self._canvas.set_envelope(envelope)
        else:
            self._label.setText('No Control Selected')
            self._toggle_btn.setChecked(False)
            self._toggle_btn.setEnabled(False)
            self._canvas.set_envelope(None)

        self._update_toggle_style()

    def _format_control_name(self, control_key: str) -> str:
        """Format a control key as a readable name."""
        parts = control_key.split('.')
        if len(parts) >= 2:
            if parts[0] == 'emitter':
                return f'Emitter {parts[1]} - {parts[2].replace("_", " ").title()}'
            elif parts[0] == 'track':
                return f'Track {parts[1]} - {parts[2].replace("_", " ").title()}'
            elif parts[0] == 'global':
                if len(parts) == 2:
                    return f'Global - {parts[1].replace("_", " ").title()}'
                return f'Global {parts[1].title()} - {parts[2].replace("_", " ").title()}'
        return control_key

    def set_playhead_position(self, position: Optional[float]):
        """Set the playhead position on the canvas."""
        self._canvas.set_playhead_position(position)

    def toggle_enabled(self):
        """Toggle the envelope enabled state."""
        self._toggle_btn.setChecked(not self._toggle_btn.isChecked())
        self._on_toggle_clicked()

    def _on_toggle_clicked(self):
        """Handle toggle button click."""
        self._update_toggle_style()
        enabled = self._toggle_btn.isChecked()
        self._canvas.set_enabled(enabled)

        if self._current_control_key and self._current_envelope:
            self._current_envelope.enabled = enabled
            self.enabledToggled.emit(self._current_control_key, enabled)

    def _on_drawing_started(self):
        """Handle drawing started - auto-enable the envelope."""
        if not self._toggle_btn.isChecked():
            self._toggle_btn.setChecked(True)
            self._on_toggle_clicked()

    def _on_canvas_changed(self, envelope: Envelope):
        """Handle envelope change from canvas."""
        if self._current_control_key:
            self.envelopeChanged.emit(self._current_control_key, envelope)

    @property
    def current_control_key(self) -> Optional[str]:
        """Get the current control key."""
        return self._current_control_key

    def clear_envelope(self):
        """Clear the current envelope."""
        self._canvas.clear()
