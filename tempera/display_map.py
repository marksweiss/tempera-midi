"""Map MIDI CC values (0-127) to the parameter values Tempera displays.

Many Tempera parameters do not scale linearly from CC 0-127 (e.g. Grain length
runs 0.0-8.0 along a curve). Each mapping is a sorted list of sampled
(cc, displayed_value) breakpoints; values between breakpoints are linearly
interpolated. Tempera's own curves appear to be piecewise-linear, so a few
well-placed breakpoints reproduce them exactly.

Only the emitter parameters in SAMPLED_PARAMS have non-linear curves. Their
breakpoint data lives in `display_maps.json` next to this module and is written
by `tools/sample_cc.py`. Parameters in STEPPED_PARAMS show one of a fixed list of
labels (e.g. Grain length Note's musical intervals) spread evenly across CC 0-127.
Parameters in LINEAR_PARAMS scale linearly over a known
range and need no sampling. Keys are Emitter CC map names (e.g. 'grain_length_cell').
"""

import json
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path

DISPLAY_MAPS_PATH = Path(__file__).with_name('display_maps.json')

MIN_CC = 0
MAX_CC = 127

# Emitter parameters whose CC -> value curve is non-linear and must be sampled from the device
SAMPLED_PARAMS = (
    'grain_density',      # 0.0-100.0
    'grain_length_cell',  # 0.0-8.0
    'relative_x',         # 0.0-8.0
    'relative_y',         # 0.0-8.0
    'spray_x',            # 0.0-8.0
    'spray_y',            # 0.0-8.0
)

# Musical intervals Grain length Note steps through, longest to shortest
GRAIN_LENGTH_NOTE_LABELS = (
    '16/1', '8/1', '4/1', '2/1', '1/1',
    '1/2', '1/3', '1/4', '1/5', '1/6', '1/7', '1/8', '1/9', '1/10', '1/11', '1/12',
    '1/16', '1/24', '1/32', '1/64',
)

# Emitter parameters that step through a fixed list of labels, evenly divided across CC 0-127
STEPPED_PARAMS = {
    'grain_length_note': GRAIN_LENGTH_NOTE_LABELS,
}

# Emitter parameters that scale linearly from CC 0-127 over a known (min, max) range
LINEAR_PARAMS = {
    'grain_shape': (0.0, 1.0),
    'grain_shape_attack': (0.0, 1.0),
    'grain_pan': (0.0, 1.0),
    'grain_tune_spread': (0.0, 1.0),
    'tone_filter_width': (0.0, 1.0),
    'tone_filter_center': (0.0, 1.0),
    'effects_send': (0.0, 1.0),
}
LINEAR_DECIMALS = 2


@dataclass(frozen=True)
class DisplayMap:
    """Piecewise-linear mapping from CC value to displayed parameter value.

    Args:
        points: (cc, value) breakpoints. Need not be sorted; at least one required.
        decimals: Number of decimal places to show when formatting.
        unit: Optional suffix appended when formatting (e.g. 'ms', '%').
    """
    points: tuple[tuple[int, float], ...]
    decimals: int = 2
    unit: str = ''

    def __post_init__(self):
        if not self.points:
            raise ValueError('DisplayMap requires at least one point')
        ordered = tuple(sorted((int(cc), float(v)) for cc, v in self.points))
        ccs = [cc for cc, _ in ordered]
        if len(set(ccs)) != len(ccs):
            raise ValueError(f'DisplayMap has duplicate CC values: {ccs}')
        if ccs[0] < MIN_CC or ccs[-1] > MAX_CC:
            raise ValueError(f'DisplayMap CC values must be in range {MIN_CC}..{MAX_CC}, got {ccs}')
        object.__setattr__(self, 'points', ordered)

    def value(self, cc: int) -> float:
        """Interpolated display value for a CC value. Clamps outside the sampled range."""
        ccs = [p[0] for p in self.points]
        if cc <= ccs[0]:
            return self.points[0][1]
        if cc >= ccs[-1]:
            return self.points[-1][1]
        i = bisect_right(ccs, cc)
        (cc_lo, v_lo), (cc_hi, v_hi) = self.points[i - 1], self.points[i]
        return v_lo + (v_hi - v_lo) * (cc - cc_lo) / (cc_hi - cc_lo)

    def format(self, cc: int) -> str:
        """Display string for a CC value."""
        text = f'{self.value(cc):.{self.decimals}f}'
        return f'{text}{self.unit}' if self.unit else text

    def to_dict(self) -> dict:
        d = {'decimals': self.decimals, 'points': [[cc, v] for cc, v in self.points]}
        if self.unit:
            d['unit'] = self.unit
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'DisplayMap':
        return cls(
            points=tuple((cc, v) for cc, v in d['points']),
            decimals=d.get('decimals', 2),
            unit=d.get('unit', ''),
        )


