# Tempera MIDI

## Overview

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

### Connecting Tempera to Computer

> [!IMPORTANT]
> You must connect the Tempera directly to the computer via USB. If you also connect a MIDI TRS Type A or Type B
> cable to the Tempera, this will take precedence and the USB connection will not be recognized.

### Environment Variable for MIDI Port Name

> [!IMPORTANT]
> You must set the `TEMPORA_PORT` environment variable and it must match an available MIDI port
The code currently assumes direct USB connection of the Tempera, which will register a MIDI port as 'Tempera'.

For example, when running the provided `main.py`:

```bash
TEMPERA_PORT='Tempera' uv run python -m main
```

### Tempera MIDI Setup and MIDI Control

Tempera MIDI settings on the device are organized around three concepts:
* Global Settings
* Emitter Settings
* Track Settings

These correspond to three MIDI settings:
* In `Settings` there is a global `Control MIDI channel` setting with two button toggles, `In` and `Out`.  This controls
  the channel for sending and receiving all Track-related and Global MIDI CC messages
* In `Keyboard` there is a `Channel` setting which controls what MIDI Channel will receive Note On / Off messages
* Each Emitter has a `Channel` setting which controls what MIDI Channel will receive Note On / Off messages. When
  playing the Tempera directly, all placed cells on all Emitters sound when any key on the overlay keyboard is pressed.
  In order to have the same behavior via notes triggered by MIDI, you must set the `Channel` for each Emitter to the
  same channel as is set for `Keyboard -> Channel`

With that as background, we recommend you set up the Tempera as follows:

| Menu | Setting | Value | Notes |
|--------------|---------|-------|-------|
| Settings     | Control MIDI channel | `1`, `In` toggled on | Enables receiving `Tempera Global` CC messages |
| Settings     | Record mode | `Replace`, `Cue rec` toggled on | Required for MIDI triggering recording |
| Settings     | Rec threshold | `0.00` | Required for MIDI-triggered recording to complete and close cleanly |
| Settings     | Source | `Instrument` | Supports resampling current playback when controlling note playback via MIDI |
| Keyboard     | Base Note | `C3` | Tempera default, so notes map to MIDI note values as expected |
| Keyboard     | Channel | `2` | |
| Keyboard     | Scale | `Chromatic` | MIDI default |
| Keyboard     | Overlay | `None` | Using MIDI to play notes allows hiding the overlay keyboard and using all 8 tracks for cell placement |
| Emitter      | Channel | `Global`, `All` or `2` | Will receive Emitter settings on any channel (unique CC values per Emitter). Placed cells won't play on Note On unless set to `Global`, `All`, or same channel as Keyboard. Consider `All` to receive Notes on `2` and CC messages on `1` for concurrent thread control. |

With the above setup on the Tempera, the defaults for MIDI channels in `tempera-midi` will work as expected:

| Class           | Channel | Notes                                                                                                          |
|-----------------|---------|----------------------------------------------------------------------------------------------------------------|
| `TemperaGlobal` | 1 | Modifies Global settings via `Control MIDI channel`                                                            | Modifies CC properties for global attributes like modwheel, envelope, effects, etc. |
| `Emitter`       | 2 | Modifies Emitter properties because each Emitter is listening on that channel                                  |
| `Track`         | 1 | Considered Global CC messages by Tempera                                                                       |
| `Midi`          | 2 | Sends `Note On / Off` which plays notes on all placed cells on all Emitters, since they are also listening on 2 |

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

## GUI Control Surface

![tempera-midi GUI](resources/tempera-midi.jpg)

The project includes a full GUI control surface for the Tempera, built with PyQt6 and async MIDI integration. It provides real-time control over every MIDI-controllable parameter on the device, organized in an intuitive layout that eliminates the menu-diving required when adjusting settings directly on the hardware.

To launch:

```bash
TEMPERA_PORT='Tempera' uv run python -m gui
```

