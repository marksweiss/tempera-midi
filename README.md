# Tempera MIDI

A Python library for generating MIDI CC messages for the Tempera granular synthesizer.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
uv sync
```

## Usage

### Global Controls

```python
from tempera_global import TemperaGlobal

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
from emitter import Emitter

# NOTE: emitter is 1-based, 1-4
# Create emitter instance (emitter 1-4, channel 0-15)
# You may want to create one object for each of the four emitters and call set_active() on them
# to modify one or another emitter
emitter = Emitter (emitter=1, midi_channel=1)

# Volume and octave
message = emitter.set_active()
# Then send this, see main.py for an example
# Now that the emitter is active, you can modify its parameters and place it in cells
message = emitter.volume(100)
# send ...
message = emitter.effects_send(80)
# send ...

# Cell placement
message = emitter.place_in_cell (column=1, cell=1)
# send ...
message = emitter.remove_from_cell (column=1, cell=1)
# send ...
```

### Track Controls

```python
from track import Track

# NOTE: track is 1-based, 1-8
# Create track instance
track = Track (track=1, midi_channel=1)

# Set track volume
message = track.volume(100)
# send ...

# Recording control
message = track.record_on ()
# send ...
```

## Running Tests

### Integration Tests

Integration tests use mido to parse and send real MIDI messages. There are two types:

1. **Virtual port tests** - Send to a virtual MIDI port (no hardware required)
2. **Hardware tests** - Send to a connected Tempera device (skipped by default)

#### Virtual Port Tests

These tests verify that the bytes produced by the library are valid MIDI messages that mido can parse and send. They use a virtual MIDI port and don't require any hardware.

```bash
# Run virtual port tests only (default)
uv run python -m unittest discover integration_test

# With verbose output
uv run python -m unittest discover integration_test -v
```

Note: Virtual port tests require virtual MIDI port support (available on macOS and Linux).

#### Hardware Tests

Hardware tests send real MIDI messages to a connected Tempera device. These are skipped by default and must be explicitly enabled via environment variable.

```bash
# Run all integration tests including hardware tests
RUN_HARDWARE_TESTS=1 uv run python -m unittest discover integration_test -v

# With custom Tempera port name
RUN_HARDWARE_TESTS=1 TEMPERA_PORT='My Tempera' uv run python -m unittest discover integration_test -v
```

The hardware tests will auto-detect a MIDI port containing "Tempera" in its name. If your device appears with a different name, use the `TEMPERA_PORT_NAME` environment variable.

To list available MIDI ports on your system:

```bash
uv run python -c "import mido; print(mido.get_output_names())"
```

## Generating Docs

Documentation is auto-generated from docstrings using pdoc. To regenerate:

```bash
uv run pdoc ./*.py -o docs/
```

Docs are also regenerated automatically by the pre-commit hook.

## Running main.py

```bash
# You must set the TEMPORA_PORT environment variable and it must match an available MIDI port
# The code currently assumes a virtual port
TEMPERA_PORT='My Tempera' uv run python -m main
```