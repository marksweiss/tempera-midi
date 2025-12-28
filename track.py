from constants import (
    TRACK_1_VOLUME, TRACK_2_VOLUME, TRACK_3_VOLUME, TRACK_4_VOLUME,
    TRACK_5_VOLUME, TRACK_6_VOLUME, TRACK_7_VOLUME, TRACK_8_VOLUME,
)
from utils import build_messages, note_on, note_off

TRACK_VOLUME_CC_MAP = {
    'track_1_volume': TRACK_1_VOLUME,
    'track_2_volume': TRACK_2_VOLUME,
    'track_3_volume': TRACK_3_VOLUME,
    'track_4_volume': TRACK_4_VOLUME,
    'track_5_volume': TRACK_5_VOLUME,
    'track_6_volume': TRACK_6_VOLUME,
    'track_7_volume': TRACK_7_VOLUME,
    'track_8_volume': TRACK_8_VOLUME,
}


class Track:
    """
    Controls for an individual Tempera track (column).

    Args:
        track: Track number (1-8).
        midi_channel: MIDI channel (1-16). Default is 1.
    """

    def __init__(self, track: int = 1, midi_channel: int = 1):
        if track < 1 or track > 8:
            raise ValueError(f"track must be in range 1..8, got {track}")
        self.track_num = track
        self.midi_channel = midi_channel

    """
    Change Track Volume
    """
    def volume(self, value: int) -> bytes:
        return build_messages({f'track_{self.track_num}_volume': value},
                              TRACK_VOLUME_CC_MAP, self.midi_channel)

    """
    Set Recording on for Track. Recording starts when audio threshold set in Settings is reached.
    """
    def record_on(self) -> bytes:
        note = 100 + (self.track_num - 1)
        return note_on(note, 127, self.midi_channel)
