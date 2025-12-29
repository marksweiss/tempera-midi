Module emitter
==============

Classes
-------

`Emitter(emitter: int = 1, midi_channel: int = 1)`
:   Controls for an individual Tempera emitter.
    
    Args:
        emitter: Emitter number (1-4).
        midi_channel: MIDI channel (1-16). Default is 1.

    ### Instance variables

    `emitter_num`
    :

    ### Methods

    `effects_send(self, value: int) ‑> mido.messages.messages.Message`
    :

    `grain(self, *, length_cell: int = None, length_note: int = None, density: int = None, shape: int = None, shape_attack: int = None, pan: int = None, tune_spread: int = None) ‑> list[mido.messages.messages.Message]`
    :

    `octave(self, value: int) ‑> mido.messages.messages.Message`
    :

    `place_in_cell(self, column: int, cell: int) ‑> mido.messages.messages.Message`
    :

    `relative_position(self, *, x: int = None, y: int = None) ‑> list[mido.messages.messages.Message]`
    :

    `remove_from_cell(self, column: int, cell: int) ‑> mido.messages.messages.Message`
    :

    `set_active(self) ‑> mido.messages.messages.Message`
    :

    `spray(self, *, x: int = None, y: int = None) ‑> list[mido.messages.messages.Message]`
    :

    `tone_filter(self, *, width: int = None, center: int = None) ‑> list[mido.messages.messages.Message]`
    :

    `volume(self, value: int) ‑> mido.messages.messages.Message`
    :