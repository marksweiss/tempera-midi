"""Unit tests for the Envelope automation module."""

import unittest
from gui.envelope.envelope import Envelope, EnvelopePoint


class TestEnvelopePoint(unittest.TestCase):
    """Test EnvelopePoint dataclass."""

    def test_create_point(self):
        """Test creating an envelope point."""
        point = EnvelopePoint(time=0.5, value=0.75)
        self.assertEqual(point.time, 0.5)
        self.assertEqual(point.value, 0.75)

    def test_to_dict(self):
        """Test serialization to dict."""
        point = EnvelopePoint(time=0.25, value=0.5)
        d = point.to_dict()
        self.assertEqual(d, {'time': 0.25, 'value': 0.5})

    def test_from_dict(self):
        """Test deserialization from dict."""
        d = {'time': 0.75, 'value': 0.25}
        point = EnvelopePoint.from_dict(d)
        self.assertEqual(point.time, 0.75)
        self.assertEqual(point.value, 0.25)


class TestEnvelope(unittest.TestCase):
    """Test Envelope class."""

    def test_empty_envelope(self):
        """Test empty envelope returns 1.0 for all positions."""
        env = Envelope()
        self.assertTrue(env.is_empty())
        self.assertEqual(env.get_value_at(0.0), 1.0)
        self.assertEqual(env.get_value_at(0.5), 1.0)
        self.assertEqual(env.get_value_at(1.0), 1.0)

    def test_single_point(self):
        """Test envelope with single point."""
        env = Envelope()
        env.add_point(0.5, 0.5)
        self.assertFalse(env.is_empty())
        # Before point
        self.assertEqual(env.get_value_at(0.0), 0.5)
        # At point
        self.assertEqual(env.get_value_at(0.5), 0.5)
        # After point
        self.assertEqual(env.get_value_at(1.0), 0.5)

    def test_linear_interpolation(self):
        """Test linear interpolation between two points."""
        env = Envelope()
        env.add_point(0.0, 0.0)
        env.add_point(1.0, 1.0)

        self.assertEqual(env.get_value_at(0.0), 0.0)
        self.assertAlmostEqual(env.get_value_at(0.25), 0.25)
        self.assertAlmostEqual(env.get_value_at(0.5), 0.5)
        self.assertAlmostEqual(env.get_value_at(0.75), 0.75)
        self.assertEqual(env.get_value_at(1.0), 1.0)

    def test_multiple_segments(self):
        """Test envelope with multiple segments."""
        env = Envelope()
        env.add_point(0.0, 0.0)
        env.add_point(0.5, 1.0)
        env.add_point(1.0, 0.5)

        self.assertEqual(env.get_value_at(0.0), 0.0)
        self.assertAlmostEqual(env.get_value_at(0.25), 0.5)
        self.assertEqual(env.get_value_at(0.5), 1.0)
        self.assertAlmostEqual(env.get_value_at(0.75), 0.75)
        self.assertEqual(env.get_value_at(1.0), 0.5)

    def test_points_sorted_by_time(self):
        """Test that points are automatically sorted by time."""
        env = Envelope()
        env.add_point(1.0, 1.0)
        env.add_point(0.0, 0.0)
        env.add_point(0.5, 0.5)

        self.assertEqual(len(env.points), 3)
        self.assertEqual(env.points[0].time, 0.0)
        self.assertEqual(env.points[1].time, 0.5)
        self.assertEqual(env.points[2].time, 1.0)

    def test_values_clamped(self):
        """Test that values are clamped to 0.0-1.0."""
        env = Envelope()
        env.add_point(-0.5, -0.5)
        env.add_point(1.5, 1.5)

        self.assertEqual(env.points[0].time, 0.0)
        self.assertEqual(env.points[0].value, 0.0)
        self.assertEqual(env.points[1].time, 1.0)
        self.assertEqual(env.points[1].value, 1.0)

    def test_clear(self):
        """Test clearing envelope points."""
        env = Envelope()
        env.add_point(0.5, 0.5)
        env.clear()
        self.assertTrue(env.is_empty())

    def test_enabled_state(self):
        """Test enabled/disabled state."""
        env = Envelope()
        self.assertFalse(env.enabled)
        env.enabled = True
        self.assertTrue(env.enabled)

    def test_to_dict(self):
        """Test serialization to dict."""
        env = Envelope()
        env.add_point(0.0, 0.0)
        env.add_point(1.0, 1.0)
        env.enabled = True

        d = env.to_dict()
        self.assertEqual(len(d['points']), 2)
        self.assertTrue(d['enabled'])
        self.assertEqual(d['points'][0], {'time': 0.0, 'value': 0.0})

    def test_from_dict(self):
        """Test deserialization from dict."""
        d = {
            'points': [
                {'time': 0.0, 'value': 0.0},
                {'time': 1.0, 'value': 1.0}
            ],
            'enabled': True
        }
        env = Envelope.from_dict(d)
        self.assertEqual(len(env.points), 2)
        self.assertTrue(env.enabled)
        self.assertEqual(env.points[0].time, 0.0)
        self.assertEqual(env.points[1].time, 1.0)

    def test_copy(self):
        """Test deep copy of envelope."""
        env = Envelope()
        env.add_point(0.5, 0.5)
        env.enabled = True

        env_copy = env.copy()
        self.assertEqual(len(env_copy.points), 1)
        self.assertTrue(env_copy.enabled)

        # Modify original, copy should be unaffected
        env.add_point(1.0, 1.0)
        env.enabled = False
        self.assertEqual(len(env_copy.points), 1)
        self.assertTrue(env_copy.enabled)


class TestEnvelopeInterpolation(unittest.TestCase):
    """Test envelope interpolation for MIDI CC modulation."""

    def test_volume_ramp(self):
        """Test a volume ramp from 0 to 100%."""
        env = Envelope()
        env.add_point(0.0, 0.0)
        env.add_point(1.0, 1.0)
        env.enabled = True

        # Simulating base value of 100 (max MIDI CC)
        base_value = 100

        # At start: 100 * 0.0 = 0
        self.assertEqual(int(base_value * env.get_value_at(0.0)), 0)

        # At 50%: 100 * 0.5 = 50
        self.assertEqual(int(base_value * env.get_value_at(0.5)), 50)

        # At end: 100 * 1.0 = 100
        self.assertEqual(int(base_value * env.get_value_at(1.0)), 100)


if __name__ == '__main__':
    unittest.main()
