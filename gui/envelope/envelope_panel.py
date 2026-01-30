"""Envelope panel widget for drawing automation curves."""

from typing import Optional, Union

from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPainter, QPen, QPainterPath, QMouseEvent, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)

from gui.envelope.envelope import Envelope, EnvelopePoint
from gui.envelope.envelope_presets import EnvelopePreset, generate_preset_points
from gui.envelope.preset_button import PresetButton
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
        self._drawing_enabled = True  # Whether mouse drawing is allowed
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

    def set_drawing_enabled(self, enabled: bool):
        """Enable or disable mouse drawing."""
        self._drawing_enabled = enabled
        self.setCursor(Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.ArrowCursor)

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
        if not self._drawing_enabled:
            return

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

        # Tool state: can be EnvelopePreset, 'pencil', or None
        self._active_tool: Optional[Union[EnvelopePreset, str]] = None
        # Remember last tool when ENV is toggled off, default to pencil for first use
        self._last_active_tool: Optional[Union[EnvelopePreset, str]] = 'pencil'
        self._per_cell: bool = False

        self._setup_ui()

    def _setup_ui(self):
        """Set up the panel layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Top bar: Label only
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel('No Control Selected')
        self._label.setStyleSheet('color: #A0A0A0; font-size: 12px;')
        top_bar.addWidget(self._label)

        top_bar.addStretch()

        layout.addLayout(top_bar)

        # Preset bar
        preset_bar = QHBoxLayout()
        preset_bar.setContentsMargins(0, 0, 0, 0)
        preset_bar.setSpacing(4)

        # Preset buttons
        self._preset_buttons: dict[EnvelopePreset, PresetButton] = {}
        for preset in EnvelopePreset:
            btn = PresetButton(preset)
            btn.clicked.connect(lambda checked, p=preset: self._on_preset_clicked(p, checked))
            self._preset_buttons[preset] = btn
            preset_bar.addWidget(btn)

        # Pencil button (free-draw toggle) - next to presets
        self._pencil_btn = QPushButton('\u270F')  # Pencil unicode
        self._pencil_btn.setCheckable(True)
        self._pencil_btn.setChecked(False)  # Start unchecked, enables when ENV is on
        self._pencil_btn.setFixedSize(30, 24)
        self._pencil_btn.setToolTip('Enable free-draw mode')
        self._pencil_btn.clicked.connect(self._on_pencil_clicked)
        self._update_pencil_style()
        preset_bar.addWidget(self._pencil_btn)

        # Extra spacing between pencil and Per Cell
        preset_bar.addSpacing(12)

        # Per Cell button
        self._per_cell_btn = QPushButton('Per Cell')
        self._per_cell_btn.setCheckable(True)
        self._per_cell_btn.setFixedSize(60, 24)
        self._per_cell_btn.setToolTip('Repeat pattern 8 times (once per cell)')
        self._per_cell_btn.clicked.connect(self._on_per_cell_clicked)
        self._update_per_cell_style()
        preset_bar.addWidget(self._per_cell_btn)

        # ENV toggle button - next to Per Cell
        self._toggle_btn = QPushButton('ENV')
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setFixedSize(50, 24)
        self._toggle_btn.setToolTip('Toggle envelope (R)')
        self._toggle_btn.clicked.connect(self._on_toggle_clicked)
        self._update_toggle_style()
        preset_bar.addWidget(self._toggle_btn)

        preset_bar.addStretch()

        layout.addLayout(preset_bar)

        # Canvas
        self._canvas = EnvelopeCanvas()
        self._canvas.envelopeChanged.connect(self._on_canvas_changed)
        self._canvas.drawingStarted.connect(self._on_drawing_started)
        layout.addWidget(self._canvas)

        # Disable all drawing controls initially (ENV is off)
        self._set_drawing_controls_enabled(False)

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

        # Preserve the current ENV toggle state when switching controls
        env_was_enabled = self._toggle_btn.isChecked()

        if control_key and envelope:
            self._label.setText(display_name or self._format_control_name(control_key))
            self._toggle_btn.setEnabled(True)
            # Keep ENV in its current state, sync the envelope to match
            if env_was_enabled:
                envelope.enabled = True
            self._canvas.set_envelope(envelope)
            self._canvas.set_enabled(env_was_enabled)
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
        """Handle ENV toggle button click."""
        self._update_toggle_style()
        enabled = self._toggle_btn.isChecked()
        self._canvas.set_enabled(enabled)

        if enabled:
            # Entering envelope mode - enable drawing controls
            self._set_drawing_controls_enabled(True)
            # Restore the last active tool (defaults to pencil on first use)
            self._restore_last_tool()
        else:
            # Save current tool before clearing
            if self._active_tool is not None:
                self._last_active_tool = self._active_tool
            # Exiting envelope mode - disable and clear all selections
            self._clear_all_tool_selections()
            self._set_drawing_controls_enabled(False)

        if self._current_control_key and self._current_envelope:
            self._current_envelope.enabled = enabled
            self.enabledToggled.emit(self._current_control_key, enabled)

    def _on_drawing_started(self):
        """Handle drawing started - auto-enable ENV and select pencil."""
        # Auto-enable ENV if not enabled
        if not self._toggle_btn.isChecked():
            self._toggle_btn.setChecked(True)
            self._on_toggle_clicked()

        # Auto-select pencil tool if not already selected
        if self._active_tool != 'pencil':
            self._clear_all_tool_selections()
            self._pencil_btn.setChecked(True)
            self._active_tool = 'pencil'
            self._update_pencil_style()
            self._canvas.set_drawing_enabled(True)

            # Disable Per Cell (free-draw doesn't support per-cell)
            self._per_cell_btn.setEnabled(False)
            self._update_per_cell_style()

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

    def _on_preset_clicked(self, preset: EnvelopePreset, checked: bool):
        """Handle preset button click."""
        if not self._toggle_btn.isChecked():
            # ENV is off, ignore (shouldn't happen if buttons are disabled)
            return

        if checked:
            # Deselect any other tool (presets or pencil)
            self._clear_all_tool_selections()

            # Select this preset
            self._preset_buttons[preset].setChecked(True)
            self._active_tool = preset

            # Enable Per Cell (presets support per-cell mode)
            self._per_cell_btn.setEnabled(True)
            self._update_per_cell_style()

            # Apply the preset pattern
            self._apply_preset()
        else:
            # Clicking same button again - deselect
            self._active_tool = None

        # Canvas drawing only when pencil is active
        self._canvas.set_drawing_enabled(self._active_tool == 'pencil')

    def _on_per_cell_clicked(self):
        """Handle Per Cell button click."""
        self._per_cell = self._per_cell_btn.isChecked()
        self._update_per_cell_style()
        # Redraw if preset is active
        if isinstance(self._active_tool, EnvelopePreset):
            self._apply_preset()

    def _on_pencil_clicked(self):
        """Handle Pencil button click."""
        if not self._toggle_btn.isChecked():
            # ENV is off, ignore
            return

        checked = self._pencil_btn.isChecked()

        if checked:
            # Deselect any other tool
            self._clear_all_tool_selections()

            # Select pencil
            self._pencil_btn.setChecked(True)
            self._active_tool = 'pencil'

            # Disable Per Cell (free-draw doesn't support per-cell)
            self._per_cell_btn.setEnabled(False)
            self._update_per_cell_style()
        else:
            # Clicking pencil again - deselect
            self._active_tool = None

            # Re-enable Per Cell
            self._per_cell_btn.setEnabled(True)
            self._update_per_cell_style()

        self._update_pencil_style()

        # Enable canvas drawing only when pencil is selected
        self._canvas.set_drawing_enabled(self._active_tool == 'pencil')

    def _apply_preset(self):
        """Apply the active preset to the envelope."""
        if not self._current_envelope or not isinstance(self._active_tool, EnvelopePreset):
            return

        points = generate_preset_points(self._active_tool, self._per_cell)
        self._current_envelope.clear()
        for time, value in points:
            self._current_envelope.add_point(time, value)

        # Refresh the canvas display
        self._canvas.set_envelope(self._current_envelope)
        self._canvas.update()

        if self._current_control_key:
            self.envelopeChanged.emit(self._current_control_key, self._current_envelope)

    def _update_per_cell_style(self):
        """Update Per Cell button style based on state."""
        if not self._per_cell_btn.isEnabled():
            # Disabled style
            self._per_cell_btn.setStyleSheet("""
                QPushButton {
                    background-color: #353535;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    color: #606060;
                    font-size: 10px;
                }
            """)
        elif self._per_cell_btn.isChecked():
            self._per_cell_btn.setStyleSheet(f"""
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
            self._per_cell_btn.setStyleSheet(f"""
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

    def _update_pencil_style(self):
        """Update Pencil button style based on state."""
        if not self._pencil_btn.isEnabled():
            # Disabled style
            self._pencil_btn.setStyleSheet("""
                QPushButton {
                    background-color: #353535;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    color: #606060;
                    font-size: 14px;
                }
            """)
        elif self._pencil_btn.isChecked():
            self._pencil_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ENVELOPE_TOGGLE_ON};
                    border: 1px solid {ENVELOPE_TOGGLE_ON};
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: #5AA0E9;
                }}
            """)
        else:
            self._pencil_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ENVELOPE_TOGGLE_OFF};
                    border: 1px solid #505050;
                    border-radius: 4px;
                    color: #A0A0A0;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: #505050;
                }}
            """)

    def _set_drawing_controls_enabled(self, enabled: bool):
        """Enable or disable all drawing-related controls based on ENV state."""
        # Preset buttons
        for btn in self._preset_buttons.values():
            btn.setEnabled(enabled)
            btn.update_style()  # Update visual style

        # Pencil button
        self._pencil_btn.setEnabled(enabled)
        self._update_pencil_style()

        # Per Cell button - disabled when pencil is active (free-draw doesn't support per-cell)
        pencil_active = self._active_tool == 'pencil'
        self._per_cell_btn.setEnabled(enabled and not pencil_active)
        self._update_per_cell_style()

        # Canvas drawing - only enabled if ENV is on AND pencil is selected
        self._canvas.set_drawing_enabled(enabled and pencil_active)

    def _clear_all_tool_selections(self):
        """Clear all button highlights and reset active tool."""
        # Uncheck all preset buttons
        for btn in self._preset_buttons.values():
            btn.setChecked(False)

        # Uncheck pencil button and update its style
        self._pencil_btn.setChecked(False)
        self._update_pencil_style()

        # Clear active tool
        self._active_tool = None

        # Disable canvas drawing
        self._canvas.set_drawing_enabled(False)

    def _restore_last_tool(self):
        """Restore the last active tool when ENV is toggled on."""
        if self._last_active_tool == 'pencil':
            # Restore pencil
            self._pencil_btn.setChecked(True)
            self._active_tool = 'pencil'
            self._update_pencil_style()
            self._canvas.set_drawing_enabled(True)
            # Disable Per Cell for pencil
            self._per_cell_btn.setEnabled(False)
            self._update_per_cell_style()
        elif isinstance(self._last_active_tool, EnvelopePreset):
            # Restore preset
            self._preset_buttons[self._last_active_tool].setChecked(True)
            self._active_tool = self._last_active_tool
            # Enable Per Cell for presets
            self._per_cell_btn.setEnabled(True)
            self._update_per_cell_style()
