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
tempera = TemperaGlobal()

# Or specify a MIDI channel (0-15)
tempera = TemperaGlobal(channel=5)

# Generate MIDI CC bytes for ADSR parameters
midi_bytes = tempera.adsr(attack=64, decay=100, sustain=80, release=50)

# Generate MIDI CC bytes for effects
midi_bytes = tempera.reverb(size=100, color=64, mix=80)
midi_bytes = tempera.delay(feedback=50, time=64, color=100, mix=60)
midi_bytes = tempera.chorus(depth=64, speed=50, flange=30, mix=70)

# Modwheel and canvas control
midi_bytes = tempera.modwheel(modwheel=64)
midi_bytes = tempera.change_canvas(program=3)

# MIDI clock messages
midi_bytes = TemperaGlobal.clock()
midi_bytes = TemperaGlobal.start()
midi_bytes = TemperaGlobal.stop()
```

### Emitter Controls

```python
from emitter import Emitter

# Create emitter instance (emitter 1-4, channel 0-15)
emitter = Emitter(emitter=1, channel=1)

# Volume and octave
midi_bytes = emitter.volume(100)
midi_bytes = emitter.octave(64)

# Grain parameters
midi_bytes = emitter.grain(density=50, length_cell=64, shape=80)

# Position and spray
midi_bytes = emitter.relative_position(x=64, y=64)
midi_bytes = emitter.spray(x=30, y=30)

# Tone filter and effects
midi_bytes = emitter.tone_filter(width=64, center=64)
midi_bytes = emitter.effects_send(80)

# Cell placement
midi_bytes = emitter.set_active()
midi_bytes = emitter.place_in_cell(column=1, cell=1)
midi_bytes = emitter.remove_from_cell(column=1, cell=1)
```

### Track Controls

```python
from track import Track

# Create track instance (track 1-8, channel 0-15)
track = Track(track=1, channel=1)

# Set track volume
midi_bytes = track.volume(100)

# Recording control
midi_bytes = track.record_on()
midi_bytes = track.record_off()
```

## Running Tests

Run all tests:

```bash
uv run python -m unittest discover test
```

Run tests with verbose output:

```bash
uv run python -m unittest discover test -v
```

Run a specific test:

```bash
uv run python -m unittest test.test_tempera_global.TestTemperaGlobal.test_adsr_attack
```