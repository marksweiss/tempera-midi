MIDI_CC_STATUS = 0xB0
MIDI_NOTE_ON = 0x90
MIDI_NOTE_OFF = 0x80


def cc(cc_num: int, value: int, channel: int) -> bytes:
    return bytes([MIDI_CC_STATUS | (channel & 0x0F), cc_num & 0x7F, value & 0x7F])


def note_on(note: int, velocity: int, channel: int) -> bytes:
    return bytes([MIDI_NOTE_ON | (channel & 0x0F), note & 0x7F, velocity & 0x7F])


def note_off(note: int, velocity: int, channel: int) -> bytes:
    return bytes([MIDI_NOTE_OFF | (channel & 0x0F), note & 0x7F, velocity & 0x7F])


def build_messages(params: dict, cc_map: dict, channel: int) -> bytes:
    result = bytearray()
    for name, value in params.items():
        result.extend(cc(cc_map[name], value, channel))
    return bytes(result)
