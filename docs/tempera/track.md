Module tempera.track
====================

Classes
-------

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