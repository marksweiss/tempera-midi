import asyncio
import os
from constants import TEMPERA_PORT_NAME
from emitter import Emitter
from midi import Midi
from mido import Message, open_output
from mido.backends.rtmidi import Output

from tempera_global import TemperaGlobal
from track import Track

INIT_SLEEP = .5
PORT = os.environ.get(TEMPERA_PORT_NAME)

async def play(messages: list[Message]):
    with open_output(PORT) as output:
        # Some exmaple code
        # Typical pattern is to have logic outside of this function in an event loop etc.
        # building lists of Messages, which are then just sent here to play
        # in the output context manager
        midi = Midi(midi_channel=1)
        await asyncio.sleep(INIT_SLEEP)

        output.send(midi.note_on(60, 127, 0))
        await asyncio.sleep(1)
        output.send(midi.note_off(60, 480))

        emitter = Emitter(emitter=1)
        output.send(emitter.set_active())
        for message in emitter.effects_send(0):
            output.send(message)

        track = Track(track=1)
        for message in track.volume(2):
            output.send(message)

        tempera = TemperaGlobal()
        for message in tempera.modwheel(3):
            output.send (message)
        for message in tempera.chorus(depth=4, speed=5):
            output.send(message)


if __name__ == '__main__':
    # Define list of mido Messages here. This is the composition which will be sent to the Tempera.
    messages: list[Message] = []

    # event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    asyncio.run(play(messages))
