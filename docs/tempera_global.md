Module tempera_global
=====================

Classes
-------

`TemperaGlobal(midi_channel: int = 1)`
:   Global controls for the Tempera: modwheel, envelope, effects, canvas and clock.
    
    Args:
        midi_channel: MIDI channel (1-16). Default is 1.

    ### Static methods

    `clock() ‑> mido.messages.messages.Message`
    :

    `start() ‑> mido.messages.messages.Message`
    :

    `stop() ‑> mido.messages.messages.Message`
    :

    ### Methods

    `adsr(self, *, attack: int = None, decay: int = None, sustain: int = None, release: int = None) ‑> list[mido.messages.messages.Message]`
    :

    `change_canvas(self, program: int) ‑> mido.messages.messages.Message`
    :   Change the active canvas via MIDI Program Change.

    `chorus(self, *, depth: int = None, speed: int = None, flange: int = None, mix: int = None) ‑> list[mido.messages.messages.Message]`
    :

    `delay(self, *, feedback: int = None, time: int = None, color: int = None, mix: int = None) ‑> list[mido.messages.messages.Message]`
    :

    `modwheel(self, modwheel: int) ‑> mido.messages.messages.Message`
    :

    `reverb(self, *, size: int = None, color: int = None, mix: int = None) ‑> list[mido.messages.messages.Message]`
    :