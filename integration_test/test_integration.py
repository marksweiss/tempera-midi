import os
import time
import unittest
import mido

from tempera_global import TemperaGlobal
from emitter import Emitter
from track import Track


# Environment variable to enable hardware tests
RUN_HARDWARE_TESTS = os.environ.get('RUN_HARDWARE_TESTS')

# Expected Tempera MIDI port name (adjust if different on your system)
TEMPERA_PORT_NAME = os.environ.get('TEMPERA_PORT_NAME', 'Tempera')


class MidiIntegrationTestBase(unittest.TestCase):
    """Base class for MIDI integration tests with virtual port setup."""

    output = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.output = mido.open_output('TemperaMidi Test', virtual=True)
        except Exception as e:
            raise unittest.SkipTest(f"Virtual MIDI ports not available: {e}")

    @classmethod
    def tearDownClass(cls):
        if cls.output:
            cls.output.close()

    def parse_and_send(self, raw_bytes):
        """Parse raw bytes and send as MIDI messages via mido."""
        if not raw_bytes:
            return []
        parser = mido.Parser()
        parser.feed(raw_bytes)
        messages = list(parser)
        for msg in messages:
            self.output.send(msg)
        return messages


class TestTemperaGlobalIntegration(MidiIntegrationTestBase):
    """Integration tests for TemperaGlobal class."""

    def setUp(self):
        self.tempera = TemperaGlobal()

    def test_modwheel(self):
        raw_bytes = self.tempera.modwheel(modwheel=64)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')
        self.assertEqual(messages[0].value, 64)

    def test_adsr_attack(self):
        raw_bytes = self.tempera.adsr(attack=100)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')
        self.assertEqual(messages[0].value, 100)

    def test_adsr_all_params(self):
        raw_bytes = self.tempera.adsr(attack=64, decay=50, sustain=80, release=30)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 4)
        for msg in messages:
            self.assertEqual(msg.type, 'control_change')

    def test_reverb_size(self):
        raw_bytes = self.tempera.reverb(size=100)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_reverb_all_params(self):
        raw_bytes = self.tempera.reverb(size=100, color=64, mix=80)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 3)

    def test_delay_feedback(self):
        raw_bytes = self.tempera.delay(feedback=50)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_delay_all_params(self):
        raw_bytes = self.tempera.delay(feedback=50, time=64, color=100, mix=60)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 4)

    def test_chorus_depth(self):
        raw_bytes = self.tempera.chorus(depth=64)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_chorus_all_params(self):
        raw_bytes = self.tempera.chorus(depth=64, speed=50, flange=30, mix=70)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 4)

    def test_change_canvas(self):
        raw_bytes = self.tempera.change_canvas(program=3)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'program_change')
        self.assertEqual(messages[0].program, 3)

    def test_clock(self):
        raw_bytes = TemperaGlobal.clock()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'clock')

    def test_start(self):
        raw_bytes = TemperaGlobal.start()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'start')

    def test_stop(self):
        raw_bytes = TemperaGlobal.stop()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'stop')

    def test_with_custom_channel(self):
        tempera = TemperaGlobal(midi_channel=5)
        raw_bytes = tempera.modwheel(modwheel=100)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].channel, 5)


class TestEmitterIntegration(MidiIntegrationTestBase):
    """Integration tests for Emitter class."""

    def setUp(self):
        self.emitter = Emitter(emitter=1)

    def test_volume(self):
        raw_bytes = self.emitter.volume(100)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')
        self.assertEqual(messages[0].value, 100)

    def test_octave(self):
        raw_bytes = self.emitter.octave(64)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_grain_density(self):
        raw_bytes = self.emitter.grain(density=50)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_grain_multiple_params(self):
        raw_bytes = self.emitter.grain(density=50, length_cell=64, shape=80)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 3)
        for msg in messages:
            self.assertEqual(msg.type, 'control_change')

    def test_relative_position_both(self):
        raw_bytes = self.emitter.relative_position(x=64, y=64)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 2)

    def test_spray_both(self):
        raw_bytes = self.emitter.spray(x=30, y=30)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 2)

    def test_tone_filter_both(self):
        raw_bytes = self.emitter.tone_filter(width=64, center=64)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 2)

    def test_effects_send(self):
        raw_bytes = self.emitter.effects_send(80)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_set_active(self):
        raw_bytes = self.emitter.set_active()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_place_in_cell(self):
        raw_bytes = self.emitter.place_in_cell(column=1, cell=1)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_remove_from_cell(self):
        raw_bytes = self.emitter.remove_from_cell(column=1, cell=1)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_emitter_2(self):
        emitter = Emitter(emitter=2)
        raw_bytes = emitter.volume(100)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_emitter_3(self):
        emitter = Emitter(emitter=3)
        raw_bytes = emitter.volume(100)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)

    def test_emitter_4(self):
        emitter = Emitter(emitter=4)
        raw_bytes = emitter.volume(100)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)

    def test_with_custom_channel(self):
        emitter = Emitter(emitter=1, midi_channel=10)
        raw_bytes = emitter.volume(100)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].channel, 10)


