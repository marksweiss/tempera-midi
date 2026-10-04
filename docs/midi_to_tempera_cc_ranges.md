# MIDI CC Ranges for Tempera

Tempera does not map incoming CC values 0-127 linearly onto every parameter's range. This page records how the
emitter parameters display on the device (firmware 2.3) for each CC value. Tempera does not transmit CC values, so
the sampled values were read off the device screen.

The source of truth is `tempera/display_maps.json` (sampled parameters) and `tempera/display_map.py` (parameter
kinds, linear ranges and stepped labels). The GUI uses them to show each slider's value as Tempera displays it.
To add or refine samples, run:

```bash
TEMPERA_PORT='Tempera' uv run python -m tools.sample_cc <param>   # --list shows params and sample counts
```

Tempera's MIDI channel setting must be **All** (or 2) for emitter CCs to be received. CC numbers are for Emitter 1;
Emitters 2-4 use their own CCs (see `tempera/constants.py`) with the same curves.

## Linear parameters (no sampling needed)

These scale linearly from CC 0 to CC 127 over the range shown.

| Parameter | CC | Range |
|-----------|----|-------|
| Grain shape | 44 | 0.0 - 1.0 |
| Grain shape Attack | 45 | 0.0 - 1.0 |
| Grain pan | 46 | 0.0 - 1.0 |
| Grain tune spread | 47 | 0.0 - 1.0 |
| Tone filter Width | 53 | 0.0 - 1.0 |
| Tone filter Center | 54 | 0.0 - 1.0 |
| Effects send | 55 | 0.0 - 1.0 |

## Stepped parameters (no sampling needed)

Grain length Note steps through tempo ratios, assumed to be evenly spaced across CC 0-127 (each step is 6 or 7 CC
values wide), matching the even spacing observed when turning the knob on the device.

**Grain length Note** (CC 42)

| CC range | Display |
|----------|---------|
| 0-5 | 16/1 |
| 6-11 | 8/1 |
| 12-18 | 4/1 |
| 19-24 | 2/1 |
| 25-31 | 1/1 |
| 32-37 | 1/2 |
| 38-43 | 1/3 |
| 44-50 | 1/4 |
| 51-56 | 1/5 |
| 57-63 | 1/6 |
| 64-69 | 1/7 |
| 70-75 | 1/8 |
| 76-82 | 1/9 |
| 83-88 | 1/10 |
| 89-95 | 1/11 |
| 96-101 | 1/12 |
| 102-107 | 1/16 |
| 108-114 | 1/24 |
| 115-120 | 1/32 |
| 121-127 | 1/64 |

## Sampled parameters (non-linear)

Values between sampled CC values are linearly interpolated. Observations:

- **Grain length Cell** is linear at 1/72 per CC (CC/72) from 0 to 1.0 at CC 72, then rises 1.0 every 8 CC to 8.0.
- **Grain density** roughly doubles every 16 CC in the lower half and climbs steeply above CC 64.
- **Relative X/Y** run from -8.0 to 7.88, centered at 0.0 on CC 64, 1.0 per 8 CC.
- **Spray X/Y** run from 0.0 to 7.94, 0.5 per 8 CC.

| CC | Grain density (43) | Grain length Cell (41) | Relative X (49) | Relative Y (50) | Spray X (51) | Spray Y (52) |
|----|--------------------|------------------------|-----------------|-----------------|--------------|--------------|
| 0 | 0.01 | 0.0000 | -8.00 | -8.00 | 0.00 | 0.00 |
| 8 | 0.25 | 0.1111 | -7.00 | -7.00 | 0.50 | 0.50 |
| 16 | 0.50 | 0.2222 | -6.00 | -6.00 | 1.00 | 1.00 |
| 24 | 0.75 | 0.3333 | -5.00 | -5.00 | 1.50 | 1.50 |
| 32 | 1.00 | 0.4444 | -4.00 | -4.00 | 2.00 | 2.00 |
| 40 | 1.50 | 0.5556 | -3.00 | -3.00 | 2.50 | 2.50 |
| 48 | 2.00 | 0.6667 | -2.00 | -2.00 | 3.00 | 3.00 |
| 56 | 3.00 | 0.7778 | -1.00 | -1.00 | 3.50 | 3.50 |
| 64 | 6.00 | 0.8889 | 0.00 | 0.00 | 4.00 | 4.00 |
| 72 | 10.00 | 1.0000 | 1.00 | 1.00 | 4.50 | 4.50 |
| 80 | 18.00 | 2.0000 | 2.00 | 2.00 | 5.00 | 5.00 |
| 88 | 26.00 | 3.0000 | 3.00 | 3.00 | 5.50 | 5.50 |
| 96 | 34.00 | 4.0000 | 4.00 | 4.00 | 6.00 | 6.00 |
| 104 | 44.00 | 5.0000 | 5.00 | 5.00 | 6.50 | 6.50 |
| 112 | 60.00 | 6.0000 | 6.00 | 6.00 | 7.00 | 7.00 |
| 120 | 76.00 | 7.0000 | 7.00 | 7.00 | 7.50 | 7.50 |
| 127 | 100.00 | 8.0000 | 7.88 | 7.88 | 7.94 | 7.94 |
