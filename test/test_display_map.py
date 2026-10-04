"""Tests for CC -> Tempera display value mapping."""
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from tempera.display_map import (
    DisplayMap, SteppedDisplayMap, load_display_maps, save_display_maps, get_display_map,
    DISPLAY_MAPS, SAMPLED_PARAMS, STEPPED_PARAMS, LINEAR_PARAMS, GRAIN_LENGTH_NOTE_LABELS,
)
from tools.sample_cc import SAMPLEABLE_PARAMS, sweep_values


class TestDisplayMap(unittest.TestCase):

    def setUp(self):
        self.map = DisplayMap(points=((64, 1.0), (0, 0.0), (127, 8.0)), decimals=4)

    def test_points_are_sorted(self):
        self.assertEqual(self.map.points, ((0, 0.0), (64, 1.0), (127, 8.0)))

    def test_exact_breakpoints(self):
        self.assertEqual(self.map.value(0), 0.0)
        self.assertEqual(self.map.value(64), 1.0)
        self.assertEqual(self.map.value(127), 8.0)

    def test_interpolates_between_breakpoints(self):
        self.assertAlmostEqual(self.map.value(32), 0.5)
        self.assertAlmostEqual(self.map.value(64 + 63 / 2), 4.5)

    def test_clamps_outside_sampled_range(self):
        partial = DisplayMap(points=((16, 0.5), (112, 60.0)))
        self.assertEqual(partial.value(0), 0.5)
        self.assertEqual(partial.value(127), 60.0)

    def test_single_point(self):
        self.assertEqual(DisplayMap(points=((64, 3.0),)).value(10), 3.0)

    def test_format(self):
        self.assertEqual(self.map.format(32), '0.5000')
        self.assertEqual(DisplayMap(points=((0, 0), (127, 100)), decimals=0, unit='%').format(127), '100%')

    def test_rejects_invalid_points(self):
        with self.assertRaises(ValueError):
            DisplayMap(points=())
        with self.assertRaises(ValueError):
            DisplayMap(points=((10, 1.0), (10, 2.0)))
        with self.assertRaises(ValueError):
            DisplayMap(points=((0, 0.0), (128, 1.0)))

    def test_save_load_round_trip(self):
        maps = {
            'b': self.map,
            'a': DisplayMap(points=((0, 1), (127, 2)), decimals=1, unit='ms'),
        }
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'maps.json'
            save_display_maps(maps, path)
            self.assertEqual(load_display_maps(path), maps)

    def test_load_missing_file_returns_empty(self):
        self.assertEqual(load_display_maps(Path('/nonexistent/maps.json')), {})


class TestSteppedDisplayMap(unittest.TestCase):

    def setUp(self):
        self.map = SteppedDisplayMap(steps=((7, '8/1'), (0, '16/1'), (14, '4/1')))

    def test_steps_are_sorted(self):
        self.assertEqual(self.map.steps[0], (0, '16/1'))

    def test_label_covers_range_up_to_next_step(self):
        self.assertEqual(self.map.format(0), '16/1')
        self.assertEqual(self.map.format(6), '16/1')
        self.assertEqual(self.map.format(7), '8/1')
        self.assertEqual(self.map.format(13), '8/1')
        self.assertEqual(self.map.format(14), '4/1')
        self.assertEqual(self.map.format(127), '4/1')

    def test_below_first_step_shows_first_label(self):
        self.assertEqual(SteppedDisplayMap(steps=((5, '1/4'),)).format(0), '1/4')

    def test_evenly_divided_spans_full_cc_range(self):
        m = SteppedDisplayMap.evenly_divided(('a', 'b', 'c', 'd'))
        self.assertEqual(m.steps, ((0, 'a'), (32, 'b'), (64, 'c'), (96, 'd')))
        self.assertEqual(m.format(31), 'a')
        self.assertEqual(m.format(127), 'd')

    def test_grain_length_note_intervals_evenly_divided(self):
        m = get_display_map('grain_length_note')
        self.assertEqual([label for _, label in m.steps], list(GRAIN_LENGTH_NOTE_LABELS))
        self.assertEqual(m.format(0), '16/1')
        self.assertEqual(m.format(127), '1/64')
        # 20 labels over 128 CC values: every step is 6 or 7 CC wide
        starts = [cc for cc, _ in m.steps] + [128]
        widths = [b - a for a, b in zip(starts, starts[1:])]
        self.assertEqual(set(widths), {6, 7})

    def test_rejects_invalid_steps(self):
        with self.assertRaises(ValueError):
            SteppedDisplayMap(steps=())
        with self.assertRaises(ValueError):
            SteppedDisplayMap(steps=((3, '1/4'), (3, '1/8')))


