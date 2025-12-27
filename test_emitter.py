import unittest
from emitter import Emitter
from midi_constants import (
    EMITTER_1_VOLUME, EMITTER_1_GRAIN_DENSITY, EMITTER_1_GRAIN_PAN,
    EMITTER_1_OCTAVE, EMITTER_1_RELATIVE_X, EMITTER_1_RELATIVE_Y,
    EMITTER_1_SPRAY_X, EMITTER_1_SPRAY_Y,
    EMITTER_1_TONE_FILTER_WIDTH, EMITTER_1_TONE_FILTER_CENTER,
    EMITTER_1_EFFECTS_SEND,
    EMITTER_2_VOLUME, EMITTER_2_GRAIN_PAN,
    EMITTER_3_VOLUME, EMITTER_3_SPRAY_X,
    EMITTER_4_VOLUME, EMITTER_4_EFFECTS_SEND,
)


def _cc_bytes(cc: int, value: int, channel: int = 1) -> bytes:
    """Helper to create expected CC message bytes."""
    return bytes([0xB0 | (channel & 0x0F), cc & 0x7F, value & 0x7F])


class TestEmitter(unittest.TestCase):

    def setUp(self):
        # Default instance uses emitter 1, channel 1
        self.emitter = Emitter()

    # Test default values
    def test_default_emitter_is_1(self):
        self.assertEqual(self.emitter.emitter_num, 1)

    def test_default_channel_is_1(self):
        self.assertEqual(self.emitter.channel, 1)

    def test_custom_emitter(self):
        emitter = Emitter(emitter=3)
        self.assertEqual(emitter.emitter_num, 3)

    def test_custom_channel(self):
        emitter = Emitter(channel=5)
        self.assertEqual(emitter.channel, 5)

    def test_custom_emitter_and_channel(self):
        emitter = Emitter(emitter=2, channel=10)
        self.assertEqual(emitter.emitter_num, 2)
        self.assertEqual(emitter.channel, 10)

    # Test emitter validation in constructor
    def test_emitter_0_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            Emitter(emitter=0)
        self.assertIn("1..4", str(ctx.exception))

    def test_emitter_5_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            Emitter(emitter=5)
        self.assertIn("1..4", str(ctx.exception))

    def test_emitter_negative_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            Emitter(emitter=-1)
        self.assertIn("1..4", str(ctx.exception))

    # Test volume()
    def test_volume_emitter_1(self):
        result = self.emitter.volume(100)
        expected = _cc_bytes(EMITTER_1_VOLUME, 100)
        self.assertEqual(result, expected)

    def test_volume_emitter_2(self):
        emitter = Emitter(emitter=2)
        result = emitter.volume(80)
        expected = _cc_bytes(EMITTER_2_VOLUME, 80)
        self.assertEqual(result, expected)

    def test_volume_emitter_3(self):
        emitter = Emitter(emitter=3)
        result = emitter.volume(60)
        expected = _cc_bytes(EMITTER_3_VOLUME, 60)
        self.assertEqual(result, expected)

    def test_volume_emitter_4(self):
        emitter = Emitter(emitter=4)
        result = emitter.volume(40)
        expected = _cc_bytes(EMITTER_4_VOLUME, 40)
        self.assertEqual(result, expected)

    def test_volume_with_channel(self):
        emitter = Emitter(emitter=1, channel=15)
        result = emitter.volume(127)
        expected = _cc_bytes(EMITTER_1_VOLUME, 127, channel=15)
        self.assertEqual(result, expected)

    # Test grain()
    def test_grain_density(self):
        result = self.emitter.grain(density=64)
        expected = _cc_bytes(EMITTER_1_GRAIN_DENSITY, 64)
        self.assertEqual(result, expected)

    def test_grain_pan(self):
        result = self.emitter.grain(pan=32)
        expected = _cc_bytes(EMITTER_1_GRAIN_PAN, 32)
        self.assertEqual(result, expected)

    def test_grain_multiple_params(self):
        result = self.emitter.grain(density=50, pan=64)
        expected = (
            _cc_bytes(EMITTER_1_GRAIN_DENSITY, 50) +
            _cc_bytes(EMITTER_1_GRAIN_PAN, 64)
        )
        self.assertEqual(result, expected)

    def test_grain_no_args_returns_empty(self):
        result = self.emitter.grain()
        self.assertEqual(result, b'')

    def test_grain_emitter_2(self):
        emitter = Emitter(emitter=2)
        result = emitter.grain(pan=64)
        expected = _cc_bytes(EMITTER_2_GRAIN_PAN, 64)
        self.assertEqual(result, expected)

    # Test octave()
    def test_octave(self):
        result = self.emitter.octave(64)
        expected = _cc_bytes(EMITTER_1_OCTAVE, 64)
        self.assertEqual(result, expected)

    # Test relative()
    def test_relative_x(self):
        result = self.emitter.relative(x=100)
        expected = _cc_bytes(EMITTER_1_RELATIVE_X, 100)
        self.assertEqual(result, expected)

    def test_relative_y(self):
        result = self.emitter.relative(y=50)
        expected = _cc_bytes(EMITTER_1_RELATIVE_Y, 50)
        self.assertEqual(result, expected)

    def test_relative_both(self):
        result = self.emitter.relative(x=100, y=50)
        expected = (
            _cc_bytes(EMITTER_1_RELATIVE_X, 100) +
            _cc_bytes(EMITTER_1_RELATIVE_Y, 50)
        )
        self.assertEqual(result, expected)

    def test_relative_no_args_returns_empty(self):
        result = self.emitter.relative()
        self.assertEqual(result, b'')

    # Test spray()
    def test_spray_x(self):
        result = self.emitter.spray(x=32)
        expected = _cc_bytes(EMITTER_1_SPRAY_X, 32)
        self.assertEqual(result, expected)

    def test_spray_y(self):
        result = self.emitter.spray(y=64)
        expected = _cc_bytes(EMITTER_1_SPRAY_Y, 64)
        self.assertEqual(result, expected)

    def test_spray_both(self):
        result = self.emitter.spray(x=32, y=64)
        expected = (
            _cc_bytes(EMITTER_1_SPRAY_X, 32) +
            _cc_bytes(EMITTER_1_SPRAY_Y, 64)
        )
        self.assertEqual(result, expected)

    def test_spray_no_args_returns_empty(self):
        result = self.emitter.spray()
        self.assertEqual(result, b'')

    def test_spray_emitter_3(self):
        emitter = Emitter(emitter=3)
        result = emitter.spray(x=32)
        expected = _cc_bytes(EMITTER_3_SPRAY_X, 32)
        self.assertEqual(result, expected)

    # Test tone_filter()
    def test_tone_filter_width(self):
        result = self.emitter.tone_filter(width=80)
        expected = _cc_bytes(EMITTER_1_TONE_FILTER_WIDTH, 80)
        self.assertEqual(result, expected)

    def test_tone_filter_center(self):
        result = self.emitter.tone_filter(center=64)
        expected = _cc_bytes(EMITTER_1_TONE_FILTER_CENTER, 64)
        self.assertEqual(result, expected)

    def test_tone_filter_both(self):
        result = self.emitter.tone_filter(width=80, center=64)
        expected = (
            _cc_bytes(EMITTER_1_TONE_FILTER_WIDTH, 80) +
            _cc_bytes(EMITTER_1_TONE_FILTER_CENTER, 64)
        )
        self.assertEqual(result, expected)

    def test_tone_filter_no_args_returns_empty(self):
        result = self.emitter.tone_filter()
        self.assertEqual(result, b'')

    # Test effects_send()
    def test_effects_send(self):
        result = self.emitter.effects_send(100)
        expected = _cc_bytes(EMITTER_1_EFFECTS_SEND, 100)
        self.assertEqual(result, expected)

    def test_effects_send_emitter_4(self):
        emitter = Emitter(emitter=4)
        result = emitter.effects_send(100)
        expected = _cc_bytes(EMITTER_4_EFFECTS_SEND, 100)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
