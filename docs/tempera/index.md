Module tempera
==============
Tempera MIDI control library.

Sub-modules
-----------
* tempera.constants
* tempera.emitter
* tempera.emitter_pool
* tempera.tempera_global
* tempera.track

Classes
-------

`Emitter(emitter: int = 1, midi_channel: int = 2)`
:   Controls for an individual Tempera emitter.
    
    Args:
        emitter: Emitter number (1-4).
        midi_channel: MIDI channel (1-16). Default is 1.

### Instance variables

`emitter_num`
:   

### Methods

`effects_send(self, value: int) ‑> mido.messages.messages.Message`
:   Change Emitter Effects Send.

`grain(self, *, length_cell: int = None, length_note: int = None, density: int = None, shape: int = None, shape_attack: int = None, pan: int = None, tune_spread: int = None) ‑> list[mido.messages.messages.Message]`
:   Change Emitter Grain Parameters.

`octave(self, value: int) ‑> mido.messages.messages.Message`
:   Change Emitter Octave.

`place_in_cell(self, column: int, cell: int) ‑> mido.messages.messages.Message`
:   Place Emitter in a given Cell in a given Column.

`relative_position(self, *, x: int = None, y: int = None) ‑> list[mido.messages.messages.Message]`
:   Change Emitter Position along X and Y axes. Applies to a placement for the Emitter in a given Cell.

`remove_from_cell(self, column: int, cell: int) ‑> mido.messages.messages.Message`
:   Remove Emitter placement in a given Cell in a given Column.

`set_active(self) ‑> mido.messages.messages.Message`
:   Set Emitter as Active.

`spray(self, *, x: int = None, y: int = None) ‑> list[mido.messages.messages.Message]`
:   Change Emitter Spray along X and Y axes. Applies to a placement for the Emitter in a given Cell.

`tone_filter(self, *, width: int = None, center: int = None) ‑> list[mido.messages.messages.Message]`
:   Change Emitter Filter width and center.

`volume(self, value: int) ‑> mido.messages.messages.Message`
:   Change Emitter Volume.

---------

`EmitterPool(port_name: str = None, virtual: bool = False, emitters_on_own_channels: bool = False)`
:   Async pool managing four Tempera emitters with queue-based message dispatch.
    
    Each emitter is assigned to its corresponding MIDI channel (emitter 1 → channel 1, etc.).
    All methods enqueue messages to a background sender task for ordered, non-blocking delivery.
    
    Usage:
        async with EmitterPool() as pool:
            await pool.volume(1, 100)
            await pool.place_in_cell(2, column=1, cell=1)
    
    Args:
        port_name: MIDI port name. Defaults to TEMPERA_PORT environment variable.
        virtual: If True, create a virtual MIDI port (for testing). Defaults to False.

### Methods

`dispatch(self, event: dict)`
:   Dispatch an event to the appropriate emitter method.
    
    Args:
        event: Dictionary with keys:
            - emitter: Emitter number (1-4)
            - method: Method name (e.g., 'volume', 'grain', 'place_in_cell')
            - args: Optional list of positional arguments
            - kwargs: Optional dict of keyword arguments
    
    Example:
        await pool.dispatch({'emitter': 1, 'method': 'volume', 'args': [64]})
        await pool.dispatch({'emitter': 2, 'method': 'grain', 'kwargs': {'density': 80}})

`effects_send(self, emitter_num: int, value: int)`
:   Change Emitter Effects Send.

`grain(self, emitter_num: int, *, length_cell: int = None, length_note: int = None, density: int = None, shape: int = None, shape_attack: int = None, pan: int = None, tune_spread: int = None)`
:   Change Emitter Grain Parameters.

`octave(self, emitter_num: int, value: int)`
:   Change Emitter Octave.

`place_in_cell(self, emitter_num: int, column: int, cell: int)`
:   Place Emitter in a given Cell in a given Column.

`play(self, emitter_num: int, note: int = 60, velocity: int = 127, duration: float = 1.0)`
:   Play a note on the Emitter's MIDI channel. Results in all placed cells playing the note.

