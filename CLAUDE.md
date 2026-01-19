# Tempera MIDI - Developer Reference

## Project Overview

A Python library for controlling the Tempera granular sampler via MIDI. Implements wrapper methods around the [Tempera MIDI specification](https://docs.beetlecrab.audio/tempera/midi.html#midi-input), providing an object model for Emitters, Tracks, Global state, and two Sequencer types for pattern-based composition.

## Core Concepts

### Tempera Hardware Model
- **Grid**: 64 cells arranged as 8 columns (tracks) x 8 cells
- **Tracks (Columns)**: Each of 8 tracks plays equal-length segments of an audio file loaded into it, split across its 8 cells
- **Cells**: Activating a cell plays that portion of the track's audio file
- **Emitters (1-4)**: Control playback parameters. Each cell is either inactive or activated for one of four Emitters at any time
- **MIDI Channels**: Default setup uses Channel 1 for Global/Track CC messages, Channel 2 for Emitter settings and Note On/Off

### MIDI CC Number Mapping
See `tempera/constants.py` for the complete CC mapping. Key ranges:
- CC 1: Modwheel
- CC 10-12: Emitter selection and cell placement
- CC 13-29: Global effects (ADSR, Reverb, Delay, Chorus)
- CC 30-39: Track volumes (note: CC 32, 38 unused)
- CC 40-55: Emitter 1 parameters
- CC 56-75: Emitter 2 parameters (note: CC 64=Damper pedal, some gaps)
- CC 76-91: Emitter 3 parameters
- CC 92-109: Emitter 4 parameters
- CC 110-119: Modulator sizes

## Project Structure

```
tempera-midi/
├── tempera/              # Core Tempera control classes
│   ├── __init__.py       # Lazy imports to avoid circular deps
│   ├── constants.py      # MIDI CC number definitions
│   ├── emitter.py        # Emitter class - per-emitter control
│   ├── emitter_pool.py   # EmitterPool - async multi-emitter management
│   ├── tempera_global.py # TemperaGlobal - global settings
│   └── track.py          # Track class - per-track control
├── sequencer/            # Pattern sequencing
│   ├── __init__.py
│   └── sequencer.py      # BaseSequencer, GridSequencer, ColumnSequencer
├── midi/                 # Low-level MIDI message generation
│   ├── __init__.py
│   └── midi.py           # Midi class - generates mido Messages
├── test/                 # Unit and integration tests
├── docs/                 # Auto-generated API docs (pdoc3)
├── main.py               # Entry point with integration tests
└── pyproject.toml        # Project config (uv)
```

## Key Classes

### `Midi` (midi/midi.py)
Low-level MIDI message factory using mido. Generates Note On/Off, CC, Program Change, Clock/Start/Stop messages.

### `Emitter` (tempera/emitter.py)
Controls a single Tempera emitter (1-4). Methods:
- `set_active()` - Make this the active emitter
- `place_in_cell(column, cell)` / `remove_from_cell(column, cell)` - Cell placement
- `volume()`, `octave()`, `effects_send()` - Single-value parameters
- `grain(length_cell, length_note, density, shape, shape_attack, pan, tune_spread)` - Granular params
- `relative_position(x, y)`, `spray(x, y)`, `tone_filter(width, center)` - Position/filter params

Each Emitter has its own `Midi` instance and CC map (EMITTER_1_CC_MAP, etc.).

### `EmitterPool` (tempera/emitter_pool.py)
Async context manager for controlling all 4 emitters with queue-based message dispatch. Key features:
- Background sender task with asyncio Queue
- All Emitter methods available with added `emitter_num` parameter
- `play(emitter_num, note, velocity, duration)` - Play on single emitter
- `play_all(emitter_nums, ...)` - Play on multiple emitters concurrently
- `dispatch(event)` - Generic event dispatch from dict
- `emitters_on_own_channels` option for per-emitter MIDI channels (2-5)

### `Track` (tempera/track.py)
Controls a single Tempera track (column 1-8). Methods:
- `volume(value)` - Track volume
- `record_on()` - Arm track for recording via note 100-107

### `TemperaGlobal` (tempera/tempera_global.py)
Global Tempera controls:
- `modwheel(value)`
- `adsr(attack, decay, sustain, release)` - Envelope
- `reverb(size, color, mix)`, `delay(feedback, time, color, mix)`, `chorus(depth, speed, flange, mix)` - Effects
- `change_canvas(program)` - Switch canvas via Program Change
- `clock()`, `start()`, `stop()` - MIDI transport (static methods)

### Sequencers (sequencer/sequencer.py)

**`BaseSequencer`** (abstract): Common timing, looping, pause/resume control. Timing via `bpm` or `step_duration`.

**`GridSequencer`**: Treats all 64 cells as one continuous sequence.
- Pattern format: `{step_index: emitter_num}` where step_index 0-63 (column-major)
- `set_pattern(pattern)`, `clear()`, `cleanup()`
- Dispatch actions: set_pattern, clear, cleanup, set_loops, pause, resume, stop

**`ColumnSequencer`**: Treats grid as 8 independent 8-step columns.
- Pattern per column: `{cell: emitter_num}` where cell 1-8
- `set_column_pattern(column, pattern)`, `clear_column(column)`, `cleanup()`
- `mute_column()`, `unmute_column()`, `set_column_mute_pattern(column, pattern)`
- Dispatch actions: set_column_pattern, clear_column, cleanup, mute_column, unmute_column, set_mute_pattern, set_loops, pause, resume, stop

## Development Commands

```bash
# Install dependencies
uv sync

# Run integration tests (connected to Tempera)
TEMPERA_PORT='Tempera' uv run python -m main

# Run unit tests
uv run python -m unittest discover test

# Run hardware integration tests
RUN_HARDWARE_TESTS=1 TEMPERA_PORT='Tempera' uv run python -m unittest discover test -v

# List available MIDI ports
uv run python -c "import mido; print(mido.get_output_names())"

# Generate docs
uv run pdoc3 --force --template templates -o docs tempera midi sequencer
```

## Important Implementation Details

1. **1-based vs 0-based indexing**: User-facing APIs use 1-based (emitter 1-4, column 1-8, cell 1-8, channel 1-16). Internally converted to 0-based for MIDI.

2. **MIDI Channel handling**: mido uses 0-15, this library uses 1-16 in public APIs and converts with `channel - 1`.

3. **Circular import avoidance**: `tempera/__init__.py` uses `__getattr__` for lazy imports.

4. **Cell index calculation**: For 64-cell grid, `value = ((column - 1) * 8) + (cell - 1)` converts to 0-63 range.

5. **CC value non-linearity**: MIDI CC 0-127 does not map linearly to Tempera parameter ranges. See `docs/midi_to_tempera_cc_ranges.md` for documented mappings (incomplete).

6. **EmitterPool modes**: By default all emitters on Channel 2 (single note_on triggers all). With `emitters_on_own_channels=True`, each gets own channel (2-5) for independent note control.

7. **Sequencer note timing**: Notes play for `step_duration * 0.999` to avoid overlap, with 0.001 gap.

## Common Patterns

### Basic Emitter Control
```python
import mido
from tempera import Emitter

with mido.open_output('Tempera') as output:
    emitter = Emitter(emitter=1, midi_channel=2)
    output.send(emitter.set_active())
    output.send(emitter.volume(100))
    output.send(emitter.place_in_cell(column=1, cell=1))
    output.send(emitter.midi.note_on(60, 127, 0))
    # ... play ...
    output.send(emitter.midi.note_off(60, 0))
```

### EmitterPool Usage
```python
from tempera import EmitterPool

async with EmitterPool() as pool:
    await pool.volume(1, 100)
    await pool.place_in_cell(1, column=1, cell=1)
    await pool.play_all([1, 2, 3, 4], note=60, velocity=127, duration=1.0)
```

### Sequencer Usage
```python
from tempera import EmitterPool
from sequencer import ColumnSequencer

async with EmitterPool() as pool:
    seq = ColumnSequencer(pool, bpm=120)
    await seq.set_column_pattern(1, {1: 1, 5: 1})
    await seq.run(loops=4)
    await seq.cleanup()
```

## Environment Variables

- `TEMPERA_PORT`: MIDI port name for Tempera device (default: 'Tempera')
- `RUN_HARDWARE_TESTS`: Set to `1` to run hardware integration tests

## Dependencies

- `mido[ports-rtmidi]`: MIDI message handling and port I/O
- `pdoc3`: Documentation generation
- Python 3.12+