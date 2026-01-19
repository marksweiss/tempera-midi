"""Transport controls panel with play/stop and BPM."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QPushButton, QSpinBox, QLabel
)


class TransportPanel(QGroupBox):
    """
    Transport controls for playback and BPM.

    Features:
    - Play button (trigger note)
    - Stop button
    - BPM spinbox

    Signals:
        playClicked(): Emitted when play button clicked
        stopClicked(): Emitted when stop button clicked
        bpmChanged(int): Emitted when BPM value changes
    """

    playClicked = Signal()
    stopClicked = Signal()
    bpmChanged = Signal(int)

    def __init__(self, parent: QWidget = None):
        super().__init__('Transport', parent)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Transport buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self._play_btn = QPushButton('\u25B6')  # Play triangle
        self._play_btn.setFixedSize(40, 32)
        self._play_btn.setToolTip('Play Note (Space)')
        self._play_btn.clicked.connect(self.playClicked.emit)
        button_layout.addWidget(self._play_btn)

        self._stop_btn = QPushButton('\u25A0')  # Stop square
        self._stop_btn.setFixedSize(40, 32)
        self._stop_btn.setToolTip('Stop (Escape)')
        self._stop_btn.clicked.connect(self.stopClicked.emit)
        button_layout.addWidget(self._stop_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # BPM control
        bpm_layout = QHBoxLayout()
        bpm_layout.setSpacing(8)

        bpm_label = QLabel('BPM:')
        bpm_layout.addWidget(bpm_label)

        self._bpm_spinbox = QSpinBox()
        self._bpm_spinbox.setMinimum(20)
        self._bpm_spinbox.setMaximum(300)
        self._bpm_spinbox.setValue(120)
        self._bpm_spinbox.setFixedWidth(70)
        self._bpm_spinbox.valueChanged.connect(self.bpmChanged.emit)
        bpm_layout.addWidget(self._bpm_spinbox)

        bpm_layout.addStretch()
        layout.addLayout(bpm_layout)

        layout.addStretch()

    def get_bpm(self) -> int:
        """Get current BPM value."""
        return self._bpm_spinbox.value()

    def set_bpm(self, value: int):
        """Set BPM value."""
        self._bpm_spinbox.setValue(value)
