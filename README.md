# Tempera MIDI

A Python library for controlling the Tempera granular sampler. This client supports the entire
specifciation as documented [here](https://docs.beetlecrab.audio/tempera/), including all global settings, track
recording (resampling), setting notes on and off, and all `Emitter` parameters.

There are some nice additional features supporting programmatic composition on the Tempera and particular to its
capabilities and features. In paticular, the `EmitterPool` class provides a convenient way to manage multiple emitters
and their parameters and manipulate all four Emitters concurrently, either in a loop programatically or in response to
external events with the pool running in a separate process.

In addition, two `Sequencer` classes provide either a multi-track sequencer abstraction over the 8 Tempera tracks
or a single-track sequencer abstraction that treats the 64-cell grid of the instrument as a single sequence. These
classes support setting per-cell Emitter placements, setting a tempo in bpm or time units, looping, and modifying
sequence patterns on the fly.

## Software Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. Follow that link for instructions on installing `uv`. After doing so, run this command once to install dependencies and create the correct local environment:

```bash
uv sync
```

## Tempera Setup

You must set the TEMPORA_PORT environment variable and it must match an available MIDI port
The code currently assumes direct USB connection of the Tempera, which will register a MIDI port as 'Tempera'
In Tempera Settings menu, set 'MIDI Settings' to the channel you are sending on (e.g. 1) and toggle Control MIDI Channel In on and set to the same channel

### Notes on Manual Temperal MIDI Setup and MIDI Control

The Tempera supports two kinds of MIDI control:
* Each Emitter has a `Channel` setting which controls what MIDI Channel will send Note On / Off messages which
  are played at the pitch of the Note On / Off by all actively placed cells on the grid for that Emitter
* In `Settings` there is a global `Control MIDI channel` setting with two button toggles, `In` and `Out`. This controls
  the channel for sending and receiving all other MIDI CC messages.

This maps to this library as follows:
* You should create `Emitter` objects with the `midi_channel` set to the `Channel` setting for that Emitter in the Tempera
* You should create a `TemperaGlobal` object with the `midi_channel` set to the `Control MIDI channel` setting in the Tempera

A typical MIDI setup on the device to send both notes and messages from this library to the Tempera might be:
* Emitter 1: Channel 1
* Emitter 2: Channel 2
* Emitter 3: Channel 3
* Emitter 4: Channel 4
* Control MIDI channel: 5
  * In: On

## Running `main.py` to Verify

The project includes an example `main.py` entry point which exercises all of the library functions. So this also
shows usage of all available methods.

Run it and verify that you see activity in the Tempera, and verify the state on the Tempera matches what is set
in the code. At this point your setup is valid and you can modify `main.py` to call the currently empty `play()`
function to do whatever interesting things you want to do.

To run:

```bash
TEMPERA_PORT='Tempera' uv run python -m main
```

## Usage

### Global Controls

```python
from tempera import TemperaGlobal

# NOTE: midi_channel is 1-based, 1-16
# Create instance with default channel (1)
tempera = TemperaGlobal()
# Or specify a MIDI channel (0-15)
# tempera = TemperaGlobal(midi_channel=5)

# Generate MIDI CC bytes for ADSR parameters
messages = tempera.adsr(attack=64, decay=100, sustain=80, release=50)

# See main.py for an example of sending messages to a MIDI port
```

### Emitter Controls

```python
from tempera import Emitter

# NOTE: emitter is 1-based, 1-4
# Create emitter instance (emitter 1-4, channel 0-15)
# You may want to create one object for each of the four emitters and call set_active() on them
# to modify one or another emitter
emitter = Emitter(emitter=1, midi_channel=1)

# Volume and octave
message = emitter.set_active()
# Then send this, see main.py for an example
# Now that the emitter is active, you can modify its parameters and place it in cells
message = emitter.volume(100)
# send ...
message = emitter.effects_send(80)
# send ...

# Cell placement
message = emitter.place_in_cell(column=1, cell=1)
# send ...
message = emitter.remove_from_cell(column=1, cell=1)
# send ...
```

### Track Controls

```python
from tempera import Track

# NOTE: track is 1-based, 1-8
# Create track instance
track = Track(track=1, midi_channel=1)

# Set track volume
message = track.volume(100)
# send ...

# Recording control
message = track.record_on()
# send ...
```

### EmitterPool

The `EmitterPool` class provides a convenient way to manage multiple emitters. It handles
queueing and sending MIDI messages in the background.

The pool launches by default with four emitters, each on its own MIDI channel (1-4).

The pool also provides a `dispatch` method to send messages to any emitter based on a
dictionary event. This makes it easy to send messages from a queue or other async source.

See @main.py for an example of using the pool in code.

```python
from tempera import EmitterPool

async with EmitterPool() as pool:
    await pool.volume(1, 100)
    # wraps emitter methods with additional emmitter_num parameter
    await pool.place_in_cell(2, column=1, cell=1)
```

### Sequencers

The `composition` package provides two sequencer classes for pattern-based composition:

#### GridSequencer

Treats the Tempera's 64 cells as a single continuous sequence:

```python
from tempera import EmitterPool
from sequencer import GridSequencer

async with EmitterPool () as pool:
  sequencer = GridSequencer (pool, bpm=120)

  # Sparse pattern: {step_index: emitter_num}
  # Only include steps that should be ON
  pattern = {0: 1, 4: 2, 8: 1, 12: 2}  # Steps 0,8 use emitter 1; steps 4,12 use emitter 2
  sequencer.set_pattern (pattern)

  await sequencer.run (loops=4)  # Run 4 times
```

#### ColumnSequencer

Treats the grid as 8 independent columns (samples), each with 8 cells:

```python
from tempera import EmitterPool
from sequencer import ColumnSequencer

async with EmitterPool () as pool:
  sequencer = ColumnSequencer (pool, step_duration=0.25)

  # Pattern per column: {cell: emitter_num}
  sequencer.set_column_pattern (1, {1: 1, 3: 1, 5: 1, 7: 1})  # Column 1, odd cells, emitter 1
  sequencer.set_column_pattern (2, {2: 2, 4: 2, 6: 2, 8: 2})  # Column 2, even cells, emitter 2

  # Mute patterns - column 2 plays every other loop
  sequencer.set_mute_pattern (2, [1, 0])

  await sequencer.run (loops=8)
```

Both sequencers support:
- Timing via `bpm` or `step_duration` parameters
- Looping (finite or infinite)
- Pause/resume control
- Event dispatch for external control (server mode)

## Running Tests

Run all tests:
```bash
uv run python -m unittest discover test
```

### Integration Tests

Integration tests use mido to parse and send real MIDI messages. There are two types:

1. **Virtual port tests** - Send to a virtual MIDI port (no hardware required)
2. **Hardware tests** - Send to a connected Tempera device (skipped by default)

#### Virtual Port Tests

These tests verify that the bytes produced by the library are valid MIDI messages that mido can parse and send. They use a virtual MIDI port and don't require any hardware.

```bash
# Run virtual port tests only (default)
uv run python -m unittest discover test

# With verbose output
uv run python -m unittest discover test -v
```

Note: Virtual port tests require virtual MIDI port support (available on macOS and Linux).

#### Hardware Tests

Hardware tests send real MIDI messages to a connected Tempera device. These are skipped by default and must be explicitly enabled via environment variable.

```bash
# Run all integration tests including hardware tests
RUN_HARDWARE_TESTS=1 uv run python -m unittest discover test -v

# With custom Tempera port name
RUN_HARDWARE_TESTS=1 TEMPERA_PORT='My Tempera' uv run python -m unittest discover test -v
```

The hardware tests will auto-detect a MIDI port containing "Tempera" in its name. If your device appears with a different name, use the `TEMPERA_PORT_NAME` environment variable.

To list available MIDI ports on your system:

```bash
uv run python -c "import mido; print(mido.get_output_names())"
```

## Generating Docs

Documentation is auto-generated from docstrings using `pdoc3`, on each commit. To regenerate manually run:
```bash
uv run pdoc3 --force --template templates -o docs tempera midi sequencer
```
