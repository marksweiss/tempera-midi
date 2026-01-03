Module tempera.emitter
======================

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