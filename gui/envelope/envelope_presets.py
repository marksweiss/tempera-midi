"""Predefined envelope patterns."""
from enum import Enum
from typing import List, Tuple


class EnvelopePreset(Enum):
    """Available envelope preset patterns."""
    RAMP_UP = "ramp_up"
    RAMP_DOWN = "ramp_down"
    TRIANGLE = "triangle"
    S_CURVE = "s_curve"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"


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
        return [(0.0, 0.0), (0.5, 1.0), (1.0, 0.0)]
    elif preset == EnvelopePreset.S_CURVE:
        # Approximate sigmoid with multiple points
        return [(0.0, 0.0), (0.25, 0.1), (0.5, 0.5), (0.75, 0.9), (1.0, 1.0)]
    elif preset == EnvelopePreset.SQUARE:
        return [(0.0, 1.0), (0.49, 1.0), (0.5, 0.0), (1.0, 0.0)]
    elif preset == EnvelopePreset.SAWTOOTH:
        return [(0.0, 0.0), (0.9, 1.0), (0.91, 0.0), (1.0, 0.0)]
    return []
