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
    def __init__(self, track: int = 1, channel: int = 1):
        if track < 1 or track > 8:
            raise ValueError(f"track must be in range 1..8, got {track}")
        self.track_num = track
        self.channel = channel

    def volume(self, value: int) -> bytes:
        return build_messages({f'track_{self.track_num}_volume': value},
                              TRACK_VOLUME_CC_MAP, self.channel)

    def record_on(self) -> bytes:
        note = 100 + (self.track_num - 1)
        return note_on(note, 127, self.channel)

    def record_off(self) -> bytes:
        note = 100 + (self.track_num - 1)
        return note_off(note, 0, self.channel)
