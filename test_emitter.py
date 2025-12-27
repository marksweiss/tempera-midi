import unittest
from emitter import Emitter
from midi_constants import (
    EMITTER_1_VOLUME, EMITTER_1_GRAIN_DENSITY, EMITTER_1_OCTAVE,
    EMITTER_2_VOLUME, EMITTER_2_GRAIN_PAN,
    EMITTER_3_VOLUME, EMITTER_3_SPRAY_X,
    EMITTER_4_VOLUME, EMITTER_4_EFFECTS_SEND,
)


def _cc_bytes(cc: int, value: int, channel: int = 1) -> bytes:
    """Helper to create expected CC message bytes."""
    return bytes([0xB0 | (channel & 0x0F), cc & 0x7F, value & 0x7F])


class TestEmitter(unittest.TestCase):

    def setUp(self):
        # Default instance uses channel 1
        self.emitter = Emitter()

    # Test default channel
    def test_default_channel_is_1(self):
        self.assertEqual(self.emitter.channel, 1)

    def test_custom_channel(self):
        emitter = Emitter(channel=5)
        self.assertEqual(emitter.channel, 5)

    # Test empty calls return empty bytes
    def test_emitter_1_no_args_returns_empty(self):
        self.assertEqual(self.emitter.emitter(1), b'')

    def test_emitter_2_no_args_returns_empty(self):
        self.assertEqual(self.emitter.emitter(2), b'')

    def test_emitter_3_no_args_returns_empty(self):
        self.assertEqual(self.emitter.emitter(3), b'')

    def test_emitter_4_no_args_returns_empty(self):
        self.assertEqual(self.emitter.emitter(4), b'')

    # Test Emitter 1
    def test_emitter_1_volume(self):
        result = self.emitter.emitter(1, volume=100)
        expected = _cc_bytes(EMITTER_1_VOLUME, 100)
        self.assertEqual(result, expected)

    def test_emitter_1_grain_density(self):
        result = self.emitter.emitter(1, grain_density=64)
        expected = _cc_bytes(EMITTER_1_GRAIN_DENSITY, 64)
        self.assertEqual(result, expected)

    def test_emitter_1_octave(self):
        result = self.emitter.emitter(1, octave=64)
        expected = _cc_bytes(EMITTER_1_OCTAVE, 64)
        self.assertEqual(result, expected)

    def test_emitter_1_multiple_params(self):
        result = self.emitter.emitter(1, volume=100, grain_density=50, octave=64)
        expected = (
            _cc_bytes(EMITTER_1_VOLUME, 100) +
            _cc_bytes(EMITTER_1_GRAIN_DENSITY, 50) +
            _cc_bytes(EMITTER_1_OCTAVE, 64)
        )
        self.assertEqual(result, expected)

    # Test Emitter 2
    def test_emitter_2_volume(self):
        result = self.emitter.emitter(2, volume=80)
        expected = _cc_bytes(EMITTER_2_VOLUME, 80)
        self.assertEqual(result, expected)

    def test_emitter_2_grain_pan(self):
        result = self.emitter.emitter(2, grain_pan=64)
        expected = _cc_bytes(EMITTER_2_GRAIN_PAN, 64)
        self.assertEqual(result, expected)

    # Test Emitter 3
    def test_emitter_3_volume(self):
        result = self.emitter.emitter(3, volume=60)
        expected = _cc_bytes(EMITTER_3_VOLUME, 60)
        self.assertEqual(result, expected)

    def test_emitter_3_spray_x(self):
        result = self.emitter.emitter(3, spray_x=32)
        expected = _cc_bytes(EMITTER_3_SPRAY_X, 32)
        self.assertEqual(result, expected)

    # Test Emitter 4
    def test_emitter_4_volume(self):
        result = self.emitter.emitter(4, volume=40)
        expected = _cc_bytes(EMITTER_4_VOLUME, 40)
        self.assertEqual(result, expected)

    def test_emitter_4_effects_send(self):
        result = self.emitter.emitter(4, effects_send=100)
        expected = _cc_bytes(EMITTER_4_EFFECTS_SEND, 100)
        self.assertEqual(result, expected)

    # Test channel parameter via constructor
    def test_emitter_1_with_channel(self):
        emitter = Emitter(channel=15)
        result = emitter.emitter(1, volume=127)
        expected = _cc_bytes(EMITTER_1_VOLUME, 127, channel=15)
        self.assertEqual(result, expected)

    # Test emitter validation
    def test_emitter_0_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.emitter.emitter(0, volume=100)
        self.assertIn("1..4", str(ctx.exception))

    def test_emitter_5_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.emitter.emitter(5, volume=100)
        self.assertIn("1..4", str(ctx.exception))

    def test_emitter_negative_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.emitter.emitter(-1, volume=100)
        self.assertIn("1..4", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
