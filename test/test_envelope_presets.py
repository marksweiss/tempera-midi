"""Tests for envelope presets and their MIDI value application."""
import unittest
from gui.envelope.envelope import Envelope
from gui.envelope.envelope_presets import EnvelopePreset, generate_preset_points
from gui.envelope.envelope_manager import EnvelopeManager


class TestEnvelopePresets(unittest.TestCase):
    """Tests for preset point generation."""

    def test_ramp_up_generates_correct_points(self):
        """Ramp up should go from 0 to 1."""
        points = generate_preset_points(EnvelopePreset.RAMP_UP, per_cell=False)
        self.assertEqual(len(points), 2)
        self.assertEqual(points[0], (0.0, 0.0))
        self.assertEqual(points[1], (1.0, 1.0))

    def test_ramp_down_generates_correct_points(self):
        """Ramp down should go from 1 to 0."""
        points = generate_preset_points(EnvelopePreset.RAMP_DOWN, per_cell=False)
        self.assertEqual(len(points), 2)
        self.assertEqual(points[0], (0.0, 1.0))
        self.assertEqual(points[1], (1.0, 0.0))

    def test_triangle_generates_correct_points(self):
        """Triangle should go up then down."""
        points = generate_preset_points(EnvelopePreset.TRIANGLE, per_cell=False)
        self.assertEqual(len(points), 3)
        self.assertEqual(points[0], (0.0, 0.0))
        self.assertEqual(points[1], (0.5, 1.0))
        self.assertEqual(points[2], (1.0, 0.0))

    def test_s_curve_generates_correct_points(self):
        """S-curve should have smooth sigmoid shape."""
        points = generate_preset_points(EnvelopePreset.S_CURVE, per_cell=False)
        self.assertEqual(len(points), 5)
        self.assertEqual(points[0], (0.0, 0.0))
        self.assertEqual(points[2], (0.5, 0.5))
        self.assertEqual(points[4], (1.0, 1.0))

    def test_square_generates_correct_points(self):
        """Square should hold at 1 then drop to 0."""
        points = generate_preset_points(EnvelopePreset.SQUARE, per_cell=False)
        self.assertEqual(len(points), 4)
        # First half at 1.0
        self.assertEqual(points[0][1], 1.0)
        self.assertEqual(points[1][1], 1.0)
        # Second half at 0.0
        self.assertEqual(points[2][1], 0.0)
        self.assertEqual(points[3][1], 0.0)

    def test_sawtooth_generates_correct_points(self):
        """Sawtooth should ramp up then drop."""
        points = generate_preset_points(EnvelopePreset.SAWTOOTH, per_cell=False)
        self.assertEqual(len(points), 4)
        self.assertEqual(points[0], (0.0, 0.0))
        self.assertEqual(points[1][1], 1.0)  # Peak
        self.assertEqual(points[2][1], 0.0)  # Drop

    def test_per_cell_repeats_8_times(self):
        """Per cell mode should repeat pattern 8 times."""
        points = generate_preset_points(EnvelopePreset.RAMP_UP, per_cell=True)
        # RAMP_UP has 2 base points, repeated 8 times = 16 points
        self.assertEqual(len(points), 16)
        # First cell starts at 0.0
        self.assertAlmostEqual(points[0][0], 0.0)
        # Last cell ends at 1.0
        self.assertAlmostEqual(points[-1][0], 1.0)

    def test_per_cell_preserves_pattern_shape(self):
        """Each cell repetition should have the same shape."""
        points = generate_preset_points(EnvelopePreset.RAMP_UP, per_cell=True)
        # Check that each cell starts at 0 and ends at 1 (in value)
        for cell in range(8):
            cell_start_idx = cell * 2
            cell_end_idx = cell_start_idx + 1
            # Start of cell should be at 0 value
            self.assertAlmostEqual(points[cell_start_idx][1], 0.0)
            # End of cell should be at 1 value
            self.assertAlmostEqual(points[cell_end_idx][1], 1.0)

    def test_triangle_midpoint(self):
        """Triangle should peak at midpoint."""
        points = generate_preset_points(EnvelopePreset.TRIANGLE, per_cell=False)
        # Should peak at midpoint
        mid = [p for p in points if abs(p[0] - 0.5) < 0.01]
        self.assertEqual(len(mid), 1)
        self.assertEqual(mid[0][1], 1.0)


