import os
import mido
from mido import Message

from constants import TEMPERA_PORT_NAME

NOTE_ON = 'note_on'
NOTE_OFF = 'note_off'
CONTROL_CHANGE = 'control_change'
PROGRAM_CHANGE = 'program_change'
CLOCK = 'clock'
START = 'start'
STOP = 'stop'


class Midi:
    def __init__(self, midi_channel=1, port=None):
        self.midi_channel = midi_channel
        self.tempera_port = os.environ.get(TEMPERA_PORT_NAME)

    # TODO DO WE NEED THIS?
    #  DO WE NEED SLEEP AND TIMING SEMANTICS?
    def send(self, message: Message):
        with mido.open_output(self.tempera_port, virtual=True) as output:
            output.send(message)

    def note_on(self, note: int, velocity: int, time: int = 0) -> Message:
        """
        Create a MIDI Note On message.

        Args:
            note: Note number (0-127)
            velocity: Note velocity (0-127)
            time: Time in ticks (default 0), 480 ticks = 1 quarter note at current tempo

        Returns:
            3-byte MIDI Note On message
        """
        return mido.Message(NOTE_ON, note=note, velocity=velocity, time=time, channel=self.midi_channel - 1)

    def note_off(self, note: int, time: int = 0) -> Message:
        """
        Create a MIDI Note Off message.

        Args:
            note: Note number (0-127)
            time: Time in ticks (default 0), 480 ticks = 1 quarter note at current tempo

        Returns:
            3-byte MIDI Note Off message
        """
        return mido.Message(NOTE_OFF, note=note, velocity=0, time=time, channel=self.midi_channel - 1)

    def cc(self, cc_num: int, value: int) -> Message:
        """
        Create a MIDI Control Change message.

        Args:
            cc_num: CC number (0-127)
            value: CC value (0-127)

        Returns:
            3-byte MIDI CC message
        """
        return mido.Message(CONTROL_CHANGE, channel=self.midi_channel - 1, control=cc_num, value=value)

    def all_ccs(self, params: dict, cc_map: dict) -> list[Message]:
        """
        Build multiple MIDI CC messages from a parameter dictionary.

        Args:
            params: Dictionary mapping parameter names to values
            cc_map: Dictionary mapping parameter names to CC numbers

        Returns:
            Concatenated MIDI CC messages
        """
        messages = []
        for name, value in params.items():
            messages.append(self.cc(cc_map[name], value))
        return messages

    def program_change(self, program: int) -> Message:
        """
        Create a MIDI Program Change message.

        Args:
            program: Program number (0-127)

        Returns:
            2-byte MIDI Program Change message
        """
        return mido.Message('program_change', program=program, channel=self.midi_channel - 1)

    @staticmethod
    def clock() -> Message:
        """
        Create a MIDI Clock message.

        Returns:
            1-byte MIDI Clock message
        """
        return mido.Message(CLOCK)

    @staticmethod
    def start() -> Message:
        """
        Create a MIDI Start message.

        Returns:
            1-byte MIDI Start message
        """
        return mido.Message(START)

    @staticmethod
    def stop() -> Message:
        """
        Create a MIDI Stop message.

        Returns:
            1-byte MIDI Stop message
        """
        return mido.Message(STOP)