@dataclass(frozen=True)
class SteppedDisplayMap:
    """Mapping from CC value to one of a fixed set of labels.

    Args:
        steps: (start_cc, label) pairs; each label is shown from its start CC up to the
            next step's start. CC values below the first start show the first label.
    """
    steps: tuple[tuple[int, str], ...]

    def __post_init__(self):
        if not self.steps:
            raise ValueError('SteppedDisplayMap requires at least one step')
        ordered = tuple(sorted((int(cc), str(label)) for cc, label in self.steps))
        ccs = [cc for cc, _ in ordered]
        if len(set(ccs)) != len(ccs):
            raise ValueError(f'SteppedDisplayMap has duplicate CC values: {ccs}')
        if ccs[0] < MIN_CC or ccs[-1] > MAX_CC:
            raise ValueError(f'SteppedDisplayMap CC values must be in range {MIN_CC}..{MAX_CC}, got {ccs}')
        object.__setattr__(self, 'steps', ordered)

    def format(self, cc: int) -> str:
        """Label shown for a CC value."""
        i = bisect_right([start for start, _ in self.steps], cc)
        return self.steps[max(i - 1, 0)][1]

    @classmethod
    def evenly_divided(cls, labels: tuple[str, ...]) -> 'SteppedDisplayMap':
        """Spread labels in equal CC ranges from 0 to 127, the first starting at 0 and the last ending at 127."""
        count = len(labels)
        span = MAX_CC - MIN_CC + 1
        return cls(steps=tuple((MIN_CC + i * span // count, label) for i, label in enumerate(labels)))


type AnyDisplayMap = DisplayMap | SteppedDisplayMap


def load_display_maps(path: Path = DISPLAY_MAPS_PATH) -> dict[str, DisplayMap]:
    """Load all display maps from a JSON file. Returns an empty dict if the file is missing."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {key: DisplayMap.from_dict(entry) for key, entry in data.items()}


def save_display_maps(maps: dict[str, DisplayMap], path: Path = DISPLAY_MAPS_PATH):
    """Write display maps to a JSON file, sorted by key."""
    data = {key: maps[key].to_dict() for key in sorted(maps)}
    path.write_text(json.dumps(data, indent=2) + '\n')


DISPLAY_MAPS: dict[str, DisplayMap] = load_display_maps()

STEPPED_DISPLAY_MAPS: dict[str, SteppedDisplayMap] = {
    key: SteppedDisplayMap.evenly_divided(labels) for key, labels in STEPPED_PARAMS.items()
}

LINEAR_DISPLAY_MAPS: dict[str, DisplayMap] = {
    key: DisplayMap(points=((MIN_CC, lo), (MAX_CC, hi)), decimals=LINEAR_DECIMALS)
    for key, (lo, hi) in LINEAR_PARAMS.items()
}


def get_display_map(key: str | None) -> AnyDisplayMap | None:
    """Look up the display map for a parameter.

    Sampled params use their breakpoints from display_maps.json (None until sampled),
    stepped and linear params use their fixed mappings, and anything else returns None
    (raw CC display).
    """
    if key in SAMPLED_PARAMS:
        return DISPLAY_MAPS.get(key)
    return STEPPED_DISPLAY_MAPS.get(key) or LINEAR_DISPLAY_MAPS.get(key)
