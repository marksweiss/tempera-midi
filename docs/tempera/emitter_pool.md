Module tempera.emitter_pool
===========================

Classes
-------

`EmitterPool(port_name: str = None, virtual: bool = False)`
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