class TestShippedDisplayMaps(unittest.TestCase):

    def test_grain_length_cell_matches_documented_samples(self):
        m = DISPLAY_MAPS['grain_length_cell']
        for cc, expected in [(16, 0.2222), (64, 0.8889), (80, 2.0), (96, 4.0), (112, 6.0), (127, 8.0)]:
            self.assertAlmostEqual(m.value(cc), expected, places=4)

    def test_shipped_keys_are_sampled_params(self):
        self.assertLessEqual(set(DISPLAY_MAPS), set(SAMPLED_PARAMS))


class TestGetDisplayMap(unittest.TestCase):

    def test_sampled_param_uses_breakpoints(self):
        self.assertIs(get_display_map('grain_length_cell'), DISPLAY_MAPS['grain_length_cell'])

    def test_sampled_param_without_data_shows_raw_cc(self):
        unsampled = [p for p in SAMPLED_PARAMS if p not in DISPLAY_MAPS]
        for param in unsampled:
            self.assertIsNone(get_display_map(param))

    def test_linear_params_scale_zero_to_one(self):
        for param in LINEAR_PARAMS:
            m = get_display_map(param)
            self.assertEqual(m.format(0), '0.00')
            self.assertEqual(m.format(127), '1.00')
            self.assertAlmostEqual(m.value(64), 64 / 127)

    def test_param_kinds_do_not_overlap(self):
        sampled, stepped, linear = set(SAMPLED_PARAMS), set(STEPPED_PARAMS), set(LINEAR_PARAMS)
        self.assertFalse(sampled & stepped or sampled & linear or stepped & linear)

    def test_other_params_have_no_map(self):
        for key in ('volume', 'octave', 'reverb_size', None):
            self.assertIsNone(get_display_map(key))


class TestSampleCcTool(unittest.TestCase):

    def test_sweep_always_includes_ends(self):
        self.assertEqual(sweep_values(8)[:3], [0, 8, 16])
        self.assertEqual(sweep_values(8)[-1], 127)
        self.assertEqual(len(sweep_values(8)), 17)
        self.assertEqual(sweep_values(127), [0, 127])

    def test_only_sampled_params_are_sampleable(self):
        self.assertEqual(set(SAMPLEABLE_PARAMS), set(SAMPLED_PARAMS))

    def test_gui_display_keys_have_known_mappings(self):
        from gui.widgets.emitter_panel import BASIC_PARAMS, GRAIN_PARAMS, POSITION_PARAMS, FILTER_PARAMS
        keys = {p['display'] for p in BASIC_PARAMS + GRAIN_PARAMS + POSITION_PARAMS + FILTER_PARAMS if 'display' in p}
        self.assertEqual(keys, set(SAMPLED_PARAMS) | set(STEPPED_PARAMS) | set(LINEAR_PARAMS))


class TestLabeledSliderDisplay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_mapped_slider_shows_display_value_and_cc_tooltip(self):
        from gui.widgets.labeled_slider import LabeledSlider
        slider = LabeledSlider('Length', initial_value=64, display_map=DISPLAY_MAPS['grain_length_cell'])
        self.assertEqual(slider._value_label.text(), '0.8889')
        self.assertEqual(slider._value_label.toolTip(), 'CC 64')
        slider.setValue(127)
        self.assertEqual(slider._value_label.text(), '8.0000')
        self.assertEqual(slider.value(), 127)

    def test_stepped_slider_shows_label(self):
        from gui.widgets.labeled_slider import LabeledSlider
        steps = SteppedDisplayMap(steps=((0, '16/1'), (64, '1/4')))
        slider = LabeledSlider('Length Note', initial_value=10, display_map=steps)
        self.assertEqual(slider._value_label.text(), '16/1')
        slider.adjust_value(60)
        self.assertEqual(slider._value_label.text(), '1/4')
        self.assertEqual(slider._value_label.toolTip(), 'CC 70')

    def test_unmapped_slider_shows_raw_cc(self):
        from gui.widgets.labeled_slider import LabeledSlider
        slider = LabeledSlider('Volume', initial_value=100)
        self.assertEqual(slider._value_label.text(), '100')
        slider.adjust_value(5)
        self.assertEqual(slider._value_label.text(), '105')


if __name__ == '__main__':
    unittest.main()
