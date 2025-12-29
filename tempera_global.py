from constants import (
    ADSR_ATTACK, ADSR_DECAY, ADSR_SUSTAIN, ADSR_RELEASE,
    MODWHEEL, REVERB_SIZE, REVERB_COLOR, REVERB_MIX,
    DELAY_FEEDBACK, DELAY_TIME, DELAY_COLOR, DELAY_MIX,
    CHORUS_DEPTH, CHORUS_SPEED, CHORUS_FLANGE, CHORUS_MIX,
)
from midi import Midi
from mido import Message

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
        self.midi = Midi(midi_channel)

    """
    Change Modwheel
    """
    def modwheel(
            self,
            modwheel: int
    ) -> list[Message]:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, MODWHEEL_CC_MAP)

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
    ) -> list[Message]:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, ADSR_CC_MAP)

    """
    Change Reverb parameters
    """
    def reverb(
        self,
        *,
        size: int = None,
        color: int = None,
        mix: int = None
    ) -> list[Message]:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, REVERB_CC_MAP)

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
    ) -> list[Message]:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, DELAY_CC_MAP)

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
    ) -> list[Message]:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, CHORUS_CC_MAP)

    """
    Change Canvas
    
    'To change the current canvas, send a Program change message with the value between 0 and 127.
    Tempera will then load a canvas form the folder the current canvas is loaded from, with the program number
    corresponding to the canvas name sorted alphabetically.'
    
    https://docs.beetlecrab.audio/tempera/midi.html#changing-canvases-with-midi
    """
    def change_canvas(self, program: int) -> Message:
        """Change the active canvas via MIDI Program Change."""
        return self.midi.program_change(program)

    """
    Send MIDI Clock message
    """
    @staticmethod
    def clock() -> Message:
        return Midi.clock()

    """
    Send MIDI Start message
    """
    @staticmethod
    def start() -> Message:
        return Midi.start()

    """
    Send MIDI Stop message
    """
    @staticmethod
    def stop() -> Message:
        return Midi.stop()
