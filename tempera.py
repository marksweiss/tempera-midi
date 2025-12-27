from midi_constants import (
    ADSR_ATTACK, ADSR_DECAY, ADSR_SUSTAIN, ADSR_RELEASE,
    REVERB_SIZE, REVERB_COLOR, REVERB_MIX,
    DELAY_FEEDBACK, DELAY_TIME, DELAY_COLOR, DELAY_MIX,
    CHORUS_DEPTH, CHORUS_SPEED, CHORUS_FLANGE, CHORUS_MIX,
    TRACK_1_VOLUME, TRACK_2_VOLUME, TRACK_3_VOLUME, TRACK_4_VOLUME,
    TRACK_5_VOLUME, TRACK_6_VOLUME, TRACK_7_VOLUME, TRACK_8_VOLUME,
    EMITTER_1_VOLUME, EMITTER_1_GRAIN_LENGTH_CELL, EMITTER_1_GRAIN_LENGTH_NOTE,
    EMITTER_1_GRAIN_DENSITY, EMITTER_1_GRAIN_SHAPE, EMITTER_1_GRAIN_SHAPE_ATTACK,
    EMITTER_1_GRAIN_PAN, EMITTER_1_GRAIN_TUNE_SPREAD, EMITTER_1_OCTAVE,
    EMITTER_1_RELATIVE_X, EMITTER_1_RELATIVE_Y, EMITTER_1_SPRAY_X, EMITTER_1_SPRAY_Y,
    EMITTER_1_TONE_FILTER_WIDTH, EMITTER_1_TONE_FILTER_CENTER, EMITTER_1_EFFECTS_SEND,
    EMITTER_2_VOLUME, EMITTER_2_GRAIN_LENGTH_CELL, EMITTER_2_GRAIN_LENGTH_NOTE,
    EMITTER_2_GRAIN_DENSITY, EMITTER_2_GRAIN_SHAPE, EMITTER_2_GRAIN_SHAPE_ATTACK,
    EMITTER_2_GRAIN_PAN, EMITTER_2_GRAIN_TUNE_SPREAD, EMITTER_2_OCTAVE,
    EMITTER_2_RELATIVE_X, EMITTER_2_RELATIVE_Y, EMITTER_2_SPRAY_X, EMITTER_2_SPRAY_Y,
    EMITTER_2_TONE_FILTER_WIDTH, EMITTER_2_TONE_FILTER_CENTER, EMITTER_2_EFFECTS_SEND,
    EMITTER_3_VOLUME, EMITTER_3_GRAIN_LENGTH_CELL, EMITTER_3_GRAIN_LENGTH_NOTE,
    EMITTER_3_GRAIN_DENSITY, EMITTER_3_GRAIN_SHAPE, EMITTER_3_GRAIN_SHAPE_ATTACK,
    EMITTER_3_GRAIN_PAN, EMITTER_3_GRAIN_TUNE_SPREAD, EMITTER_3_OCTAVE,
    EMITTER_3_RELATIVE_X, EMITTER_3_RELATIVE_Y, EMITTER_3_SPRAY_X, EMITTER_3_SPRAY_Y,
    EMITTER_3_TONE_FILTER_WIDTH, EMITTER_3_TONE_FILTER_CENTER, EMITTER_3_EFFECTS_SEND,
    EMITTER_4_VOLUME, EMITTER_4_GRAIN_LENGTH_CELL, EMITTER_4_GRAIN_LENGTH_NOTE,
    EMITTER_4_GRAIN_DENSITY, EMITTER_4_GRAIN_SHAPE, EMITTER_4_GRAIN_SHAPE_ATTACK,
    EMITTER_4_GRAIN_PAN, EMITTER_4_GRAIN_TUNE_SPREAD, EMITTER_4_OCTAVE,
    EMITTER_4_RELATIVE_X, EMITTER_4_RELATIVE_Y, EMITTER_4_SPRAY_X, EMITTER_4_SPRAY_Y,
    EMITTER_4_TONE_FILTER_WIDTH, EMITTER_4_TONE_FILTER_CENTER, EMITTER_4_EFFECTS_SEND,
)

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

