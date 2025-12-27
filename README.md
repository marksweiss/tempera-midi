# Tempera MIDI

A Python library for generating MIDI CC messages for the Tempera granular synthesizer.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
uv sync
```

## Usage

```python
from tempera_global import TemperaGlobal

# Create instance with default channel (1)
tempera = TemperaGlobal ()

# Or specify a MIDI channel (0-15)
tempera = TemperaGlobal (channel=5)

# Generate MIDI CC bytes for ADSR parameters
midi_bytes = tempera.adsr (attack=64, decay=100, sustain=80, release=50)

# Generate MIDI CC bytes for reverb
midi_bytes = tempera.reverb (size=100, mix=64)

# Generate MIDI CC bytes for emitter 1
midi_bytes = tempera.emitter_1 (volume=100, grain_density=50, octave=64)
```

## Running Tests

Run all tests:

```bash
uv run python -m unittest test_tempera
```

Run tests with verbose output:

```bash
uv run python -m unittest test_tempera -v
```

Run a specific test:

```bash
uv run python -m unittest test_tempera.TestTempera.test_adsr_attack
```