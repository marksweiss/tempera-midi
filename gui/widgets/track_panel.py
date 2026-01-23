"""Track volume controls panel."""

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QSlider, QLabel, QPushButton
)

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
    """

    volumeChanged = Signal(int, int)
    volumeSet = Signal(int, int)
    recordClicked = Signal(int)

    def __init__(self, parent: QWidget = None):
        super().__init__('Tracks', parent)

        self._sliders: dict[int, QSlider] = {}
        self._value_labels: dict[int, QLabel] = {}
        self._record_buttons: dict[int, QPushButton] = {}
        self._record_timers: dict[int, QTimer] = {}

        self._setup_ui()

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