EMITTER_1_CC_MAP = {
    'volume': EMITTER_1_VOLUME,
    'grain_length_cell': EMITTER_1_GRAIN_LENGTH_CELL,
    'grain_length_note': EMITTER_1_GRAIN_LENGTH_NOTE,
    'grain_density': EMITTER_1_GRAIN_DENSITY,
    'grain_shape': EMITTER_1_GRAIN_SHAPE,
    'grain_shape_attack': EMITTER_1_GRAIN_SHAPE_ATTACK,
    'grain_pan': EMITTER_1_GRAIN_PAN,
    'grain_tune_spread': EMITTER_1_GRAIN_TUNE_SPREAD,
    'octave': EMITTER_1_OCTAVE,
    'relative_x': EMITTER_1_RELATIVE_X,
    'relative_y': EMITTER_1_RELATIVE_Y,
    'spray_x': EMITTER_1_SPRAY_X,
    'spray_y': EMITTER_1_SPRAY_Y,
    'tone_filter_width': EMITTER_1_TONE_FILTER_WIDTH,
    'tone_filter_center': EMITTER_1_TONE_FILTER_CENTER,
    'effects_send': EMITTER_1_EFFECTS_SEND,
}

EMITTER_2_CC_MAP = {
    'volume': EMITTER_2_VOLUME,
    'grain_length_cell': EMITTER_2_GRAIN_LENGTH_CELL,
    'grain_length_note': EMITTER_2_GRAIN_LENGTH_NOTE,
    'grain_density': EMITTER_2_GRAIN_DENSITY,
    'grain_shape': EMITTER_2_GRAIN_SHAPE,
    'grain_shape_attack': EMITTER_2_GRAIN_SHAPE_ATTACK,
    'grain_pan': EMITTER_2_GRAIN_PAN,
    'grain_tune_spread': EMITTER_2_GRAIN_TUNE_SPREAD,
    'octave': EMITTER_2_OCTAVE,
    'relative_x': EMITTER_2_RELATIVE_X,
    'relative_y': EMITTER_2_RELATIVE_Y,
    'spray_x': EMITTER_2_SPRAY_X,
    'spray_y': EMITTER_2_SPRAY_Y,
    'tone_filter_width': EMITTER_2_TONE_FILTER_WIDTH,
    'tone_filter_center': EMITTER_2_TONE_FILTER_CENTER,
    'effects_send': EMITTER_2_EFFECTS_SEND,
}

EMITTER_3_CC_MAP = {
    'volume': EMITTER_3_VOLUME,
    'grain_length_cell': EMITTER_3_GRAIN_LENGTH_CELL,
    'grain_length_note': EMITTER_3_GRAIN_LENGTH_NOTE,
    'grain_density': EMITTER_3_GRAIN_DENSITY,
    'grain_shape': EMITTER_3_GRAIN_SHAPE,
    'grain_shape_attack': EMITTER_3_GRAIN_SHAPE_ATTACK,
    'grain_pan': EMITTER_3_GRAIN_PAN,
    'grain_tune_spread': EMITTER_3_GRAIN_TUNE_SPREAD,
    'octave': EMITTER_3_OCTAVE,
    'relative_x': EMITTER_3_RELATIVE_X,
    'relative_y': EMITTER_3_RELATIVE_Y,
    'spray_x': EMITTER_3_SPRAY_X,
    'spray_y': EMITTER_3_SPRAY_Y,
    'tone_filter_width': EMITTER_3_TONE_FILTER_WIDTH,
    'tone_filter_center': EMITTER_3_TONE_FILTER_CENTER,
    'effects_send': EMITTER_3_EFFECTS_SEND,
}

EMITTER_4_CC_MAP = {
    'volume': EMITTER_4_VOLUME,
    'grain_length_cell': EMITTER_4_GRAIN_LENGTH_CELL,
    'grain_length_note': EMITTER_4_GRAIN_LENGTH_NOTE,
    'grain_density': EMITTER_4_GRAIN_DENSITY,
    'grain_shape': EMITTER_4_GRAIN_SHAPE,
    'grain_shape_attack': EMITTER_4_GRAIN_SHAPE_ATTACK,
    'grain_pan': EMITTER_4_GRAIN_PAN,
    'grain_tune_spread': EMITTER_4_GRAIN_TUNE_SPREAD,
    'octave': EMITTER_4_OCTAVE,
    'relative_x': EMITTER_4_RELATIVE_X,
    'relative_y': EMITTER_4_RELATIVE_Y,
    'spray_x': EMITTER_4_SPRAY_X,
    'spray_y': EMITTER_4_SPRAY_Y,
    'tone_filter_width': EMITTER_4_TONE_FILTER_WIDTH,
    'tone_filter_center': EMITTER_4_TONE_FILTER_CENTER,
    'effects_send': EMITTER_4_EFFECTS_SEND,
}


