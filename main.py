import asyncio
import os
from constants import TEMPERA_PORT_NAME
from emitter import Emitter
from midi import Midi
from mido import Message, open_output

from tempera_global import TemperaGlobal
from track import Track

INIT_SLEEP = .5
PORT = os.environ.get(TEMPERA_PORT_NAME)


async def play(messages: list[Message]):
    pass


# Integration test function. Run this from main
async def play_test(override_port: str = None):
    port = override_port or PORT
    with open_output(port) as output:
        # in the output context manager
        midi = Midi(midi_channel=1)
        await asyncio.sleep(INIT_SLEEP)

        # --- Midi class tests ---
        output.send(midi.note_on(60, 127, 0))
        print("calling Midi.note_on with arguments (60, 127, 0) just succeeded")
        await asyncio.sleep(1)

        output.send(midi.note_off(60, 480))
        print("calling Midi.note_off with arguments (60, 480) just succeeded")

        output.send(midi.cc(1, 64))
        print("calling Midi.cc with arguments (1, 64) just succeeded")

        output.send(midi.program_change(0))
        print("calling Midi.program_change with arguments (0) just succeeded")

        # --- Emitter class tests ---
        emitter = Emitter(emitter=1)

        output.send(emitter.set_active())
        print("calling Emitter.set_active with arguments () just succeeded")

        output.send(emitter.volume(100))
        print("calling Emitter.volume with arguments (100) just succeeded")

        for message in emitter.grain(length_cell=64, length_note=32, density=80, shape=50, shape_attack=40, pan=64, tune_spread=30):
            output.send(message)
        print("calling Emitter.grain with arguments (length_cell=64, length_note=32, density=80, shape=50, shape_attack=40, pan=64, tune_spread=30) just succeeded")

        output.send(emitter.octave(64))
        print("calling Emitter.octave with arguments (64) just succeeded")

        for message in emitter.relative_position(x=64, y=64):
            output.send(message)
        print("calling Emitter.relative_position with arguments (x=64, y=64) just succeeded")

        for message in emitter.spray(x=32, y=32):
            output.send(message)
        print("calling Emitter.spray with arguments (x=32, y=32) just succeeded")

        for message in emitter.tone_filter(width=80, center=64):
            output.send(message)
        print("calling Emitter.tone_filter with arguments (width=80, center=64) just succeeded")

        output.send(emitter.effects_send(50))
        print("calling Emitter.effects_send with arguments (50) just succeeded")

        output.send(emitter.place_in_cell(column=1, cell=1))
        print("calling Emitter.place_in_cell with arguments (column=1, cell=1) just succeeded")

        await asyncio.sleep(2)

        output.send(emitter.remove_from_cell(column=1, cell=1))
        print("calling Emitter.remove_from_cell with arguments (column=1, cell=1) just succeeded")

        output.send(emitter.place_in_cell(column=1, cell=1))
        print("calling Emitter.place_in_cell with arguments (column=1, cell=1) just succeeded")

        await asyncio.sleep(2)

        output.send(emitter.remove_from_cell(column=1, cell=1))
        print("calling Emitter.remove_from_cell with arguments (column=1, cell=1) just succeeded")

        # --- Track class tests ---
        track = Track(track=1)

        output.send(track.volume(100))
        print("calling Track.volume with arguments (100) just succeeded")

        output.send(track.record_on())
        print("calling Track.record_on with arguments () just succeeded")

        # --- TemperaGlobal class tests ---
        tempera = TemperaGlobal()

        output.send(tempera.modwheel(64))
        print("calling TemperaGlobal.modwheel with arguments (64) just succeeded")

        for message in tempera.adsr(attack=30, decay=40, sustain=100, release=50):
            output.send(message)
        print("calling TemperaGlobal.adsr with arguments (attack=30, decay=40, sustain=100, release=50) just succeeded")

        for message in tempera.reverb(size=60, color=70, mix=50):
            output.send(message)
        print("calling TemperaGlobal.reverb with arguments (size=60, color=70, mix=50) just succeeded")

        for message in tempera.delay(feedback=40, time=60, color=50, mix=30):
            output.send(message)
        print("calling TemperaGlobal.delay with arguments (feedback=40, time=60, color=50, mix=30) just succeeded")

        for message in tempera.chorus(depth=50, speed=40, flange=30, mix=60):
            output.send(message)
        print("calling TemperaGlobal.chorus with arguments (depth=50, speed=40, flange=30, mix=60) just succeeded")

        # output.send(tempera.change_canvas(0))
        # print("calling TemperaGlobal.change_canvas with arguments (0) just succeeded")

        output.send(TemperaGlobal.clock())
        print("calling TemperaGlobal.clock with arguments () just succeeded")

        output.send(TemperaGlobal.start())
        print("calling TemperaGlobal.start with arguments () just succeeded")

        output.send(TemperaGlobal.stop())
        print("calling TemperaGlobal.stop with arguments () just succeeded")

        print("\n=== All integration tests completed successfully ===")


if __name__ == '__main__':
    # Comment this out to skip running the lighgtweight integration test
    # pass an argumenbt for override_port or set env var TEMPERA_PORT to run against actual Tempera
    asyncio.run(play_test())

    # Define list of mido Messages here. This is the composition which will be sent to the Tempera.
    messages: list[Message] = []
    # Pass them to the play() function
    asyncio.run(play(messages))
