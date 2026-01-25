"""Envelope timing manager for synchronizing automation with sequencer."""

import asyncio
import time
from typing import Callable, Optional

from PySide6.QtCore import QObject, Signal


class EnvelopeManager(QObject):
    """Manages envelope timing and synchronization with the sequencer.

    The manager tracks the current position in an 8-beat cycle and provides
    timing information for envelope interpolation.

    Signals:
        positionChanged(float): Emitted when position changes (0.0 to 1.0)
        tickUpdate(): Emitted on each update tick (~60fps) when running
    """

    positionChanged = Signal(float)
    tickUpdate = Signal()

    # Update rate (approximately 60 fps)
    UPDATE_INTERVAL_MS = 16

    def __init__(self, bpm: int = 120, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._bpm = bpm
        self._running = False
        self._position = 0.0  # 0.0 to 1.0 (normalized position in 8-beat cycle)
        self._start_time: Optional[float] = None
        self._update_task: Optional[asyncio.Task] = None

        # Callbacks for envelope modulation
        self._on_tick: Optional[Callable[[float], None]] = None

    @property
    def bpm(self) -> int:
        """Get current BPM."""
        return self._bpm

    @bpm.setter
    def bpm(self, value: int):
        """Set BPM."""
        self._bpm = max(20, min(300, value))

    @property
    def position(self) -> float:
        """Get current position in cycle (0.0 to 1.0)."""
        return self._position

    @property
    def is_running(self) -> bool:
        """Check if timing loop is running."""
        return self._running

    def set_tick_callback(self, callback: Optional[Callable[[float], None]]):
        """Set callback for tick updates.

        The callback receives the current position (0.0 to 1.0).
        """
        self._on_tick = callback

    def _beats_to_seconds(self, beats: float) -> float:
        """Convert beats to seconds at current BPM."""
        return (beats / self._bpm) * 60.0

    def _get_cycle_duration(self) -> float:
        """Get the duration of one 8-beat cycle in seconds."""
        return self._beats_to_seconds(8.0)

    def start(self):
        """Start the timing loop."""
        if self._running:
            return

        self._running = True
        self._start_time = time.monotonic()
        self._position = 0.0

        # Start the update task
        self._update_task = asyncio.create_task(self._update_loop())

    async def stop(self):
        """Stop the timing loop."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None
        self._position = 0.0
        self.positionChanged.emit(0.0)

    def reset(self):
        """Reset position to start of cycle."""
        self._start_time = time.monotonic()
        self._position = 0.0
        self.positionChanged.emit(0.0)

    async def _update_loop(self):
        """Main update loop running at ~60fps."""
        try:
            while self._running:
                self._update_position()

                # Emit signals
                self.positionChanged.emit(self._position)
                self.tickUpdate.emit()

                # Call tick callback if set
                if self._on_tick:
                    self._on_tick(self._position)

                # Wait for next update
                await asyncio.sleep(self.UPDATE_INTERVAL_MS / 1000.0)
        except asyncio.CancelledError:
            pass

    def _update_position(self):
        """Update the current position based on elapsed time."""
        if self._start_time is None:
            return

        elapsed = time.monotonic() - self._start_time
        cycle_duration = self._get_cycle_duration()

        # Calculate position in cycle (0.0 to 1.0), looping
        self._position = (elapsed % cycle_duration) / cycle_duration

    def get_value_at_current_position(self, envelope) -> float:
        """Get envelope value at current position.

        Args:
            envelope: Envelope object to evaluate

        Returns:
            Envelope value at current position (0.0 to 1.0)
        """
        if envelope is None or not envelope.enabled:
            return 1.0
        return envelope.get_value_at(self._position)

    def apply_envelope_to_value(self, base_value: int, envelope) -> int:
        """Apply envelope modulation to a base MIDI value.

        Args:
            base_value: Base MIDI CC value (0-127)
            envelope: Envelope to apply

        Returns:
            Modulated value (0-127)
        """
        if envelope is None or not envelope.enabled:
            return base_value

        factor = envelope.get_value_at(self._position)
        return int(base_value * factor)