class Tempera:
    MIDI_CC_STATUS = 0xB0

    @staticmethod
    def _cc(cc: int, value: int, channel: int = 0) -> bytes:
        return bytes([Tempera.MIDI_CC_STATUS | (channel & 0x0F), cc & 0x7F, value & 0x7F])

    @staticmethod
    def _build_messages(params: dict, cc_map: dict, channel: int) -> bytes:
        result = bytearray()
        for name, value in params.items():
            result.extend(Tempera._cc(cc_map[name], value, channel))
        return bytes(result)

    @staticmethod
    def adsr(
        *,
        attack: int = None,
        decay: int = None,
        sustain: int = None,
        release: int = None,
        channel: int = 0
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'channel'}
        return Tempera._build_messages(params, ADSR_CC_MAP, channel)

    @staticmethod
    def reverb(
        *,
        size: int = None,
        color: int = None,
        mix: int = None,
        channel: int = 0
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'channel'}
        return Tempera._build_messages(params, REVERB_CC_MAP, channel)

    @staticmethod
    def delay(
        *,
        feedback: int = None,
        time: int = None,
        color: int = None,
        mix: int = None,
        channel: int = 0
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'channel'}
        return Tempera._build_messages(params, DELAY_CC_MAP, channel)

    @staticmethod
    def chorus(
        *,
        depth: int = None,
        speed: int = None,
        flange: int = None,
        mix: int = None,
        channel: int = 0
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'channel'}
        return Tempera._build_messages(params, CHORUS_CC_MAP, channel)

    @staticmethod
    def track_volume(
        *,
        track_1: int = None,
        track_2: int = None,
        track_3: int = None,
        track_4: int = None,
        track_5: int = None,
        track_6: int = None,
        track_7: int = None,
        track_8: int = None,
        channel: int = 0
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'channel'}
        return Tempera._build_messages(params, TRACK_VOLUME_CC_MAP, channel)

    @staticmethod
    def emitter_1(
        *,
        volume: int = None,
        grain_length_cell: int = None,
        grain_length_note: int = None,
        grain_density: int = None,
        grain_shape: int = None,
        grain_shape_attack: int = None,
        grain_pan: int = None,
        grain_tune_spread: int = None,
        octave: int = None,
        relative_x: int = None,
        relative_y: int = None,
        spray_x: int = None,
        spray_y: int = None,
        tone_filter_width: int = None,
        tone_filter_center: int = None,
        effects_send: int = None,
        channel: int = 0
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'channel'}
        return Tempera._build_messages(params, EMITTER_1_CC_MAP, channel)

    @staticmethod
    def emitter_2(
        *,
        volume: int = None,
        grain_length_cell: int = None,
        grain_length_note: int = None,
        grain_density: int = None,
        grain_shape: int = None,
        grain_shape_attack: int = None,
        grain_pan: int = None,
        grain_tune_spread: int = None,
        octave: int = None,
        relative_x: int = None,
        relative_y: int = None,
        spray_x: int = None,
        spray_y: int = None,
        tone_filter_width: int = None,
        tone_filter_center: int = None,
        effects_send: int = None,
        channel: int = 0
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'channel'}
        return Tempera._build_messages(params, EMITTER_2_CC_MAP, channel)

    @staticmethod
    def emitter_3(
        *,
        volume: int = None,
        grain_length_cell: int = None,
        grain_length_note: int = None,
        grain_density: int = None,
        grain_shape: int = None,
        grain_shape_attack: int = None,
        grain_pan: int = None,
        grain_tune_spread: int = None,
        octave: int = None,
        relative_x: int = None,
        relative_y: int = None,
        spray_x: int = None,
        spray_y: int = None,
        tone_filter_width: int = None,
        tone_filter_center: int = None,
        effects_send: int = None,
        channel: int = 0
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'channel'}
        return Tempera._build_messages(params, EMITTER_3_CC_MAP, channel)

    @staticmethod
    def emitter_4(
        *,
        volume: int = None,
        grain_length_cell: int = None,
        grain_length_note: int = None,
        grain_density: int = None,
        grain_shape: int = None,
        grain_shape_attack: int = None,
        grain_pan: int = None,
        grain_tune_spread: int = None,
        octave: int = None,
        relative_x: int = None,
        relative_y: int = None,
        spray_x: int = None,
        spray_y: int = None,
        tone_filter_width: int = None,
        tone_filter_center: int = None,
        effects_send: int = None,
        channel: int = 0
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'channel'}
        return Tempera._build_messages(params, EMITTER_4_CC_MAP, channel)