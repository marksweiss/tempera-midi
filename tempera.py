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


class Tempera:
    MIDI_CC_STATUS = 0xB0

    @staticmethod
    def _cc(cc: int, value: int, channel: int = 0) -> bytes:
        return bytes([Tempera.MIDI_CC_STATUS | (channel & 0x0F), cc & 0x7F, value & 0x7F])

    @staticmethod
    def adsr(
        *,
        attack: int = None,
        decay: int = None,
        sustain: int = None,
        release: int = None,
        channel: int = 0
    ) -> bytes:
        result = bytearray()
        if attack is not None:
            result.extend(Tempera._cc(ADSR_ATTACK, attack, channel))
        if decay is not None:
            result.extend(Tempera._cc(ADSR_DECAY, decay, channel))
        if sustain is not None:
            result.extend(Tempera._cc(ADSR_SUSTAIN, sustain, channel))
        if release is not None:
            result.extend(Tempera._cc(ADSR_RELEASE, release, channel))
        return bytes(result)

    @staticmethod
    def reverb(
        *,
        size: int = None,
        color: int = None,
        mix: int = None,
        channel: int = 0
    ) -> bytes:
        result = bytearray()
        if size is not None:
            result.extend(Tempera._cc(REVERB_SIZE, size, channel))
        if color is not None:
            result.extend(Tempera._cc(REVERB_COLOR, color, channel))
        if mix is not None:
            result.extend(Tempera._cc(REVERB_MIX, mix, channel))
        return bytes(result)

    @staticmethod
    def delay(
        *,
        feedback: int = None,
        time: int = None,
        color: int = None,
        mix: int = None,
        channel: int = 0
    ) -> bytes:
        result = bytearray()
        if feedback is not None:
            result.extend(Tempera._cc(DELAY_FEEDBACK, feedback, channel))
        if time is not None:
            result.extend(Tempera._cc(DELAY_TIME, time, channel))
        if color is not None:
            result.extend(Tempera._cc(DELAY_COLOR, color, channel))
        if mix is not None:
            result.extend(Tempera._cc(DELAY_MIX, mix, channel))
        return bytes(result)

    @staticmethod
    def chorus(
        *,
        depth: int = None,
        speed: int = None,
        flange: int = None,
        mix: int = None,
        channel: int = 0
    ) -> bytes:
        result = bytearray()
        if depth is not None:
            result.extend(Tempera._cc(CHORUS_DEPTH, depth, channel))
        if speed is not None:
            result.extend(Tempera._cc(CHORUS_SPEED, speed, channel))
        if flange is not None:
            result.extend(Tempera._cc(CHORUS_FLANGE, flange, channel))
        if mix is not None:
            result.extend(Tempera._cc(CHORUS_MIX, mix, channel))
        return bytes(result)

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
        result = bytearray()
        if track_1 is not None:
            result.extend(Tempera._cc(TRACK_1_VOLUME, track_1, channel))
        if track_2 is not None:
            result.extend(Tempera._cc(TRACK_2_VOLUME, track_2, channel))
        if track_3 is not None:
            result.extend(Tempera._cc(TRACK_3_VOLUME, track_3, channel))
        if track_4 is not None:
            result.extend(Tempera._cc(TRACK_4_VOLUME, track_4, channel))
        if track_5 is not None:
            result.extend(Tempera._cc(TRACK_5_VOLUME, track_5, channel))
        if track_6 is not None:
            result.extend(Tempera._cc(TRACK_6_VOLUME, track_6, channel))
        if track_7 is not None:
            result.extend(Tempera._cc(TRACK_7_VOLUME, track_7, channel))
        if track_8 is not None:
            result.extend(Tempera._cc(TRACK_8_VOLUME, track_8, channel))
        return bytes(result)

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
        result = bytearray()
        if volume is not None:
            result.extend(Tempera._cc(EMITTER_1_VOLUME, volume, channel))
        if grain_length_cell is not None:
            result.extend(Tempera._cc(EMITTER_1_GRAIN_LENGTH_CELL, grain_length_cell, channel))
        if grain_length_note is not None:
            result.extend(Tempera._cc(EMITTER_1_GRAIN_LENGTH_NOTE, grain_length_note, channel))
        if grain_density is not None:
            result.extend(Tempera._cc(EMITTER_1_GRAIN_DENSITY, grain_density, channel))
        if grain_shape is not None:
            result.extend(Tempera._cc(EMITTER_1_GRAIN_SHAPE, grain_shape, channel))
        if grain_shape_attack is not None:
            result.extend(Tempera._cc(EMITTER_1_GRAIN_SHAPE_ATTACK, grain_shape_attack, channel))
        if grain_pan is not None:
            result.extend(Tempera._cc(EMITTER_1_GRAIN_PAN, grain_pan, channel))
        if grain_tune_spread is not None:
            result.extend(Tempera._cc(EMITTER_1_GRAIN_TUNE_SPREAD, grain_tune_spread, channel))
        if octave is not None:
            result.extend(Tempera._cc(EMITTER_1_OCTAVE, octave, channel))
        if relative_x is not None:
            result.extend(Tempera._cc(EMITTER_1_RELATIVE_X, relative_x, channel))
        if relative_y is not None:
            result.extend(Tempera._cc(EMITTER_1_RELATIVE_Y, relative_y, channel))
        if spray_x is not None:
            result.extend(Tempera._cc(EMITTER_1_SPRAY_X, spray_x, channel))
        if spray_y is not None:
            result.extend(Tempera._cc(EMITTER_1_SPRAY_Y, spray_y, channel))
        if tone_filter_width is not None:
            result.extend(Tempera._cc(EMITTER_1_TONE_FILTER_WIDTH, tone_filter_width, channel))
        if tone_filter_center is not None:
            result.extend(Tempera._cc(EMITTER_1_TONE_FILTER_CENTER, tone_filter_center, channel))
        if effects_send is not None:
            result.extend(Tempera._cc(EMITTER_1_EFFECTS_SEND, effects_send, channel))
        return bytes(result)

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
        result = bytearray()
        if volume is not None:
            result.extend(Tempera._cc(EMITTER_2_VOLUME, volume, channel))
        if grain_length_cell is not None:
            result.extend(Tempera._cc(EMITTER_2_GRAIN_LENGTH_CELL, grain_length_cell, channel))
        if grain_length_note is not None:
            result.extend(Tempera._cc(EMITTER_2_GRAIN_LENGTH_NOTE, grain_length_note, channel))
        if grain_density is not None:
            result.extend(Tempera._cc(EMITTER_2_GRAIN_DENSITY, grain_density, channel))
        if grain_shape is not None:
            result.extend(Tempera._cc(EMITTER_2_GRAIN_SHAPE, grain_shape, channel))
        if grain_shape_attack is not None:
            result.extend(Tempera._cc(EMITTER_2_GRAIN_SHAPE_ATTACK, grain_shape_attack, channel))
        if grain_pan is not None:
            result.extend(Tempera._cc(EMITTER_2_GRAIN_PAN, grain_pan, channel))
        if grain_tune_spread is not None:
            result.extend(Tempera._cc(EMITTER_2_GRAIN_TUNE_SPREAD, grain_tune_spread, channel))
        if octave is not None:
            result.extend(Tempera._cc(EMITTER_2_OCTAVE, octave, channel))
        if relative_x is not None:
            result.extend(Tempera._cc(EMITTER_2_RELATIVE_X, relative_x, channel))
        if relative_y is not None:
            result.extend(Tempera._cc(EMITTER_2_RELATIVE_Y, relative_y, channel))
        if spray_x is not None:
            result.extend(Tempera._cc(EMITTER_2_SPRAY_X, spray_x, channel))
        if spray_y is not None:
            result.extend(Tempera._cc(EMITTER_2_SPRAY_Y, spray_y, channel))
        if tone_filter_width is not None:
            result.extend(Tempera._cc(EMITTER_2_TONE_FILTER_WIDTH, tone_filter_width, channel))
        if tone_filter_center is not None:
            result.extend(Tempera._cc(EMITTER_2_TONE_FILTER_CENTER, tone_filter_center, channel))
        if effects_send is not None:
            result.extend(Tempera._cc(EMITTER_2_EFFECTS_SEND, effects_send, channel))
        return bytes(result)

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
        result = bytearray()
        if volume is not None:
            result.extend(Tempera._cc(EMITTER_3_VOLUME, volume, channel))
        if grain_length_cell is not None:
            result.extend(Tempera._cc(EMITTER_3_GRAIN_LENGTH_CELL, grain_length_cell, channel))
        if grain_length_note is not None:
            result.extend(Tempera._cc(EMITTER_3_GRAIN_LENGTH_NOTE, grain_length_note, channel))
        if grain_density is not None:
            result.extend(Tempera._cc(EMITTER_3_GRAIN_DENSITY, grain_density, channel))
        if grain_shape is not None:
            result.extend(Tempera._cc(EMITTER_3_GRAIN_SHAPE, grain_shape, channel))
        if grain_shape_attack is not None:
            result.extend(Tempera._cc(EMITTER_3_GRAIN_SHAPE_ATTACK, grain_shape_attack, channel))
        if grain_pan is not None:
            result.extend(Tempera._cc(EMITTER_3_GRAIN_PAN, grain_pan, channel))
        if grain_tune_spread is not None:
            result.extend(Tempera._cc(EMITTER_3_GRAIN_TUNE_SPREAD, grain_tune_spread, channel))
        if octave is not None:
            result.extend(Tempera._cc(EMITTER_3_OCTAVE, octave, channel))
        if relative_x is not None:
            result.extend(Tempera._cc(EMITTER_3_RELATIVE_X, relative_x, channel))
        if relative_y is not None:
            result.extend(Tempera._cc(EMITTER_3_RELATIVE_Y, relative_y, channel))
        if spray_x is not None:
            result.extend(Tempera._cc(EMITTER_3_SPRAY_X, spray_x, channel))
        if spray_y is not None:
            result.extend(Tempera._cc(EMITTER_3_SPRAY_Y, spray_y, channel))
        if tone_filter_width is not None:
            result.extend(Tempera._cc(EMITTER_3_TONE_FILTER_WIDTH, tone_filter_width, channel))
        if tone_filter_center is not None:
            result.extend(Tempera._cc(EMITTER_3_TONE_FILTER_CENTER, tone_filter_center, channel))
        if effects_send is not None:
            result.extend(Tempera._cc(EMITTER_3_EFFECTS_SEND, effects_send, channel))
        return bytes(result)

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
        result = bytearray()
        if volume is not None:
            result.extend(Tempera._cc(EMITTER_4_VOLUME, volume, channel))
        if grain_length_cell is not None:
            result.extend(Tempera._cc(EMITTER_4_GRAIN_LENGTH_CELL, grain_length_cell, channel))
        if grain_length_note is not None:
            result.extend(Tempera._cc(EMITTER_4_GRAIN_LENGTH_NOTE, grain_length_note, channel))
        if grain_density is not None:
            result.extend(Tempera._cc(EMITTER_4_GRAIN_DENSITY, grain_density, channel))
        if grain_shape is not None:
            result.extend(Tempera._cc(EMITTER_4_GRAIN_SHAPE, grain_shape, channel))
        if grain_shape_attack is not None:
            result.extend(Tempera._cc(EMITTER_4_GRAIN_SHAPE_ATTACK, grain_shape_attack, channel))
        if grain_pan is not None:
            result.extend(Tempera._cc(EMITTER_4_GRAIN_PAN, grain_pan, channel))
        if grain_tune_spread is not None:
            result.extend(Tempera._cc(EMITTER_4_GRAIN_TUNE_SPREAD, grain_tune_spread, channel))
        if octave is not None:
            result.extend(Tempera._cc(EMITTER_4_OCTAVE, octave, channel))
        if relative_x is not None:
            result.extend(Tempera._cc(EMITTER_4_RELATIVE_X, relative_x, channel))
        if relative_y is not None:
            result.extend(Tempera._cc(EMITTER_4_RELATIVE_Y, relative_y, channel))
        if spray_x is not None:
            result.extend(Tempera._cc(EMITTER_4_SPRAY_X, spray_x, channel))
        if spray_y is not None:
            result.extend(Tempera._cc(EMITTER_4_SPRAY_Y, spray_y, channel))
        if tone_filter_width is not None:
            result.extend(Tempera._cc(EMITTER_4_TONE_FILTER_WIDTH, tone_filter_width, channel))
        if tone_filter_center is not None:
            result.extend(Tempera._cc(EMITTER_4_TONE_FILTER_CENTER, tone_filter_center, channel))
        if effects_send is not None:
            result.extend(Tempera._cc(EMITTER_4_EFFECTS_SEND, effects_send, channel))
        return bytes(result)