from tempera.constants import (
    ADSR_ATTACK, ADSR_DECAY, ADSR_SUSTAIN, ADSR_RELEASE,
    MODWHEEL, REVERB_SIZE, REVERB_COLOR, REVERB_MIX,
    DELAY_FEEDBACK, DELAY_TIME, DELAY_COLOR, DELAY_MIX,
    CHORUS_DEPTH, CHORUS_SPEED, CHORUS_FLANGE, CHORUS_MIX,
    MODULATOR_1_SIZE, MODULATOR_2_SIZE, MODULATOR_3_SIZE, MODULATOR_4_SIZE,
    MODULATOR_5_SIZE, MODULATOR_6_SIZE, MODULATOR_7_SIZE, MODULATOR_8_SIZE,
    MODULATOR_9_SIZE, MODULATOR_10_SIZE,
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

MODULATOR_SIZE_CC_MAP = {
    1: MODULATOR_1_SIZE,
    2: MODULATOR_2_SIZE,
    3: MODULATOR_3_SIZE,
    4: MODULATOR_4_SIZE,
    5: MODULATOR_5_SIZE,
    6: MODULATOR_6_SIZE,
    7: MODULATOR_7_SIZE,
    8: MODULATOR_8_SIZE,
    9: MODULATOR_9_SIZE,
    10: MODULATOR_10_SIZE,
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

    def modwheel(
            self,
            modwheel: int
    ) -> Message:
        """Change Modwheel."""
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, MODWHEEL_CC_MAP)[0]

    def modulator_size(
            self,
            modulator_num: int,
            value: int
    ) -> Message:
        """Change Modulator Size for a specific modulator.

        Args:
            modulator_num: Modulator number (1-10)
            value: Size value (0-127)

        Returns:
            MIDI CC message for the modulator size
        """
        if modulator_num not in MODULATOR_SIZE_CC_MAP:
            raise ValueError(f"Invalid modulator number: {modulator_num}. Must be 1-10.")
        cc_num = MODULATOR_SIZE_CC_MAP[modulator_num]
        return self.midi.cc(cc_num, value)

    def adsr(
        self,
        *,
        attack: int = None,
        decay: int = None,
        sustain: int = None,
        release: int = None
    ) -> list[Message]:
        """Change ADSR envelope parameters."""
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, ADSR_CC_MAP)

    def reverb(
        self,
        *,
        size: int = None,
        color: int = None,
        mix: int = None
    ) -> list[Message]:
        """Change Reverb parameters."""
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, REVERB_CC_MAP)

    def delay(
        self,
        *,
        feedback: int = None,
        time: int = None,
        color: int = None,
        mix: int = None
    ) -> list[Message]:
        """Change Delay parameters."""
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, DELAY_CC_MAP)

    def chorus(
        self,
        *,
        depth: int = None,
        speed: int = None,
        flange: int = None,
        mix: int = None
    ) -> list[Message]:
        """Change Chorus parameters."""
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, CHORUS_CC_MAP)

    def change_canvas(self, program: int) -> Message:
        """Change the active canvas via MIDI Program Change.

        To change the current canvas, send a Program change message with the value between 0 and 127.
        Tempera will then load a canvas from the folder the current canvas is loaded from, with the program number
        corresponding to the canvas name sorted alphabetically.

        See: https://docs.beetlecrab.audio/tempera/midi.html#changing-canvases-with-midi
        """
        return self.midi.program_change(program)

    @staticmethod
    def clock() -> Message:
        """Send MIDI Clock message."""
        return Midi.clock()

    @staticmethod
    def start() -> Message:
        """Send MIDI Start message."""
        return Midi.start()

    @staticmethod
    def stop() -> Message:
        """Send MIDI Stop message."""
        return Midi.stop()
