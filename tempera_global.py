from constants import (
    ADSR_ATTACK, ADSR_DECAY, ADSR_SUSTAIN, ADSR_RELEASE,
    MODWHEEL, REVERB_SIZE, REVERB_COLOR, REVERB_MIX,
    DELAY_FEEDBACK, DELAY_TIME, DELAY_COLOR, DELAY_MIX,
    CHORUS_DEPTH, CHORUS_SPEED, CHORUS_FLANGE, CHORUS_MIX,
    MIDI_PC_STATUS, MIDI_CLOCK, MIDI_START, MIDI_STOP,
)
from utils import build_messages

MODWHEEL_CC_MAP = {
    'modwheel': MODWHEEL,
}

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


class TemperaGlobal:
    """
    Global controls for the Tempera: modwheel, envelope, effects, canvas and clock.

    Args:
        midi_channel: MIDI channel (1-16). Default is 1.
    """

    def __init__(self, midi_channel: int = 1):
        self.midi_channel = midi_channel

    """
    Change Modwheel
    """
    def modwheel(
            self,
            *,
            modwheel: int = None,
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, MODWHEEL_CC_MAP, self.midi_channel)

    """
    Change ADSR envelope parameters
    """
    def adsr(
        self,
        *,
        attack: int = None,
        decay: int = None,
        sustain: int = None,
        release: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, ADSR_CC_MAP, self.midi_channel)

    """
    Change Reverb parameters
    """
    def reverb(
        self,
        *,
        size: int = None,
        color: int = None,
        mix: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, REVERB_CC_MAP, self.midi_channel)

    """
    Change Delay parameters
    """
    def delay(
        self,
        *,
        feedback: int = None,
        time: int = None,
        color: int = None,
        mix: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, DELAY_CC_MAP, self.midi_channel)

    """
    Change Chorus parameters
    """
    def chorus(
        self,
        *,
        depth: int = None,
        speed: int = None,
        flange: int = None,
        mix: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, CHORUS_CC_MAP, self.midi_channel)

    def change_canvas(self, program: int) -> bytes:
        """Change the active canvas via MIDI Program Change."""
        return bytes([MIDI_PC_STATUS | ((self.midi_channel - 1) & 0x0F), program & 0x7F])

    """
    Send MIDI Clock message
    """
    @staticmethod
    def clock() -> bytes:
        return bytes([MIDI_CLOCK])

    """
    Send MIDI Start message
    """
    @staticmethod
    def start() -> bytes:
        return bytes([MIDI_START])

    """
    Send MIDI Stop message
    """
    @staticmethod
    def stop() -> bytes:
        return bytes([MIDI_STOP])
