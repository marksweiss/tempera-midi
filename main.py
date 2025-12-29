import asyncio
import os
from constants import TEMPERA_PORT_NAME
from midi import Midi
from mido import Message, open_output
from mido.backends.rtmidi import Output

INIT_SLEEP = .5

async def play(messages: list[Message]):
    with open_output(os.environ.get(TEMPERA_PORT_NAME), True) as output:
        midi = Midi(midi_channel=1)
        await asyncio.sleep(INIT_SLEEP)

        # output.send(Midi.start())
        # await asyncio.sleep(1)
        # output.send(Midi.stop())

        output.send(midi.note_on(60, 127, 0))
        # await asyncio.sleep(1)
        output.send(midi.note_off(60, 480))


if __name__ == '__main__':
    # Define list of mido Messages here. This is the composition which will be sent to the Tempera.
    messages: list[Message] = []

    # event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    asyncio.run(play(messages))
