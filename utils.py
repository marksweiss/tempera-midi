"""
MIDI message utilities for Tempera.

All functions in this module accept MIDI channels as 1-16 (human-readable),
matching the channel numbers displayed by MIDI software and hardware.
Internally, channels are converted to 0-15 for the MIDI protocol.
"""

MIDI_CC_STATUS = 0xB0
MIDI_NOTE_ON = 0x90
MIDI_NOTE_OFF = 0x80


def cc(cc_num: int, value: int, channel: int) -> bytes:
    """
    Create a MIDI Control Change message.

    Args:
        cc_num: CC number (0-127)
        value: CC value (0-127)
        channel: MIDI channel (1-16)

    Returns:
        3-byte MIDI CC message
    """
    return bytes([MIDI_CC_STATUS | ((channel - 1) & 0x0F), cc_num & 0x7F, value & 0x7F])


def note_on(note: int, velocity: int, channel: int) -> bytes:
    """
    Create a MIDI Note On message.

    Args:
        note: Note number (0-127)
        velocity: Note velocity (0-127)
        channel: MIDI channel (1-16)

    Returns:
        3-byte MIDI Note On message
    """
    return bytes([MIDI_NOTE_ON | ((channel - 1) & 0x0F), note & 0x7F, velocity & 0x7F])


def note_off(note: int, velocity: int, channel: int) -> bytes:
    """
    Create a MIDI Note Off message.

    Args:
        note: Note number (0-127)
        velocity: Note velocity (0-127)
        channel: MIDI channel (1-16)

    Returns:
        3-byte MIDI Note Off message
    """
    return bytes([MIDI_NOTE_OFF | ((channel - 1) & 0x0F), note & 0x7F, velocity & 0x7F])


def build_messages(params: dict, cc_map: dict, channel: int) -> bytes:
    """
    Build multiple MIDI CC messages from a parameter dictionary.

    Args:
        params: Dictionary mapping parameter names to values
        cc_map: Dictionary mapping parameter names to CC numbers
        channel: MIDI channel (1-16)

    Returns:
        Concatenated MIDI CC messages
    """
    result = bytearray()
    for name, value in params.items():
        result.extend(cc(cc_map[name], value, channel))
    return bytes(result)