class TestTrackIntegration(MidiIntegrationTestBase):
    """Integration tests for Track class."""

    def setUp(self):
        self.track = Track(track=1)

    def test_volume(self):
        raw_bytes = self.track.volume(100)
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')
        self.assertEqual(messages[0].value, 100)

    def test_record_on(self):
        raw_bytes = self.track.record_on()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'note_on')
        self.assertEqual(messages[0].note, 100)
        self.assertEqual(messages[0].velocity, 127)

    def test_track_2(self):
        track = Track(track=2)
        raw_bytes = track.record_on()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].note, 101)

    def test_track_3(self):
        track = Track(track=3)
        raw_bytes = track.record_on()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(messages[0].note, 102)

    def test_track_4(self):
        track = Track(track=4)
        raw_bytes = track.record_on()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(messages[0].note, 103)

    def test_track_5(self):
        track = Track(track=5)
        raw_bytes = track.record_on()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(messages[0].note, 104)

    def test_track_6(self):
        track = Track(track=6)
        raw_bytes = track.record_on()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(messages[0].note, 105)

    def test_track_7(self):
        track = Track(track=7)
        raw_bytes = track.record_on()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(messages[0].note, 106)

    def test_track_8(self):
        track = Track(track=8)
        raw_bytes = track.record_on()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(messages[0].note, 107)

    def test_with_custom_channel(self):
        track = Track(track=1, midi_channel=15)
        raw_bytes = track.record_on()
        messages = self.parse_and_send(raw_bytes)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].channel, 15)


def find_tempera_port():
    """Find a MIDI output port matching the Tempera name."""
    output_names = mido.get_output_names()
    for name in output_names:
        if TEMPERA_PORT_NAME.lower() in name.lower():
            return name
    return None


@unittest.skipUnless(RUN_HARDWARE_TESTS, "Hardware tests require RUN_HARDWARE_TESTS=1 and connected Tempera")
class MidiHardwareTestBase(unittest.TestCase):
    """
    Base class for hardware MIDI tests that send to a real Tempera device.

    To run these tests:
        RUN_HARDWARE_TESTS=1 uv run python -m unittest discover integration_test -v

    If your Tempera shows up with a different port name, set:
        TEMPERA_PORT_NAME="Your Tempera Port Name"
    """

    output = None
    tempera_port_name = None

    @classmethod
    def setUpClass(cls):
        cls.tempera_port_name = find_tempera_port()
        if not cls.tempera_port_name:
            available = mido.get_output_names()
            raise unittest.SkipTest(
                f"Tempera not found. Available ports: {available}. "
                f"Set TEMPERA_PORT_NAME env var if using different name."
            )
        try:
            cls.output = mido.open_output(cls.tempera_port_name)
        except Exception as e:
            raise unittest.SkipTest(f"Could not open Tempera port: {e}")

    @classmethod
    def tearDownClass(cls):
        if cls.output:
            cls.output.close()

    def parse_and_send(self, raw_bytes):
        """Parse raw bytes and send as MIDI messages to Tempera."""
        if not raw_bytes:
            return []
        parser = mido.Parser()
        parser.feed(raw_bytes)
        messages = list(parser)
        for msg in messages:
            self.output.send(msg)
        return messages

    def send_with_delay(self, raw_bytes, delay=0.05):
        """Send messages with a small delay for hardware to process."""
        messages = self.parse_and_send(raw_bytes)
        time.sleep(delay)
        return messages


@unittest.skipUnless(RUN_HARDWARE_TESTS, "Hardware tests require RUN_HARDWARE_TESTS=1 and connected Tempera")
class TestTemperaGlobalHardware(MidiHardwareTestBase):
    """Hardware tests for TemperaGlobal - sends real MIDI to connected Tempera."""

    def setUp(self):
        self.tempera = TemperaGlobal()

    def test_modwheel(self):
        messages = self.send_with_delay(self.tempera.modwheel(modwheel=64))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_adsr_attack(self):
        messages = self.send_with_delay(self.tempera.adsr(attack=100))
        self.assertEqual(len(messages), 1)

    def test_adsr_all_params(self):
        messages = self.send_with_delay(
            self.tempera.adsr(attack=64, decay=50, sustain=80, release=30)
        )
        self.assertEqual(len(messages), 4)

    def test_reverb_size(self):
        messages = self.send_with_delay(self.tempera.reverb(size=100))
        self.assertEqual(len(messages), 1)

    def test_reverb_all_params(self):
        messages = self.send_with_delay(
            self.tempera.reverb(size=100, color=64, mix=80)
        )
        self.assertEqual(len(messages), 3)

    def test_delay_feedback(self):
        messages = self.send_with_delay(self.tempera.delay(feedback=50))
        self.assertEqual(len(messages), 1)

    def test_delay_all_params(self):
        messages = self.send_with_delay(
            self.tempera.delay(feedback=50, time=64, color=100, mix=60)
        )
        self.assertEqual(len(messages), 4)

    def test_chorus_depth(self):
        messages = self.send_with_delay(self.tempera.chorus(depth=64))
        self.assertEqual(len(messages), 1)

    def test_chorus_all_params(self):
        messages = self.send_with_delay(
            self.tempera.chorus(depth=64, speed=50, flange=30, mix=70)
        )
        self.assertEqual(len(messages), 4)

    def test_change_canvas(self):
        messages = self.send_with_delay(self.tempera.change_canvas(program=0))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'program_change')

    def test_clock(self):
        messages = self.send_with_delay(TemperaGlobal.clock())
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'clock')

    def test_start(self):
        messages = self.send_with_delay(TemperaGlobal.start())
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'start')

    def test_stop(self):
        messages = self.send_with_delay(TemperaGlobal.stop())
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'stop')


