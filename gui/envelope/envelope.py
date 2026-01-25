"""Envelope data model for automation curves."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EnvelopePoint:
    """A point on an envelope curve.

    Attributes:
        time: Position in the envelope (0.0 to 1.0)
        value: Value at this position (0.0 to 1.0)
    """
    time: float
    value: float

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {'time': self.time, 'value': self.value}

    @classmethod
    def from_dict(cls, data: dict) -> 'EnvelopePoint':
        """Create from dictionary."""
        return cls(time=data['time'], value=data['value'])


@dataclass
class Envelope:
    """An automation envelope that modulates a control value.

    The envelope defines a curve over time (0.0 to 1.0) that is applied
    as a factor to the control's base value. The envelope loops every
    8 beats when the sequencer is running.

    Attributes:
        points: List of envelope points, sorted by time
        enabled: Whether the envelope is active
    """
    points: list[EnvelopePoint] = field(default_factory=list)
    enabled: bool = False

    def add_point(self, time: float, value: float):
        """Add a point to the envelope.

        Points are automatically sorted by time.

        Args:
            time: Position in envelope (0.0 to 1.0)
            value: Value at this position (0.0 to 1.0)
        """
        time = max(0.0, min(1.0, time))
        value = max(0.0, min(1.0, value))
        self.points.append(EnvelopePoint(time, value))
        self.points.sort(key=lambda p: p.time)

    def clear(self):
        """Remove all points from the envelope."""
        self.points.clear()

    def get_value_at(self, time: float) -> float:
        """Get the envelope value at a given time via linear interpolation.

        Args:
            time: Position in envelope (0.0 to 1.0)

        Returns:
            Interpolated value (0.0 to 1.0). Returns 1.0 if envelope is empty.
        """
        if not self.points:
            return 1.0

        time = max(0.0, min(1.0, time))

        # Find surrounding points
        before: Optional[EnvelopePoint] = None
        after: Optional[EnvelopePoint] = None

        for point in self.points:
            if point.time <= time:
                before = point
            elif after is None:
                after = point
                break

        # Handle edge cases
        if before is None and after is None:
            return 1.0
        if before is None:
            return after.value
        if after is None:
            return before.value
        if before.time == after.time:
            return before.value

        # Linear interpolation
        t = (time - before.time) / (after.time - before.time)
        return before.value + t * (after.value - before.value)

    def is_empty(self) -> bool:
        """Check if envelope has no points."""
        return len(self.points) == 0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'points': [p.to_dict() for p in self.points],
            'enabled': self.enabled
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Envelope':
        """Create from dictionary."""
        points = [EnvelopePoint.from_dict(p) for p in data.get('points', [])]
        return cls(points=points, enabled=data.get('enabled', False))

    def copy(self) -> 'Envelope':
        """Create a deep copy of this envelope."""
        return Envelope(
            points=[EnvelopePoint(p.time, p.value) for p in self.points],
            enabled=self.enabled
        )