class TestEnvelopeMIDIApplication(unittest.TestCase):
    """Tests for applying presets to MIDI values."""

    def setUp(self):
        self.manager = EnvelopeManager(bpm=120)

    def test_ramp_up_at_start_is_zero(self):
        """Ramp up at position 0 should give value 0."""
        envelope = Envelope(enabled=True)
        for time, value in generate_preset_points(EnvelopePreset.RAMP_UP):
            envelope.add_point(time, value)

        # At position 0, value should be 0
        value = envelope.get_value_at(0.0)
        self.assertAlmostEqual(value, 0.0)

    def test_ramp_up_at_end_is_full(self):
        """Ramp up at position 1 should give value 1."""
        envelope = Envelope(enabled=True)
        for time, value in generate_preset_points(EnvelopePreset.RAMP_UP):
            envelope.add_point(time, value)

        # At position 1, value should be 1
        value = envelope.get_value_at(1.0)
        self.assertAlmostEqual(value, 1.0)

    def test_ramp_up_midi_modulation(self):
        """Ramp up should correctly modulate MIDI value."""
        envelope = Envelope(enabled=True)
        for time, value in generate_preset_points(EnvelopePreset.RAMP_UP):
            envelope.add_point(time, value)

        base_value = 100
        # At position 0.5, ramp up should be at 50%
        self.manager._position = 0.5
        result = self.manager.apply_envelope_to_value(base_value, envelope)
        self.assertEqual(result, 50)  # 100 * 0.5 = 50

    def test_ramp_down_midi_modulation(self):
        """Ramp down should correctly modulate MIDI value."""
        envelope = Envelope(enabled=True)
        for time, value in generate_preset_points(EnvelopePreset.RAMP_DOWN):
            envelope.add_point(time, value)

        base_value = 100
        # At position 0, ramp down should be at 100%
        self.manager._position = 0.0
        result = self.manager.apply_envelope_to_value(base_value, envelope)
        self.assertEqual(result, 100)

        # At position 1.0, ramp down should be at 0%
        self.manager._position = 1.0
        result = self.manager.apply_envelope_to_value(base_value, envelope)
        self.assertEqual(result, 0)

    def test_square_holds_then_drops(self):
        """Square should hold at 1 for first half then drop to 0."""
        envelope = Envelope(enabled=True)
        for time, value in generate_preset_points(EnvelopePreset.SQUARE):
            envelope.add_point(time, value)

        # First half should be full
        self.assertAlmostEqual(envelope.get_value_at(0.25), 1.0)
        # Second half should be zero
        self.assertAlmostEqual(envelope.get_value_at(0.75), 0.0)

    def test_triangle_peak_at_midpoint(self):
        """Triangle should peak at midpoint."""
        envelope = Envelope(enabled=True)
        for time, value in generate_preset_points(EnvelopePreset.TRIANGLE):
            envelope.add_point(time, value)

        # Start should be zero
        self.assertAlmostEqual(envelope.get_value_at(0.0), 0.0)
        # Midpoint should be full
        self.assertAlmostEqual(envelope.get_value_at(0.5), 1.0)
        # End should be zero
        self.assertAlmostEqual(envelope.get_value_at(1.0), 0.0)

    def test_per_cell_applies_8_times(self):
        """Per-cell mode should apply pattern 8 times."""
        envelope = Envelope(enabled=True)
        for time, value in generate_preset_points(EnvelopePreset.RAMP_UP, per_cell=True):
            envelope.add_point(time, value)

        # Each cell should ramp from 0 to 1
        # At 0.0625 (midpoint of first cell = 0.5 * 0.125), should be ~0.5
        value = envelope.get_value_at(0.0625)
        self.assertAlmostEqual(value, 0.5, places=1)

        # At 0.1875 (midpoint of second cell = 0.125 + 0.5 * 0.125), should also be ~0.5
        value = envelope.get_value_at(0.1875)
        self.assertAlmostEqual(value, 0.5, places=1)

    def test_disabled_envelope_returns_base_value(self):
        """Disabled envelope should not modulate value."""
        envelope = Envelope(enabled=False)
        for time, value in generate_preset_points(EnvelopePreset.RAMP_UP):
            envelope.add_point(time, value)

        base_value = 100
        self.manager._position = 0.0  # Would normally return 0 with ramp up
        result = self.manager.apply_envelope_to_value(base_value, envelope)
        self.assertEqual(result, 100)  # Should return base value unchanged


if __name__ == '__main__':
    unittest.main()