`play_all(self, emitter_nums: list[int], note: int = 60, velocity: int = 127, duration: float = 1.0)`
:   Play a note on multiple emitters concurrently.
    
    Sends all note_on messages, waits for duration, then sends all note_off messages.
    
    Args:
        emitter_nums: List of emitter numbers (1-4) to play.
        note: MIDI note number.
        velocity: Note velocity.
        duration: Note duration in seconds.

`relative_position(self, emitter_num: int, *, x: int = None, y: int = None)`
:   Change Emitter Position along X and Y axes.

`remove_from_cell(self, emitter_num: int, column: int, cell: int)`
:   Remove Emitter placement from a given Cell in a given Column.

`send_raw(self, message: mido.messages.messages.Message)`
:   Send a raw MIDI message through the queue.

`set_active(self, emitter_num: int)`
:   Set Emitter as Active.

`spray(self, emitter_num: int, *, x: int = None, y: int = None)`
:   Change Emitter Spray along X and Y axes.

`start(self)`
:   Open MIDI port and start the background sender task.

`stop(self)`
:   Stop the sender task, drain the queue, and close the MIDI port.

`tone_filter(self, emitter_num: int, *, width: int = None, center: int = None)`
:   Change Emitter Filter width and center.

`volume(self, emitter_num: int, value: int)`
:   Change Emitter Volume.

---------

`TemperaGlobal(midi_channel: int = 1)`
:   Global controls for the Tempera: modwheel, envelope, effects, canvas and clock.
    
    Args:
        midi_channel: MIDI channel (1-16). Default is 1.

### Static methods

`clock() ‑> mido.messages.messages.Message`
:   Send MIDI Clock message.

`start() ‑> mido.messages.messages.Message`
:   Send MIDI Start message.

`stop() ‑> mido.messages.messages.Message`
:   Send MIDI Stop message.

### Methods

`adsr(self, *, attack: int = None, decay: int = None, sustain: int = None, release: int = None) ‑> list[mido.messages.messages.Message]`
:   Change ADSR envelope parameters.

`change_canvas(self, program: int) ‑> mido.messages.messages.Message`
:   Change the active canvas via MIDI Program Change.
    
    To change the current canvas, send a Program change message with the value between 0 and 127.
    Tempera will then load a canvas from the folder the current canvas is loaded from, with the program number
    corresponding to the canvas name sorted alphabetically.
    
    See: https://docs.beetlecrab.audio/tempera/midi.html#changing-canvases-with-midi

`chorus(self, *, depth: int = None, speed: int = None, flange: int = None, mix: int = None) ‑> list[mido.messages.messages.Message]`
:   Change Chorus parameters.

`delay(self, *, feedback: int = None, time: int = None, color: int = None, mix: int = None) ‑> list[mido.messages.messages.Message]`
:   Change Delay parameters.

`filter(self, *, cutoff: int = None, resonance: int = None) ‑> list[mido.messages.messages.Message]`
:   Change Filter parameters.

`modulator_size(self, modulator_num: int, value: int) ‑> mido.messages.messages.Message`
:   Change Modulator Size for a specific modulator.
    
    Args:
        modulator_num: Modulator number (1-10)
        value: Size value (0-127)
    
    Returns:
        MIDI CC message for the modulator size

`modwheel(self, modwheel: int) ‑> mido.messages.messages.Message`
:   Change Modwheel.

`reverb(self, *, size: int = None, color: int = None, mix: int = None) ‑> list[mido.messages.messages.Message]`
:   Change Reverb parameters.

---------

`Track(track: int = 1, midi_channel: int = 1)`
:   Controls for an individual Tempera track (column).
    
    Args:
        track: Track number (1-8).
        midi_channel: MIDI channel (1-16). Default is 1.

### Methods

`record_on(self) ‑> mido.messages.messages.Message`
:   Set Recording on for Track. Recording starts when audio threshold set in Settings is reached.

`volume(self, value: int) ‑> mido.messages.messages.Message`
:   Change Track Volume.

---------