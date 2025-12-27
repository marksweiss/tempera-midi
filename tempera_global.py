from midi_constants import (
    ADSR_ATTACK, ADSR_DECAY, ADSR_SUSTAIN, ADSR_RELEASE,
    REVERB_SIZE, REVERB_COLOR, REVERB_MIX,
    DELAY_FEEDBACK, DELAY_TIME, DELAY_COLOR, DELAY_MIX,
    CHORUS_DEPTH, CHORUS_SPEED, CHORUS_FLANGE, CHORUS_MIX,
    TRACK_1_VOLUME, TRACK_2_VOLUME, TRACK_3_VOLUME, TRACK_4_VOLUME,
    TRACK_5_VOLUME, TRACK_6_VOLUME, TRACK_7_VOLUME, TRACK_8_VOLUME,
)
from utils import build_messages

ADSR_CC_MAP = {
    'attack': ADSR_ATTACK,
    'decay': ADSR_DECAY,
    'sustain': ADSR_SUSTAIN,
    'release': ADSR_RELEASE,
}

REVERB_CC_MAP = {
    'size': REVERB_SIZE,
    'color': REVERB_COLOR,
    'mix': REVERB_MIX,
}

DELAY_CC_MAP = {
    'feedback': DELAY_FEEDBACK,
    'time': DELAY_TIME,
    'color': DELAY_COLOR,
    'mix': DELAY_MIX,
}

CHORUS_CC_MAP = {
    'depth': CHORUS_DEPTH,
    'speed': CHORUS_SPEED,
    'flange': CHORUS_FLANGE,
    'mix': CHORUS_MIX,
}

TRACK_VOLUME_CC_MAP = {
    'track_1': TRACK_1_VOLUME,
    'track_2': TRACK_2_VOLUME,
    'track_3': TRACK_3_VOLUME,
    'track_4': TRACK_4_VOLUME,
    'track_5': TRACK_5_VOLUME,
    'track_6': TRACK_6_VOLUME,
    'track_7': TRACK_7_VOLUME,
    'track_8': TRACK_8_VOLUME,
}


class TemperaGlobal:
    MIDI_PC_STATUS = 0xC0
    MIDI_CLOCK = 0xF8
    MIDI_START = 0xFA
    MIDI_STOP = 0xFC

    def __init__(self, channel: int = 1):
        self.channel = channel

    def adsr(
        self,
        *,
        attack: int = None,
        decay: int = None,
        sustain: int = None,
        release: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, ADSR_CC_MAP, self.channel)

    def reverb(
        self,
        *,
        size: int = None,
        color: int = None,
        mix: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, REVERB_CC_MAP, self.channel)

    def delay(
        self,
        *,
        feedback: int = None,
        time: int = None,
        color: int = None,
        mix: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, DELAY_CC_MAP, self.channel)

    def chorus(
        self,
        *,
        depth: int = None,
        speed: int = None,
        flange: int = None,
        mix: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, CHORUS_CC_MAP, self.channel)

    def track_volume(
        self,
        *,
        track_1: int = None,
        track_2: int = None,
        track_3: int = None,
        track_4: int = None,
        track_5: int = None,
        track_6: int = None,
        track_7: int = None,
        track_8: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, TRACK_VOLUME_CC_MAP, self.channel)

    def change_canvas(self, program: int) -> bytes:
        return bytes([TemperaGlobal.MIDI_PC_STATUS | (self.channel & 0x0F), program & 0x7F])

    @staticmethod
    def clock() -> bytes:
        return bytes([TemperaGlobal.MIDI_CLOCK])

    @staticmethod
    def start() -> bytes:
        return bytes([TemperaGlobal.MIDI_START])

    @staticmethod
    def stop() -> bytes:
        return bytes([TemperaGlobal.MIDI_STOP])