### Layout Overview

The interface is divided into four main sections, all visible at once:

- **Cell Grid + Transport** (upper left): An interactive 8x8 grid representing the Tempera's 64 cells, with transport controls for playback, sequencer selection, and BPM
- **Emitter Panel** (upper right): All parameters for the currently selected emitter, organized into subsections (Basic, Tone Filter, Position/Spray, Grain)
- **Track Panel** (lower left): A mixer-style view of all 8 tracks with vertical volume faders and per-track record buttons
- **Global Panel** (lower right): ADSR envelope, effects (Reverb, Delay, Filter, Chorus), and Modulator controls in a tabbed layout
- **Envelope Panel** (top, full width): An automation envelope editor for applying envelopes to any parameter

### Emitter Controls

Four color-coded emitter buttons (1-4) let you switch between emitters instantly. Each emitter exposes all 16 of its parameters as sliders grouped into four subsections: Basic (Volume, Octave, Effects Send), Tone Filter (Width, Center), Position/Spray (Position X/Y, Spray X/Y), and Grain (Length Cell, Length Note, Density, Shape, Shape Attack, Pan, Tune Spread).

### Track Mixer

The 8 track volume sliders are arranged horizontally in a mixer-style layout, each with a value readout and track number label. A **Lock** button links all 8 faders together, so moving any one slider sets all tracks to the same value — functioning as a master volume fader. Each track also has a circular **Record** button that triggers resampled recording on that track via MIDI.

### Global Effects

All global parameters are accessible without navigating submenus: ADSR envelope (Attack, Decay, Sustain, Release), Reverb (Size, Color, Mix), Delay (Feedback, Time, Color, Mix), Filter (Cutoff, Resonance), Chorus (Depth, Speed, Flange, Mix), and Modulator controls (select any of 10 modulators and adjust its size). Effects are organized in tabs for quick switching.

### Cell Grid

The 8x8 grid displays the current state of all 64 cells, color-coded by emitter. Left-click to place the active emitter in a cell, right-click to clear it. The grid adapts to the current mode — in hardware mode it sends placements directly to the Tempera, and in sequencer modes it edits the active sequencer pattern. Keyboard navigation provides a pulsing cursor that can be moved with arrow keys or WASD, with Space to toggle cells.

### Sequencer Modes

Two sequencer modes provide compositional functionality not available on the hardware device:

- **8-Track Sequencer** (Column Sequencer): Treats the grid as 8 independent tracks, each with an 8-step pattern. Each column runs its own pattern simultaneously, with per-column mute control
- **1-Track Sequencer** (Grid Sequencer): Treats all 64 cells as a single continuous 64-step sequence, cycling through the entire grid in column-major order

Both sequencers support adjustable BPM (20-300), looping, real-time pattern editing during playback, and integration with the envelope automation system. Toggle between modes using the transport panel buttons, or disable both to return to direct hardware control.

### Envelope Automation

Any MIDI-controllable parameter on the UI can have an automation envelope applied to it. The envelope panel at the top of the window provides:

- **Freehand drawing**: Click and drag on the canvas to draw a custom envelope shape
- **7 preset shapes**: Ramp Up, Ramp Down, Triangle, Triangle Down, Square, Square Up, and Rounded
- **Per-Cell mode**: The envelope pattern repeats once per step (8 repetitions per cycle), applying modulation independently to each step in the sequence
- **Over-All mode**: The envelope spans the entire 8-step cycle, applying a single continuous modulation arc across all steps

Envelopes modulate the base parameter value — for example, if a volume slider is set to 100 and the envelope value at the current position is 0.5, the output is 50. A playhead shows the current position during sequencer playback. Envelopes can be enabled, disabled, and cleared independently per parameter.

### Save and Load

