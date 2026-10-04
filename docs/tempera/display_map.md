Module tempera.display_map
==========================
Map MIDI CC values (0-127) to the parameter values Tempera displays.

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

Functions
---------

`get_display_map(key: str | None) ‑> AnyDisplayMap | None`
:   Look up the display map for a parameter.
    
    Sampled params use their breakpoints from display_maps.json (None until sampled),
    stepped and linear params use their fixed mappings, and anything else returns None
    (raw CC display).

`load_display_maps(path: pathlib.Path = PosixPath('/Users/markweiss/iCloud Drive (Archive)/Documents/projects/music/tempera-midi/tempera/display_maps.json')) ‑> dict[str, tempera.display_map.DisplayMap]`
:   Load all display maps from a JSON file. Returns an empty dict if the file is missing.

`save_display_maps(maps: dict[str, tempera.display_map.DisplayMap], path: pathlib.Path = PosixPath('/Users/markweiss/iCloud Drive (Archive)/Documents/projects/music/tempera-midi/tempera/display_maps.json'))`
:   Write display maps to a JSON file, sorted by key.

Classes
-------

`DisplayMap(points: tuple[tuple[int, float], ...], decimals: int = 2, unit: str = '')`
:   Piecewise-linear mapping from CC value to displayed parameter value.
    
    Args:
        points: (cc, value) breakpoints. Need not be sorted; at least one required.
        decimals: Number of decimal places to show when formatting.
        unit: Optional suffix appended when formatting (e.g. 'ms', '%').

### Static methods

`from_dict(d: dict) ‑> tempera.display_map.DisplayMap`
:   

### Instance variables

`decimals: int`
:   The type of the None singleton.

`points: tuple[tuple[int, float], ...]`
:   The type of the None singleton.

`unit: str`
:   The type of the None singleton.

### Methods

`format(self, cc: int) ‑> str`
:   Display string for a CC value.

`to_dict(self) ‑> dict`
:   

`value(self, cc: int) ‑> float`
:   Interpolated display value for a CC value. Clamps outside the sampled range.

---------

`SteppedDisplayMap(steps: tuple[tuple[int, str], ...])`
:   Mapping from CC value to one of a fixed set of labels.
    
    Args:
        steps: (start_cc, label) pairs; each label is shown from its start CC up to the
            next step's start. CC values below the first start show the first label.

### Static methods

`evenly_divided(labels: tuple[str, ...]) ‑> tempera.display_map.SteppedDisplayMap`
:   Spread labels in equal CC ranges from 0 to 127, the first starting at 0 and the last ending at 127.

### Instance variables

`steps: tuple[tuple[int, str], ...]`
:   The type of the None singleton.

### Methods

`format(self, cc: int) ‑> str`
:   Label shown for a CC value.

---------