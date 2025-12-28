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

# Create instance with default channel (1)
tempera = TemperaGlobal ()

# Or specify a MIDI channel (0-15)
tempera = TemperaGlobal (midi_channel=5)

# Generate MIDI CC bytes for ADSR parameters
midi_bytes = tempera.adsr (attack=64, decay=100, sustain=80, release=50)

# Generate MIDI CC bytes for effects
midi_bytes = tempera.reverb (size=100, color=64, mix=80)
midi_bytes = tempera.delay (feedback=50, time=64, color=100, mix=60)
midi_bytes = tempera.chorus (depth=64, speed=50, flange=30, mix=70)

# Modwheel and canvas control
midi_bytes = tempera.modwheel (modwheel=64)
midi_bytes = tempera.change_canvas (program=3)

# MIDI clock messages
midi_bytes = TemperaGlobal.clock ()
midi_bytes = TemperaGlobal.start ()
midi_bytes = TemperaGlobal.stop ()
```

### Emitter Controls

```python
from emitter import Emitter

# Create emitter instance (emitter 1-4, channel 0-15)
emitter = Emitter (emitter=1, midi_channel=1)

# Volume and octave
midi_bytes = emitter.volume (100)
midi_bytes = emitter.octave (64)

# Grain parameters
midi_bytes = emitter.grain (density=50, length_cell=64, shape=80)

# Position and spray
midi_bytes = emitter.relative_position (x=64, y=64)
midi_bytes = emitter.spray (x=30, y=30)

# Tone filter and effects
midi_bytes = emitter.tone_filter (width=64, center=64)
midi_bytes = emitter.effects_send (80)

# Cell placement
midi_bytes = emitter.set_active ()
midi_bytes = emitter.place_in_cell (column=1, cell=1)
midi_bytes = emitter.remove_from_cell (column=1, cell=1)
```

### Track Controls

```python
from track import Track

# Create track instance (track 1-8, channel 0-15)
track = Track (track=1, midi_channel=1)

# Set track volume
midi_bytes = track.volume (100)

# Recording control
midi_bytes = track.record_on ()
midi_bytes = track.record_off ()
```

## Running Tests

### Unit Tests

Run all unit tests:

```bash
uv run python -m unittest discover test
```

Run unit tests with verbose output:

```bash
uv run python -m unittest discover test -v
```

Run a specific unit test:

```bash
uv run python -m unittest test.test_tempera_global.TestTemperaGlobal.test_adsr_attack
```

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
RUN_HARDWARE_TESTS=1 TEMPERA_PORT_NAME="My Tempera" uv run python -m unittest discover integration_test -v
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