All UI state can be saved and loaded as a named canvas (Ctrl+S / Ctrl+O). A saved canvas captures every MIDI-controllable parameter value (all emitter, track, and global settings), all cell placements, all sequencer patterns, all envelope configurations, and the current grid mode. Canvases are stored as JSON files in a platform-appropriate location (`~/.config/tempera-edit/canvases/` on macOS/Linux).

### Keyboard Shortcuts and Mouse Support

The GUI supports full keyboard navigation with two one-handed layouts:

- **Left-hand (WASD)**: W/S to navigate, A/D to adjust values, Shift+A/D for large steps, F to toggle focus depth, Q/E/T/G to jump to Grid/Emitter/Tracks/Global
- **Right-hand (Arrows)**: Up/Down to navigate, Left/Right to adjust values, Shift+Left/Right for large steps, Return to toggle focus

Shared shortcuts include 1-4 for emitter selection, Escape to stop the sequencer, Ctrl+Z / Ctrl+Shift+Z for undo/redo, R to toggle envelope automation on the focused control, and F1 or ? to show keyboard hint overlays. All controls also respond to mouse interaction — clicking any slider or control focuses it for keyboard adjustment, and sliders can be dragged directly.

### Undo / Redo

Parameter changes are tracked with a 50-level undo history. Ctrl+Z undoes the last change and syncs the full state back to the hardware; Ctrl+Shift+Z redoes. Slider drags are coalesced into a single undo entry on release.

## Code Usage

### Global Controls

```python
import mido
from tempera import TemperaGlobal

with mido.open_output('Tempera') as output:
  # NOTE: midi_channel is 1-based, 1-16
    # Create instance with default channel (1)
    tempera = TemperaGlobal()
    # Or specify a MIDI channel (0-15)
    # tempera = TemperaGlobal(midi_channel=5)

    # Generate MIDI CC bytes for ADSR parameters
    messages = tempera.adsr(attack=64, decay=100, sustain=80, release=50)
    for message in messages:
        output.send(message)

    # See main.py for an example of sending messages to a MIDI port
```

### Emitter Controls

```python
import asyncio
import mido
from tempera import Emitter

async def main():
    # NOTE: emitter is 1-based, 1-4
    # Create emitter instance (emitter 1-4, channel 0-15)
    # You may want to create one object for each of the four emitters and call set_active() on them
    # to modify one or another emitter
    # Can also put each emitter on its own MIDI channel to selectively send notes to a particular emitter
    emitter = Emitter(emitter=1, midi_channel=3)

    # Then send this, see main.py for an example
    # Now that the emitter is active, you can modify its parameters and place it in cells
    with mido.open_output('Tempera') as output:
        # Volume and octave
        message = emitter.set_active()
        output.send(message)
        message = emitter.volume (100)
        output.send(message)
        message = emitter.effects_send (80)
        output.send(message)

        # Cell placement and playback
        # Can play notes via the Emitter's Midi attribute, which is set to the channel passed when creating the Emitter
        # So, if each Emitter is on its own channel, playing back through the Emitter only plays that note on cells
        #  that Emitter is placed in
        # 50 == C3, default base note of the Tempera Keyboard, so this plays all placed cells with no pitch shift, at max volume
        message = emitter.place_in_cell(column=1, cell=1)
        output.send(message)
        output.send(emitter.midi.note_on(60, 127, 0))
        await asyncio.sleep (2)
        output.send(emitter.midi.note_off(0, 0, 0))
          
        # Or just call emitter.play(), which will play C3 at max volume for the duration passed in, on this emitter's
        # MIDI channel. Useful when you are only sending the Note to trigger playback of the cells placed by the Emitter
        await emitter.play(output=output, duration=2)
        message = emitter.remove_from_cell(column=1, cell=1)
        output.send(message)
```

### Track Controls

```python
import mido
from tempera import Track

async def main():
    with mido.open_output('Tempera') as output:
        # NOTE: track is 1-based, 1-8
        # Create track instance
        track = Track(track=1, midi_channel=1)

        # Set track volume
        message = track.volume(100)
        output.send(message)

        # Recording control
        message = track.record_on()
        output.send(message)
```

