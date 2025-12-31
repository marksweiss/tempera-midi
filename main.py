import asyncio
import os
from constants import TEMPERA_PORT_NAME
from emitter import Emitter
from emitter_pool import EmitterPool
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


async def play_test_emitter_pool(override_port: str = None):
    """Test EmitterPool with all four emitters placing in different cells."""
    port = override_port or PORT

    async with EmitterPool(port_name=port) as pool:
        await asyncio.sleep(INIT_SLEEP)

        print("Testing EmitterPool with all 4 emitters...")

        # Set up all emitters with different parameters
        for emitter_num in range(1, 5):
            await pool.set_active(emitter_num)
            print(f"Emitter {emitter_num}: set_active")

            await pool.volume(emitter_num, 80 + emitter_num * 5)
            print(f"Emitter {emitter_num}: volume({80 + emitter_num * 5})")

            await pool.grain(
                emitter_num,
                length_cell=60 + emitter_num * 2,
                density=70 + emitter_num * 5,
                shape=40 + emitter_num * 10
            )
            print(f"Emitter {emitter_num}: grain settings applied")

            await pool.octave(emitter_num, 64)
            print(f"Emitter {emitter_num}: octave(64)")

            await pool.relative_position(emitter_num, x=64, y=64)
            print(f"Emitter {emitter_num}: relative_position(x=64, y=64)")

            await pool.spray(emitter_num, x=20 + emitter_num * 5, y=20 + emitter_num * 5)
            print(f"Emitter {emitter_num}: spray applied")

            await pool.tone_filter(emitter_num, width=80, center=64)
            print(f"Emitter {emitter_num}: tone_filter(width=80, center=64)")

            await pool.effects_send(emitter_num, 40 + emitter_num * 10)
            print(f"Emitter {emitter_num}: effects_send({40 + emitter_num * 10})")

        await asyncio.sleep(0.5)

        # Place each emitter in different cells using modulus 4
        # Cell indices 0-63 map to column 1-8, cell 1-8
        # Emitter 1: indices 0, 4, 8, 12 (mod 4 == 0)
        # Emitter 2: indices 1, 5, 9, 13 (mod 4 == 1)
        # Emitter 3: indices 2, 6, 10, 14 (mod 4 == 2)
        # Emitter 4: indices 3, 7, 11, 15 (mod 4 == 3)
        print("\nPlacing emitters in cells (each emitter in cells where index mod 4 matches emitter-1)...")

        placements = []  # Track placements for cleanup
        for flat_index in range(63):
            emitter_num = (flat_index % 4) + 1
            column = (flat_index // 8) + 1  # 1-8
            # Mod 7 to leave bottom row open for keyboard
            cell = (flat_index % 7) + 1     # 1-8

            await pool.set_active(emitter_num)
            await pool.place_in_cell(emitter_num, column=column, cell=cell)
            placements.append((emitter_num, column, cell))
            print(f"Emitter {emitter_num}: placed in column={column}, cell={cell}")
            # Sadly some delay necessary or messages are dropped and don't reach device
            await asyncio.sleep(.001)

        print("\nAll 4 emitters now have placements. Observe on hardware...")
        await asyncio.sleep(5)

        # Test dispatch method
        print("\nTesting dispatch method...")
        await pool.dispatch({'emitter': 1, 'method': 'volume', 'args': [100]})
        print("dispatch: Emitter 1 volume -> 100")

        await pool.dispatch({
            'emitter': 2,
            'method': 'grain',
            'kwargs': {'density': 100, 'shape': 80}
        })
        print("dispatch: Emitter 2 grain density=100, shape=80")

        await asyncio.sleep(2)

        # Cleanup - remove all placements
        print("\nRemoving all placements...")
        for emitter_num, column, cell in placements:
            await pool.set_active(emitter_num)
            await pool.remove_from_cell(emitter_num, column=column, cell=cell)
            print(f"Emitter {emitter_num}: removed from column={column}, cell={cell}")
            await asyncio.sleep(.001)

        await asyncio.sleep(0.5)
        print("\n=== EmitterPool integration test completed successfully ===")


if __name__ == '__main__':
    # Comment this out to skip running the lightweight integration test
    # pass an argument for override_port or set env var TEMPERA_PORT to run against actual Tempera
    # asyncio.run(play_test())

    # Uncomment to run the EmitterPool test (tests all 4 emitters with async pool)
    asyncio.run(play_test_emitter_pool())

    # Define list of mido Messages here. This is the composition which will be sent to the Tempera.
    messages: list[Message] = []
    # Pass them to the play() function
    asyncio.run(play(messages))
