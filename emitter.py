from midi_constants import (
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
from utils import build_messages

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


class Emitter:
    def __init__(self, channel: int = 1):
        self.channel = channel

    def emitter(
        self,
        emitter: int,
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
        effects_send: int = None
    ) -> bytes:
        if emitter < 1 or emitter > 4:
            raise ValueError(f"emitter must be in range 1..4, got {emitter}")
        method = getattr(self, f'_emitter_{emitter}')
        return method(
            volume=volume,
            grain_length_cell=grain_length_cell,
            grain_length_note=grain_length_note,
            grain_density=grain_density,
            grain_shape=grain_shape,
            grain_shape_attack=grain_shape_attack,
            grain_pan=grain_pan,
            grain_tune_spread=grain_tune_spread,
            octave=octave,
            relative_x=relative_x,
            relative_y=relative_y,
            spray_x=spray_x,
            spray_y=spray_y,
            tone_filter_width=tone_filter_width,
            tone_filter_center=tone_filter_center,
            effects_send=effects_send
        )

    def _emitter_1(
        self,
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
        effects_send: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, EMITTER_1_CC_MAP, self.channel)

    def _emitter_2(
        self,
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
        effects_send: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, EMITTER_2_CC_MAP, self.channel)

    def _emitter_3(
        self,
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
        effects_send: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, EMITTER_3_CC_MAP, self.channel)

    def _emitter_4(
        self,
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
        effects_send: int = None
    ) -> bytes:
        params = {k: v for k, v in locals().items() if v is not None and k != 'self'}
        return build_messages(params, EMITTER_4_CC_MAP, self.channel)
