"""Transport controls panel with play/stop, BPM, and sequencer selection."""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QPushButton, QSpinBox, QLabel
)

from gui.styles import get_transport_button_style


class TransportPanel(QGroupBox):
    """
    Transport controls for playback, BPM, and sequencer selection.

    Features:
    - Play button (trigger note)
    - Stop button
    - Sequencer type selection (8 Track / 1 Track, mutually exclusive, both can be off)
    - BPM spinbox

    Signals:
        playClicked(): Emitted when play button clicked
        stopClicked(): Emitted when stop button clicked
        bpmChanged(int): Emitted when BPM value changes
        sequencerChanged(str or None): Emitted when sequencer selection changes
            Values: 'column' (8 Track), 'grid' (1 Track), or None (neither)
    """

    playClicked = Signal()
    stopClicked = Signal()
    bpmChanged = Signal(int)
    sequencerChanged = Signal(object)  # str or None

    def __init__(self, parent: QWidget = None):
        super().__init__('Transport', parent)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 2, 8, 9)

        # Transport buttons and sequencer selection
        button_layout = QHBoxLayout()
        button_layout.setSpacing(6)

        self._play_btn = QPushButton('\u25B6')  # Play triangle
        self._play_btn.setFixedSize(36, 26)
        self._play_btn.setToolTip('Play Note (Space)')
        self._play_btn.setStyleSheet(get_transport_button_style('play'))
        self._play_btn.clicked.connect(self.playClicked.emit)
        button_layout.addWidget(self._play_btn)

        self._stop_btn = QPushButton('\u25A0')  # Stop square
        self._stop_btn.setFixedSize(36, 26)
        self._stop_btn.setToolTip('Stop (Escape)')
        self._stop_btn.setStyleSheet(get_transport_button_style('stop'))
        self._stop_btn.clicked.connect(self.stopClicked.emit)
        button_layout.addWidget(self._stop_btn)

        # Sequencer type buttons (mutually exclusive, both can be off)
        self._seq_8track_btn = QPushButton('8 Track Seq')
        self._seq_8track_btn.setCheckable(True)
        self._seq_8track_btn.setFixedHeight(26)
        self._seq_8track_btn.setToolTip('Column Sequencer (8 independent tracks)')
        self._seq_8track_btn.clicked.connect(self._on_8track_clicked)
        button_layout.addWidget(self._seq_8track_btn)

        self._seq_1track_btn = QPushButton('1 Track Seq')
        self._seq_1track_btn.setCheckable(True)
        self._seq_1track_btn.setFixedHeight(26)
        self._seq_1track_btn.setToolTip('Grid Sequencer (64-step single sequence)')
        self._seq_1track_btn.clicked.connect(self._on_1track_clicked)
        button_layout.addWidget(self._seq_1track_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # BPM control
        bpm_layout = QHBoxLayout()
        bpm_layout.setSpacing(6)

        bpm_label = QLabel('BPM:')
        bpm_layout.addWidget(bpm_label)

        self._bpm_spinbox = QSpinBox()
        self._bpm_spinbox.setMinimum(20)
        self._bpm_spinbox.setMaximum(300)
        self._bpm_spinbox.setValue(120)
        self._bpm_spinbox.setFixedWidth(70)
        self._bpm_spinbox.setFixedHeight(24)
        self._bpm_spinbox.valueChanged.connect(self.bpmChanged.emit)
        bpm_layout.addWidget(self._bpm_spinbox)

        bpm_layout.addStretch()
        layout.addLayout(bpm_layout)

    def get_bpm(self) -> int:
        """Get current BPM value."""
        return self._bpm_spinbox.value()

    def set_bpm(self, value: int):
        """Set BPM value."""
        self._bpm_spinbox.setValue(value)

    def _on_8track_clicked(self):
        """Handle 8 Track Seq button click."""
        if self._seq_8track_btn.isChecked():
            # Turn off the other button
            self._seq_1track_btn.setChecked(False)
            self.sequencerChanged.emit('column')
        else:
            # Button was unchecked
            self.sequencerChanged.emit(None)

    def _on_1track_clicked(self):
        """Handle 1 Track Seq button click."""
        if self._seq_1track_btn.isChecked():
            # Turn off the other button
            self._seq_8track_btn.setChecked(False)
            self.sequencerChanged.emit('grid')
        else:
            # Button was unchecked
            self.sequencerChanged.emit(None)

    def get_sequencer(self) -> Optional[str]:
        """Get the selected sequencer type.

        Returns:
            'column' for 8 Track Seq, 'grid' for 1 Track Seq, or None if neither selected.
        """
        if self._seq_8track_btn.isChecked():
            return 'column'
        elif self._seq_1track_btn.isChecked():
            return 'grid'
        return None

    def set_sequencer(self, seq_type: Optional[str]):
        """Set the sequencer selection without emitting signals.

        Args:
            seq_type: 'column' for 8 Track, 'grid' for 1 Track, or None for neither.
        """
        self._seq_8track_btn.blockSignals(True)
        self._seq_1track_btn.blockSignals(True)

        self._seq_8track_btn.setChecked(seq_type == 'column')
        self._seq_1track_btn.setChecked(seq_type == 'grid')

        self._seq_8track_btn.blockSignals(False)
        self._seq_1track_btn.blockSignals(False)
