from constants import (
    ACTIVE_EMITTER, PLACE_EMITTER_IN_CELL, REMOVE_EMITTER_FROM_CELL,
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
from midi import Midi
from mido import Message

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

EMITTER_CC_MAPS = {
    1: EMITTER_1_CC_MAP,
    2: EMITTER_2_CC_MAP,
    3: EMITTER_3_CC_MAP,
    4: EMITTER_4_CC_MAP,
}

class Emitter:
    """
    Controls for an individual Tempera emitter.

    Args:
        emitter: Emitter number (1-4).
        midi_channel: MIDI channel (1-16). Default is 1.
    """

    def __init__(self, emitter: int = 1, midi_channel: int = 1):
        if emitter < 1 or emitter > 4:
            raise ValueError(f"emitter must be in range 1..4, got {emitter}")
        self._emitter_num = emitter
        self.cc_map = EMITTER_CC_MAPS[emitter]
        self.midi_channel = midi_channel
        self.midi = Midi(midi_channel)

    @property
    def emitter_num(self):
        return self._emitter_num

    @emitter_num.setter
    def emitter_num(self, value):
        self._emitter_num = value
        self.cc_map = EMITTER_CC_MAPS[value]

    def volume(self, value: int) -> Message:
        """Change Emitter Volume."""
        return self.midi.all_ccs({'volume': value}, self.cc_map)[0]

    def grain(
        self,
        *,
        length_cell: int = None,
        length_note: int = None,
        density: int = None,
        shape: int = None,
        shape_attack: int = None,
        pan: int = None,
        tune_spread: int = None
    ) -> list[Message]:
        """Change Emitter Grain Parameters."""
        params = {f'grain_{k}': v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, EMITTER_CC_MAPS[self.emitter_num])

    def octave(self, value: int) -> Message:
        """Change Emitter Octave."""
        return self.midi.all_ccs({'octave': value}, self.cc_map)[0]

    def relative_position(self, *, x: int = None, y: int = None) -> list[Message]:
        """Change Emitter Position along X and Y axes. Applies to a placement for the Emitter in a given Cell."""
        params = {f'relative_{k}': v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, self.cc_map)

    def spray(self, *, x: int = None, y: int = None) -> list[Message]:
        """Change Emitter Spray along X and Y axes. Applies to a placement for the Emitter in a given Cell."""
        params = {f'spray_{k}': v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, self.cc_map)

    def tone_filter(self, *, width: int = None, center: int = None) -> list[Message]:
        """Change Emitter Filter width and center."""
        params = {f'tone_filter_{k}': v for k, v in locals().items() if v is not None and k != 'self'}
        return self.midi.all_ccs(params, self.cc_map)

    def effects_send(self, value: int) -> Message:
        """Change Emitter Effects Send."""
        return self.midi.all_ccs({'effects_send': value}, self.cc_map)[0]

    def set_active(self) -> Message:
        """Set Emitter as Active."""
        return self.midi.cc(ACTIVE_EMITTER, self.emitter_num - 1)

    def place_in_cell(self, column: int, cell: int) -> Message:
        """Place Emitter in a given Cell in a given Column."""
        if column < 1 or column > 8:
            raise ValueError(f"column must be in range 1..8, got {column}")
        if cell < 1 or cell > 8:
            raise ValueError(f"cell must be in range 1..8, got {cell}")
        value = ((column - 1) * 8) + (cell - 1)
        return self.midi.cc(PLACE_EMITTER_IN_CELL, value)

    def remove_from_cell(self, column: int, cell: int) -> Message:
        """Remove Emitter placement in a given Cell in a given Column."""
        if column < 1 or column > 8:
            raise ValueError(f"column must be in range 1..8, got {column}")
        if cell < 1 or cell > 8:
            raise ValueError(f"cell must be in range 1..8, got {cell}")
        value = ((column - 1) * 8) + (cell - 1)
        return self.midi.cc(REMOVE_EMITTER_FROM_CELL, value)
