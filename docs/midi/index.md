Module midi
===========
MIDI message generation library.

Sub-modules
-----------
* midi.midi

Classes
-------

`Midi(midi_channel=1, port=None)`
:   

### Static methods

`clock() ‑> mido.messages.messages.Message`
:   Create a MIDI Clock message.
    
    Returns:
        1-byte MIDI Clock message

`start() ‑> mido.messages.messages.Message`
:   Create a MIDI Start message.
    
    Returns:
        1-byte MIDI Start message

`stop() ‑> mido.messages.messages.Message`
:   Create a MIDI Stop message.
    
    Returns:
        1-byte MIDI Stop message

### Methods

`all_ccs(self, params: dict, cc_map: dict) ‑> list[mido.messages.messages.Message]`
:   Build multiple MIDI CC messages from a parameter dictionary.
    
    Args:
        params: Dictionary mapping parameter names to values
        cc_map: Dictionary mapping parameter names to CC numbers
    
    Returns:
        Concatenated MIDI CC messages

`cc(self, cc_num: int, value: int) ‑> mido.messages.messages.Message`
:   Create a MIDI Control Change message.
    
    Args:
        cc_num: CC number (0-127)
        value: CC value (0-127)
    
    Returns:
        3-byte MIDI CC message

`note_off(self, note: int, time: int = 0) ‑> mido.messages.messages.Message`
:   Create a MIDI Note Off message.
    
    Args:
        note: Note number (0-127)
        time: Time in ticks (default 0), 480 ticks = 1 quarter note at current tempo
    
    Returns:
        3-byte MIDI Note Off message

`note_on(self, note: int, velocity: int, time: int = 0) ‑> mido.messages.messages.Message`
:   Create a MIDI Note On message.
    
    Args:
        note: Note number (0-127)
        velocity: Note velocity (0-127)
        time: Time in ticks (default 0), 480 ticks = 1 quarter note at current tempo
    
    Returns:
        3-byte MIDI Note On message

`program_change(self, program: int) ‑> mido.messages.messages.Message`
:   Create a MIDI Program Change message.
    
    Args:
        program: Program number (0-127)
    
    Returns:
        2-byte MIDI Program Change message

`send(self, message: mido.messages.messages.Message)`
:   

---------