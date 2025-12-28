import unittest
from track import Track
from constants import (
    TRACK_1_VOLUME, TRACK_2_VOLUME, TRACK_3_VOLUME, TRACK_4_VOLUME,
    TRACK_5_VOLUME, TRACK_6_VOLUME, TRACK_7_VOLUME, TRACK_8_VOLUME,
)
from utils import cc

CHANNEL = 1


class TestTrack(unittest.TestCase):

    def setUp(self):
        # Default instance uses track 1, channel 1
        self.track = Track()

    # Test default values
    def test_default_track_is_1(self):
        self.assertEqual(self.track.track_num, 1)

    def test_default_channel_is_1(self):
        self.assertEqual(self.track.midi_channel, 1)

    def test_custom_track(self):
        track = Track(track=5)
        self.assertEqual(track.track_num, 5)

    def test_custom_channel(self):
        track = Track(midi_channel=10)
        self.assertEqual(track.midi_channel, 10)

    def test_custom_track_and_channel(self):
        track = Track(track=3, midi_channel=8)
        self.assertEqual(track.track_num, 3)
        self.assertEqual(track.midi_channel, 8)

    # Test track validation in constructor
    def test_track_0_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            Track(track=0)
        self.assertIn("1..8", str(ctx.exception))

    def test_track_9_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            Track(track=9)
        self.assertIn("1..8", str(ctx.exception))

    def test_track_negative_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            Track(track=-1)
        self.assertIn("1..8", str(ctx.exception))

    # Test volume()
    def test_volume_track_1(self):
        track = Track(track=1)
        result = track.volume(100)
        expected = cc(TRACK_1_VOLUME, 100, CHANNEL)
        self.assertEqual(result, expected)

    def test_volume_track_2(self):
        track = Track(track=2)
        result = track.volume(90)
        expected = cc(TRACK_2_VOLUME, 90, CHANNEL)
        self.assertEqual(result, expected)

    def test_volume_track_3(self):
        track = Track(track=3)
        result = track.volume(80)
        expected = cc(TRACK_3_VOLUME, 80, CHANNEL)
        self.assertEqual(result, expected)

    def test_volume_track_4(self):
        track = Track(track=4)
        result = track.volume(70)
        expected = cc(TRACK_4_VOLUME, 70, CHANNEL)
        self.assertEqual(result, expected)

    def test_volume_track_5(self):
        track = Track(track=5)
        result = track.volume(60)
        expected = cc(TRACK_5_VOLUME, 60, CHANNEL)
        self.assertEqual(result, expected)

    def test_volume_track_6(self):
        track = Track(track=6)
        result = track.volume(50)
        expected = cc(TRACK_6_VOLUME, 50, CHANNEL)
        self.assertEqual(result, expected)

    def test_volume_track_7(self):
        track = Track(track=7)
        result = track.volume(40)
        expected = cc(TRACK_7_VOLUME, 40, CHANNEL)
        self.assertEqual(result, expected)

    def test_volume_track_8(self):
        track = Track(track=8)
        result = track.volume(30)
        expected = cc(TRACK_8_VOLUME, 30, CHANNEL)
        self.assertEqual(result, expected)

    def test_volume_with_channel(self):
        track = Track(track=1, midi_channel=15)
        result = track.volume(127)
        expected = cc(TRACK_1_VOLUME, 127, channel=15)
        self.assertEqual(result, expected)

    # Test record_on()
    def test_record_on_track_1(self):
        track = Track(track=1)
        result = track.record_on()
        expected = bytes([0x90 | CHANNEL, 100, 127])  # note = 100 + (1-1) = 100
        self.assertEqual(result, expected)

    def test_record_on_track_2(self):
        track = Track(track=2)
        result = track.record_on()
        expected = bytes([0x90 | CHANNEL, 101, 127])  # note = 100 + (2-1) = 101
        self.assertEqual(result, expected)

    def test_record_on_track_8(self):
        track = Track(track=8)
        result = track.record_on()
        expected = bytes([0x90 | CHANNEL, 107, 127])  # note = 100 + (8-1) = 107
        self.assertEqual(result, expected)

    def test_record_on_with_channel(self):
        track = Track(track=1, midi_channel=5)
        result = track.record_on()
        expected = bytes([0x90 | 5, 100, 127])
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