### EmitterPool

The `EmitterPool` class provides a convenient way to manage multiple emitters. It handles queueing and sending MIDI
messages in the background.

The pool launches by default with four emitters mapping to the four Emitters on the Tempera. By default all are
set to MIDI Channel 2, per the discussion above in
[Tempera MIDI Setup and MIDI Control](#tempera-midi-setup-and-midi-control). The `play_all()` method in this case
simply sends one `Note On` message on Channel 2. You can override this behavior by creating the pool with
`emitters_on_own_channels=True`, in which case each Emitter will be assigned to its own MIDI channel (2-5) and
`play_all()` will send a `Note On` message to each channel. 

The pool also provides a `dispatch` method to send messages to any emitter based on a
dictionary event. This makes it easy to send messages from a queue or other async source.

See `main.py` for examples of using the pool in code.

```python
import mido
from tempera import EmitterPool

async def main():
    with mido.open_output('Tempera') as output:
        async with EmitterPool() as pool:
            await pool.volume(1, 100)
            # wraps emitter methods with additional emmitter_num parameter
            await pool.place_in_cell(2, column=1, cell=1)
```

### Sequencers

The `sequencer` package provides two sequencer classes for pattern-based composition.

#### GridSequencer

Treats the Tempera's 64 cells as a single continuous sequence:

```python
from tempera import EmitterPool
from sequencer import GridSequencer

async def main():
    async with EmitterPool() as pool:
      sequencer = GridSequencer(pool, bpm=120)

      # Sparse pattern: {step_index: emitter_num}
      # Only include steps that should be ON
      pattern = {0: 1, 4: 2, 8: 1, 12: 2}  # Steps 0,8 use emitter 1; steps 4,12 use emitter 2
      sequencer.set_pattern(pattern)

      await sequencer.run(loops=4)  # Run 4 times
```

#### ColumnSequencer

Treats the grid as 8 independent columns (samples), each with 8 cells:

```python
from tempera import EmitterPool
from sequencer import ColumnSequencer


async def main():
    async with EmitterPool () as pool:
        sequencer = ColumnSequencer (pool, step_duration=0.25)

        # Pattern per column: {cell: emitter_num}
        # Sparse format, only pass in pairs for cells which you want to place an Emitter into
        sequencer.set_column_pattern(1, {1: 1, 3: 1, 5: 1, 7: 1})  # Column 1, odd cells, emitter 1
        sequencer.set_column_pattern(2, {2: 2, 4: 2, 6: 2, 8: 2})  # Column 2, even cells, emitter 2

        # Mute patterns - column 2 plays every other loop
        sequencer.set_column_mute_pattern(2, [1, 0])

        await sequencer.run(loops=8)
```

Both sequencers support:
- Timing via `bpm` or `step_duration` parameters
- Looping (finite or infinite)
- Pause/resume control
- Event dispatch for external control (server mode)

---

## For Conributors

### Running Tests

Run all tests:
```bash
uv run python -m unittest discover test
```

Run GUI tests only:
```bash
QT_QPA_PLATFORM=offscreen uv run python -m unittest discover test/gui_tests -v
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
RUN_HARDWARE_TESTS=1 TEMPERA_PORT='Tempera' uv run python -m unittest discover test -v
```

The hardware tests will auto-detect a MIDI port containing "Tempera" in its name.
If your device appears with a different name, use the `TEMPERA_PORT_NAME` environment variable.

To list available MIDI ports on your system:

```bash
uv run python -c "import mido; print(mido.get_output_names())"
```

### Generating Docs

Documentation is auto-generated from docstrings using `pdoc3`, on each commit. To regenerate manually run:
```bash
uv run pdoc3 --force --template templates -o docs tempera midi sequencer
```