import unittest
from tempera_global import TemperaGlobal
from midi_constants import (
    ADSR_ATTACK, ADSR_DECAY, ADSR_SUSTAIN, ADSR_RELEASE,
    REVERB_SIZE, REVERB_COLOR, REVERB_MIX,
    DELAY_FEEDBACK, DELAY_TIME, DELAY_COLOR, DELAY_MIX,
    CHORUS_DEPTH, CHORUS_SPEED, CHORUS_FLANGE, CHORUS_MIX,
    TRACK_1_VOLUME, TRACK_2_VOLUME, TRACK_3_VOLUME, TRACK_4_VOLUME,
    TRACK_5_VOLUME, TRACK_6_VOLUME, TRACK_7_VOLUME, TRACK_8_VOLUME,
)


def _cc_bytes(cc: int, value: int, channel: int = 1) -> bytes:
    """Helper to create expected CC message bytes."""
    return bytes([0xB0 | (channel & 0x0F), cc & 0x7F, value & 0x7F])


class TestTemperaGlobal(unittest.TestCase):

    def setUp(self):
        # Default instance uses channel 1
        self.tempera = TemperaGlobal()

    # Test default channel
    def test_default_channel_is_1(self):
        self.assertEqual(self.tempera.channel, 1)

    def test_custom_channel(self):
        tempera = TemperaGlobal(channel=5)
        self.assertEqual(tempera.channel, 5)

    # Test empty calls return empty bytes
    def test_adsr_no_args_returns_empty(self):
        self.assertEqual(self.tempera.adsr(), b'')

    def test_reverb_no_args_returns_empty(self):
        self.assertEqual(self.tempera.reverb(), b'')

    def test_delay_no_args_returns_empty(self):
        self.assertEqual(self.tempera.delay(), b'')

    def test_chorus_no_args_returns_empty(self):
        self.assertEqual(self.tempera.chorus(), b'')

    def test_track_volume_no_args_returns_empty(self):
        self.assertEqual(self.tempera.track_volume(), b'')

    # Test ADSR
    def test_adsr_attack(self):
        result = self.tempera.adsr(attack=64)
        expected = _cc_bytes(ADSR_ATTACK, 64)
        self.assertEqual(result, expected)

    def test_adsr_decay(self):
        result = self.tempera.adsr(decay=100)
        expected = _cc_bytes(ADSR_DECAY, 100)
        self.assertEqual(result, expected)

    def test_adsr_sustain(self):
        result = self.tempera.adsr(sustain=80)
        expected = _cc_bytes(ADSR_SUSTAIN, 80)
        self.assertEqual(result, expected)

    def test_adsr_release(self):
        result = self.tempera.adsr(release=50)
        expected = _cc_bytes(ADSR_RELEASE, 50)
        self.assertEqual(result, expected)

    def test_adsr_multiple_params(self):
        result = self.tempera.adsr(attack=10, decay=20, sustain=30, release=40)
        expected = (
            _cc_bytes(ADSR_ATTACK, 10) +
            _cc_bytes(ADSR_DECAY, 20) +
            _cc_bytes(ADSR_SUSTAIN, 30) +
            _cc_bytes(ADSR_RELEASE, 40)
        )
        self.assertEqual(result, expected)

    # Test Reverb
    def test_reverb_size(self):
        result = self.tempera.reverb(size=127)
        expected = _cc_bytes(REVERB_SIZE, 127)
        self.assertEqual(result, expected)

    def test_reverb_color(self):
        result = self.tempera.reverb(color=64)
        expected = _cc_bytes(REVERB_COLOR, 64)
        self.assertEqual(result, expected)

    def test_reverb_mix(self):
        result = self.tempera.reverb(mix=32)
        expected = _cc_bytes(REVERB_MIX, 32)
        self.assertEqual(result, expected)

    def test_reverb_multiple_params(self):
        result = self.tempera.reverb(size=100, color=50, mix=25)
        expected = (
            _cc_bytes(REVERB_SIZE, 100) +
            _cc_bytes(REVERB_COLOR, 50) +
            _cc_bytes(REVERB_MIX, 25)
        )
        self.assertEqual(result, expected)

    # Test Delay
    def test_delay_feedback(self):
        result = self.tempera.delay(feedback=60)
        expected = _cc_bytes(DELAY_FEEDBACK, 60)
        self.assertEqual(result, expected)

    def test_delay_time(self):
        result = self.tempera.delay(time=80)
        expected = _cc_bytes(DELAY_TIME, 80)
        self.assertEqual(result, expected)

    def test_delay_color(self):
        result = self.tempera.delay(color=40)
        expected = _cc_bytes(DELAY_COLOR, 40)
        self.assertEqual(result, expected)

    def test_delay_mix(self):
        result = self.tempera.delay(mix=90)
        expected = _cc_bytes(DELAY_MIX, 90)
        self.assertEqual(result, expected)

    def test_delay_multiple_params(self):
        result = self.tempera.delay(feedback=10, time=20, color=30, mix=40)
        expected = (
            _cc_bytes(DELAY_FEEDBACK, 10) +
            _cc_bytes(DELAY_TIME, 20) +
            _cc_bytes(DELAY_COLOR, 30) +
            _cc_bytes(DELAY_MIX, 40)
        )
        self.assertEqual(result, expected)

    # Test Chorus
    def test_chorus_depth(self):
        result = self.tempera.chorus(depth=70)
        expected = _cc_bytes(CHORUS_DEPTH, 70)
        self.assertEqual(result, expected)

    def test_chorus_speed(self):
        result = self.tempera.chorus(speed=45)
        expected = _cc_bytes(CHORUS_SPEED, 45)
        self.assertEqual(result, expected)

    def test_chorus_flange(self):
        result = self.tempera.chorus(flange=55)
        expected = _cc_bytes(CHORUS_FLANGE, 55)
        self.assertEqual(result, expected)

    def test_chorus_mix(self):
        result = self.tempera.chorus(mix=65)
        expected = _cc_bytes(CHORUS_MIX, 65)
        self.assertEqual(result, expected)

    def test_chorus_multiple_params(self):
        result = self.tempera.chorus(depth=10, speed=20, flange=30, mix=40)
        expected = (
            _cc_bytes(CHORUS_DEPTH, 10) +
            _cc_bytes(CHORUS_SPEED, 20) +
            _cc_bytes(CHORUS_FLANGE, 30) +
            _cc_bytes(CHORUS_MIX, 40)
        )
        self.assertEqual(result, expected)

    # Test Track Volume
    def test_track_volume_track_1(self):
        result = self.tempera.track_volume(track_1=100)
        expected = _cc_bytes(TRACK_1_VOLUME, 100)
        self.assertEqual(result, expected)

    def test_track_volume_track_8(self):
        result = self.tempera.track_volume(track_8=50)
        expected = _cc_bytes(TRACK_8_VOLUME, 50)
        self.assertEqual(result, expected)

    def test_track_volume_multiple_tracks(self):
        result = self.tempera.track_volume(track_1=100, track_2=90, track_3=80, track_4=70)
        expected = (
            _cc_bytes(TRACK_1_VOLUME, 100) +
            _cc_bytes(TRACK_2_VOLUME, 90) +
            _cc_bytes(TRACK_3_VOLUME, 80) +
            _cc_bytes(TRACK_4_VOLUME, 70)
        )
        self.assertEqual(result, expected)

    # Test channel parameter via constructor
    def test_adsr_with_channel(self):
        tempera = TemperaGlobal(channel=5)
        result = tempera.adsr(attack=64)
        expected = _cc_bytes(ADSR_ATTACK, 64, channel=5)
        self.assertEqual(result, expected)

    def test_reverb_with_channel(self):
        tempera = TemperaGlobal(channel=10)
        result = tempera.reverb(size=100)
        expected = _cc_bytes(REVERB_SIZE, 100, channel=10)
        self.assertEqual(result, expected)

    # Test value clamping (values > 127 should be masked to 7 bits)
    def test_value_masked_to_7_bits(self):
        result = self.tempera.adsr(attack=200)  # 200 & 0x7F = 72
        expected = _cc_bytes(ADSR_ATTACK, 200)  # _cc_bytes also masks
        self.assertEqual(result, expected)
        self.assertEqual(result[2], 200 & 0x7F)

    # Test channel clamping (channel > 15 should be masked to 4 bits)
    def test_channel_masked_to_4_bits(self):
        tempera = TemperaGlobal(channel=20)  # 20 & 0x0F = 4
        result = tempera.adsr(attack=64)
        self.assertEqual(result[0], 0xB0 | (20 & 0x0F))

    # Test change_canvas (Program Change)
    def test_change_canvas(self):
        result = self.tempera.change_canvas(1)
        expected = bytes([0xC0 | 1, 1])  # PC status + channel 1, program 1
        self.assertEqual(result, expected)

    def test_change_canvas_different_program(self):
        result = self.tempera.change_canvas(64)
        expected = bytes([0xC0 | 1, 64])
        self.assertEqual(result, expected)

    def test_change_canvas_max_program(self):
        result = self.tempera.change_canvas(127)
        expected = bytes([0xC0 | 1, 127])
        self.assertEqual(result, expected)

    def test_change_canvas_with_channel(self):
        tempera = TemperaGlobal(channel=10)
        result = tempera.change_canvas(42)
        expected = bytes([0xC0 | 10, 42])
        self.assertEqual(result, expected)

    def test_change_canvas_program_masked_to_7_bits(self):
        result = self.tempera.change_canvas(200)  # 200 & 0x7F = 72
        self.assertEqual(result[1], 200 & 0x7F)

    # Test clock, start, stop (MIDI real-time messages - static methods)
    def test_clock(self):
        result = TemperaGlobal.clock()
        self.assertEqual(result, bytes([0xF8]))

    def test_start(self):
        result = TemperaGlobal.start()
        self.assertEqual(result, bytes([0xFA]))

    def test_stop(self):
        result = TemperaGlobal.stop()
        self.assertEqual(result, bytes([0xFC]))


if __name__ == '__main__':
    unittest.main()
