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

    `modwheel(self, modwheel: int) ‑> mido.messages.messages.Message`
    :   Change Modwheel.

    `reverb(self, *, size: int = None, color: int = None, mix: int = None) ‑> list[mido.messages.messages.Message]`
    :   Change Reverb parameters.