@unittest.skipUnless(RUN_HARDWARE_TESTS, "Hardware tests require RUN_HARDWARE_TESTS=1 and connected Tempera")
class TestEmitterHardware(MidiHardwareTestBase):
    """Hardware tests for Emitter - sends real MIDI to connected Tempera."""

    def setUp(self):
        self.emitter = Emitter(emitter=1)

    def test_volume(self):
        messages = self.send_with_delay(self.emitter.volume(100))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_octave(self):
        messages = self.send_with_delay(self.emitter.octave(64))
        self.assertEqual(len(messages), 1)

    def test_grain_density(self):
        messages = self.send_with_delay(self.emitter.grain(density=50))
        self.assertEqual(len(messages), 1)

    def test_grain_multiple_params(self):
        messages = self.send_with_delay(
            self.emitter.grain(density=50, length_cell=64, shape=80)
        )
        self.assertEqual(len(messages), 3)

    def test_relative_position_both(self):
        messages = self.send_with_delay(self.emitter.relative_position(x=64, y=64))
        self.assertEqual(len(messages), 2)

    def test_spray_both(self):
        messages = self.send_with_delay(self.emitter.spray(x=30, y=30))
        self.assertEqual(len(messages), 2)

    def test_tone_filter_both(self):
        messages = self.send_with_delay(self.emitter.tone_filter(width=64, center=64))
        self.assertEqual(len(messages), 2)

    def test_effects_send(self):
        messages = self.send_with_delay(self.emitter.effects_send(80))
        self.assertEqual(len(messages), 1)

    def test_set_active(self):
        messages = self.send_with_delay(self.emitter.set_active())
        self.assertEqual(len(messages), 1)

    def test_place_in_cell(self):
        messages = self.send_with_delay(self.emitter.place_in_cell(column=1, cell=1))
        self.assertEqual(len(messages), 1)

    def test_remove_from_cell(self):
        messages = self.send_with_delay(self.emitter.remove_from_cell(column=1, cell=1))
        self.assertEqual(len(messages), 1)

    def test_emitter_2(self):
        emitter = Emitter(emitter=2)
        messages = self.send_with_delay(emitter.volume(100))
        self.assertEqual(len(messages), 1)

    def test_emitter_3(self):
        emitter = Emitter(emitter=3)
        messages = self.send_with_delay(emitter.volume(100))
        self.assertEqual(len(messages), 1)

    def test_emitter_4(self):
        emitter = Emitter(emitter=4)
        messages = self.send_with_delay(emitter.volume(100))
        self.assertEqual(len(messages), 1)


@unittest.skipUnless(RUN_HARDWARE_TESTS, "Hardware tests require RUN_HARDWARE_TESTS=1 and connected Tempera")
class TestTrackHardware(MidiHardwareTestBase):
    """Hardware tests for Track - sends real MIDI to connected Tempera."""

    def setUp(self):
        self.track = Track(track=1)

    def test_volume(self):
        messages = self.send_with_delay(self.track.volume(100))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'control_change')

    def test_record_on(self):
        messages = self.send_with_delay(self.track.record_on())
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].type, 'note_on')

    def test_track_2(self):
        track = Track(track=2)
        messages = self.send_with_delay(track.volume(100))
        self.assertEqual(len(messages), 1)

    def test_track_3(self):
        track = Track(track=3)
        messages = self.send_with_delay(track.volume(100))
        self.assertEqual(len(messages), 1)

    def test_track_4(self):
        track = Track(track=4)
        messages = self.send_with_delay(track.volume(100))
        self.assertEqual(len(messages), 1)

    def test_track_5(self):
        track = Track(track=5)
        messages = self.send_with_delay(track.volume(100))
        self.assertEqual(len(messages), 1)

    def test_track_6(self):
        track = Track(track=6)
        messages = self.send_with_delay(track.volume(100))
        self.assertEqual(len(messages), 1)

    def test_track_7(self):
        track = Track(track=7)
        messages = self.send_with_delay(track.volume(100))
        self.assertEqual(len(messages), 1)

    def test_track_8(self):
        track = Track(track=8)
        messages = self.send_with_delay(track.volume(100))
        self.assertEqual(len(messages), 1)


if __name__ == '__main__':
    unittest.main()
