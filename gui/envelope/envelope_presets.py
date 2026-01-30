"""Predefined envelope patterns."""
import math
from enum import Enum
from typing import List, Tuple


class EnvelopePreset(Enum):
    """Available envelope preset patterns."""
    RAMP_UP = "ramp_up"
    RAMP_DOWN = "ramp_down"
    TRIANGLE = "triangle"
    TRIANGLE_DOWN = "triangle_down"
    SQUARE = "square"
    SQUARE_UP = "square_up"
    ROUNDED = "rounded"


def generate_preset_points(preset: EnvelopePreset, per_cell: bool = False) -> List[Tuple[float, float]]:
    """Generate envelope points for a preset.

    Args:
        preset: The preset type
        per_cell: If True, repeat pattern 8 times (once per cell/beat)

    Returns:
        List of (time, value) tuples, normalized 0.0-1.0
    """
    # Generate base pattern (single occurrence)
    base_points = _get_base_points(preset)

    if not per_cell:
        return base_points

    # Repeat 8 times for per-cell mode
    repeated = []
    for cell in range(8):
        cell_start = cell / 8.0
        cell_width = 1.0 / 8.0
        for time, value in base_points:
            repeated.append((cell_start + time * cell_width, value))
    return repeated


def _get_base_points(preset: EnvelopePreset) -> List[Tuple[float, float]]:
    """Get base points for a single pattern occurrence."""
    if preset == EnvelopePreset.RAMP_UP:
        return [(0.0, 0.0), (1.0, 1.0)]
    elif preset == EnvelopePreset.RAMP_DOWN:
        return [(0.0, 1.0), (1.0, 0.0)]
    elif preset == EnvelopePreset.TRIANGLE:
        # Point at top (peak in middle)
        return [(0.0, 0.0), (0.5, 1.0), (1.0, 0.0)]
    elif preset == EnvelopePreset.TRIANGLE_DOWN:
        # Vertical flip - point at bottom (valley in middle)
        return [(0.0, 1.0), (0.5, 0.0), (1.0, 1.0)]
    elif preset == EnvelopePreset.SQUARE:
        # Starts high, drops to low at midpoint
        return [(0.0, 1.0), (0.49, 1.0), (0.5, 0.0), (1.0, 0.0)]
    elif preset == EnvelopePreset.SQUARE_UP:
        # Horizontal flip - starts low, jumps to high at midpoint
        return [(0.0, 0.0), (0.49, 0.0), (0.5, 1.0), (1.0, 1.0)]
    elif preset == EnvelopePreset.ROUNDED:
        # Top half of ellipse - smooth curve from 0 to 1 and back
        points = []
        num_points = 20
        for i in range(num_points + 1):
            x = i / num_points
            # y = sqrt(1 - (2x-1)^2) gives top half of unit circle centered at (0.5, 0)
            y = math.sqrt(max(0, 1 - (2 * x - 1) ** 2))
            points.append((x, y))
        return points
    return []
