MIDI_CC_STATUS = 0xB0


def cc(cc_num: int, value: int, channel: int) -> bytes:
    return bytes([MIDI_CC_STATUS | (channel & 0x0F), cc_num & 0x7F, value & 0x7F])


def build_messages(params: dict, cc_map: dict, channel: int) -> bytes:
    result = bytearray()
    for name, value in params.items():
        result.extend(cc(cc_map[name], value, channel))
    return bytes(result)
