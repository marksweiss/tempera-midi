"""Track volume controls panel."""

from PySide6.QtCore import Qt, Signal, QTimer, QEvent
from PySide6.QtGui import QKeyEvent, QFocusEvent
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QSlider, QLabel, QPushButton, QApplication
)

from gui.styles import get_slider_focus_style, get_section_focus_style

# Style for record buttons - red circle like a tape deck record button
RECORD_BUTTON_STYLE = """
    QPushButton {
        background-color: #8B0000;
        border: 1px solid #5C0000;
        border-radius: 6px;
        min-width: 12px;
        max-width: 12px;
        min-height: 12px;
        max-height: 12px;
    }
    QPushButton:hover {
        background-color: #A00000;
        border-color: #700000;
    }
    QPushButton:checked {
        background-color: #FF0000;
        border-color: #AA0000;
        border-style: inset;
    }
"""


class TrackPanel(QGroupBox):
    """
    Panel for controlling 8 track volumes with record arm buttons.

    Each track has:
    - Vertical volume slider (0-127)
    - Track number label
    - Record arm button

    Signals:
        volumeChanged(int, int): Emitted when volume changes (track_num, value)
        volumeSet(int, int): Emitted when slider released (track_num, value)
        recordClicked(int): Emitted when record button clicked (track_num)
        controlFocusRequested(int, int): Emitted when a track slider is clicked (track_index, 0)
    """

    volumeChanged = Signal(int, int)
    volumeSet = Signal(int, int)
    recordClicked = Signal(int)
    controlFocusRequested = Signal(int, int)
    # Signals for keyboard navigation within panel
    subsectionNavigated = Signal(int)  # Emitted when track changes via keyboard (track_index 0-based)

    def __init__(self, parent: QWidget = None):
        super().__init__('Tracks', parent)

        self._sliders: dict[int, QSlider] = {}
        self._value_labels: dict[int, QLabel] = {}
        self._record_buttons: dict[int, QPushButton] = {}
        self._record_timers: dict[int, QTimer] = {}

        # Keyboard navigation state
        self._focused_track = -1  # -1 means no track focused
        self._panel_focused = False
        self._in_control_mode = False  # Whether we're navigating tracks

        self._setup_ui()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(2)  # Minimal spacing between label and sliders
        main_layout.setContentsMargins(8, 0, 8, 8)  # No top margin - group box title provides spacing

        # Volume label just above sliders
        volume_label = QLabel('Volume')
        volume_label.setStyleSheet('font-size: 11px; color: #A0A0A0;')
        main_layout.addWidget(volume_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Horizontal layout for track controls
        tracks_layout = QHBoxLayout()
        tracks_layout.setSpacing(8)

        for track in range(1, 9):
            track_widget = self._create_track_control(track)
            tracks_layout.addWidget(track_widget)

        main_layout.addLayout(tracks_layout)

    def _create_track_control(self, track_num: int) -> QWidget:
        """Create controls for a single track."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        layout.setContentsMargins(2, 2, 2, 2)

        # Value label at top
        value_label = QLabel('100')
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFixedWidth(32)
        self._value_labels[track_num] = value_label
        layout.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Vertical slider
        slider = QSlider(Qt.Orientation.Vertical)
        slider.setMinimum(0)
        slider.setMaximum(127)
        slider.setValue(100)
        slider.setTracking(True)
        slider.setFixedWidth(24)
        slider.setMinimumHeight(160)
        self._sliders[track_num] = slider
        layout.addWidget(slider, alignment=Qt.AlignmentFlag.AlignCenter)

        # Connect slider signals
        slider.valueChanged.connect(lambda v, t=track_num: self._on_value_changed(t, v))
        slider.sliderReleased.connect(lambda t=track_num: self._on_slider_released(t))

        # Install event filter for click detection
        slider.installEventFilter(self)

        # Track number label
        track_label = QLabel(str(track_num))
        track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(track_label)

        # Record button - red circle like tape deck
        record_btn = QPushButton()
        record_btn.setFixedSize(12, 12)
        record_btn.setCheckable(True)
        record_btn.setStyleSheet(RECORD_BUTTON_STYLE)
        record_btn.setToolTip(f'Arm Track {track_num} for Recording')
        record_btn.clicked.connect(lambda checked, t=track_num: self._on_record_clicked(t))
        self._record_buttons[track_num] = record_btn
        layout.addWidget(record_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Timer to auto-release record button after 15 seconds
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda t=track_num: self._on_record_timeout(t))
        self._record_timers[track_num] = timer

        return widget

    def _on_record_clicked(self, track_num: int):
        """Handle record button click."""
        btn = self._record_buttons[track_num]
        if btn.isChecked():
            # Button was just pressed - start timer and emit signal
            self._record_timers[track_num].start(15000)  # 15 seconds
            self.recordClicked.emit(track_num)
        else:
            # Button was manually unchecked - stop timer
            self._record_timers[track_num].stop()

    def _on_record_timeout(self, track_num: int):
        """Handle record button timeout - auto-release after 15 seconds."""
        self._record_buttons[track_num].setChecked(False)

    def _on_value_changed(self, track_num: int, value: int):
        """Handle slider value change."""
        self._value_labels[track_num].setText(str(value))
        self.volumeChanged.emit(track_num, value)

    def _on_slider_released(self, track_num: int):
        """Handle slider release."""
        self.volumeSet.emit(track_num, self._sliders[track_num].value())

    def get_volume(self, track_num: int) -> int:
        """Get a track's volume."""
        return self._sliders[track_num].value()

    def set_volume(self, track_num: int, value: int):
        """Set a track's volume without emitting signals."""
        slider = self._sliders[track_num]
        slider.blockSignals(True)
        slider.setValue(value)
        self._value_labels[track_num].setText(str(value))
        slider.blockSignals(False)

    def set_all_volumes(self, volumes: dict[int, int]):
        """Set all track volumes."""
        for track_num, value in volumes.items():
            self.set_volume(track_num, value)

    def get_all_volumes(self) -> dict[int, int]:
        """Get all track volumes."""
        return {t: s.value() for t, s in self._sliders.items()}

    # --- Keyboard navigation ---

    def set_panel_focused(self, focused: bool):
        """Set whether this panel is the active section."""
        self._panel_focused = focused
        self.setStyleSheet(get_section_focus_style(focused))
        # Clear track focus when panel loses focus
        if not focused:
            self.clear_track_focus()
            self._in_control_mode = False

    def set_track_focus(self, track_num: int):
        """Focus a specific track (1-8) or -1 to unfocus all.

        Args:
            track_num: Track number (1-8), or -1 to unfocus
        """
        # Clear previous focus
        if self._focused_track > 0 and self._focused_track in self._sliders:
            self._sliders[self._focused_track].setStyleSheet(get_slider_focus_style(False))

        # Set new focus
        self._focused_track = track_num if 1 <= track_num <= 8 else -1

        if self._focused_track > 0:
            self._sliders[self._focused_track].setStyleSheet(get_slider_focus_style(True))

    def focus_next_track(self):
        """Move focus to next track, wrapping at end."""
        if self._focused_track < 1:
            self.set_track_focus(1)
        else:
            new_track = (self._focused_track % 8) + 1
            self.set_track_focus(new_track)

    def focus_prev_track(self):
        """Move focus to previous track, wrapping at start."""
        if self._focused_track < 1:
            self.set_track_focus(8)
        else:
            new_track = ((self._focused_track - 2) % 8) + 1
            self.set_track_focus(new_track)

    def clear_track_focus(self):
        """Clear focus from all tracks."""
        self.set_track_focus(-1)

    def adjust_focused_volume(self, delta: int):
        """Adjust volume of focused track.

        Args:
            delta: Amount to add (positive or negative)
        """
        if self._focused_track > 0 and self._focused_track in self._sliders:
            slider = self._sliders[self._focused_track]
            new_value = slider.value() + delta
            new_value = max(0, min(127, new_value))
            if new_value != slider.value():
                slider.setValue(new_value)
                self._value_labels[self._focused_track].setText(str(new_value))
                self.volumeChanged.emit(self._focused_track, new_value)
                self.volumeSet.emit(self._focused_track, new_value)

    def reset_focused_to_default(self):
        """Reset focused track to default volume (100)."""
        if self._focused_track > 0:
            self.set_volume(self._focused_track, 100)
            self.volumeChanged.emit(self._focused_track, 100)
            self.volumeSet.emit(self._focused_track, 100)

    def get_navigation_path(self) -> str:
        """Get current navigation path string."""
        if self._focused_track > 0:
            volume = self._sliders[self._focused_track].value()
            return f"Tracks > Track {self._focused_track}: {volume}"
        return "Tracks"

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for track navigation."""
        key = event.key()

        # Left/Right or A/D to select track
        if key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self.focus_prev_track()
            # Emit signal with 0-based track index
            if self._focused_track > 0:
                self.subsectionNavigated.emit(self._focused_track - 1)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self.focus_next_track()
            # Emit signal with 0-based track index
            if self._focused_track > 0:
                self.subsectionNavigated.emit(self._focused_track - 1)
        # Up/Down or W/S to adjust volume
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_W):
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.adjust_focused_volume(10)
            else:
                self.adjust_focused_volume(1)
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.adjust_focused_volume(-10)
            else:
                self.adjust_focused_volume(-1)
        # X or Delete to reset
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Delete):
            self.reset_focused_to_default()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event: QFocusEvent):
        """Handle focus gained - show panel highlight only."""
        super().focusInEvent(event)
        self.set_panel_focused(True)
        # Don't auto-focus a track - NavigationManager controls that

    def focusOutEvent(self, event: QFocusEvent):
        """Handle focus lost - only clear if focus left the panel hierarchy."""
        super().focusOutEvent(event)
        # Only clear if focus went OUTSIDE this panel hierarchy
        new_focus = QApplication.focusWidget()
        if new_focus is None or not self.isAncestorOf(new_focus):
            self.set_panel_focused(False)

    def enter_control_mode(self, control_index: int = 0):
        """Enter control mode - start navigating tracks.

        For TrackPanel, the subsection represents the track, and control_index
        is not used since each track only has one control (volume). The track
        focus should already be set via set_track_focus before this is called.

        Args:
            control_index: Not used for TrackPanel (kept for API consistency)
        """
        self._in_control_mode = True
        # Only set default focus if no track is focused yet
        if self._focused_track < 1:
            self.set_track_focus(1)

    def exit_control_mode(self):
        """Exit control mode - return to panel focus."""
        self._in_control_mode = False
        self.clear_track_focus()

    def eventFilter(self, obj, event):
        """Filter events to detect track slider clicks."""
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                # Find which track this slider belongs to
                for track_num, slider in self._sliders.items():
                    if obj == slider:
                        # Track index is track_num - 1 (0-based), control is always 0
                        self.controlFocusRequested.emit(track_num - 1, 0)
                        break
        return super().eventFilter(obj, event)
