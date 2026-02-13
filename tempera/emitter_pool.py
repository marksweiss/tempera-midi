import asyncio
import os
from typing import Union

import mido
from mido import Message

from tempera.emitter import Emitter, DEFAULT_PLAYBACK_CHANNEL


class EmitterPool:
    """
    Async pool managing four Tempera emitters with queue-based message dispatch.

    Each emitter is assigned to its corresponding MIDI channel (emitter 1 → channel 1, etc.).
    All methods enqueue messages to a background sender task for ordered, non-blocking delivery.

    Usage:
        async with EmitterPool() as pool:
            await pool.volume(1, 100)
            await pool.place_in_cell(2, column=1, cell=1)

    Args:
        port_name: MIDI port name. Defaults to TEMPERA_PORT environment variable.
        virtual: If True, create a virtual MIDI port (for testing). Defaults to False.
    """

    def __init__(self, port_name: str = None, virtual: bool = False, emitters_on_own_channels: bool = False):
        self._port_name = port_name or os.environ.get('TEMPERA_PORT', 'Tempera')
        self._virtual = virtual
        self._emitters_on_own_channels = emitters_on_own_channels
        if emitters_on_own_channels:
            self._emitters = {i: Emitter(emitter=i, midi_channel=DEFAULT_PLAYBACK_CHANNEL + i) for i in range(1, 5)}
        else:
            self._emitters = {i: Emitter(emitter=i) for i in range(1, 5)}
            # All emitters on same channel, so only need to send one note_on and one note_off
            # Capture reference at init time to not have to look it up on each call to play_all()
            self._midi = self._emitters[1].midi
        self._queue: asyncio.Queue[Union[Message, list[Message]]] = asyncio.Queue()
        self._output = None
        self._sender_task = None
        self._running = False

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
        return False

    async def start(self):
        """Open MIDI port and start the background sender task."""
        self._output = mido.open_output(self._port_name, virtual=self._virtual)
        self._running = True
        self._sender_task = asyncio.create_task(self._sender_loop())

    async def stop(self):
        """Stop the sender task, drain the queue, and close the MIDI port."""
        if self._sender_task:
            # Wait for queue to drain with timeout (sender loop still running)
            try:
                await asyncio.wait_for(self._queue.join(), timeout=1.0)
            except asyncio.TimeoutError:
                pass
            # Now stop the sender loop and cancel the task
            self._running = False
            self._sender_task.cancel()
            try:
                await self._sender_task
            except asyncio.CancelledError:
                pass
        self._running = False
        if self._output:
            self._output.close()
            self._output = None

    async def _sender_loop(self):
        """Background task that consumes messages from the queue and sends them."""
        while self._running:
            try:
                item = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue

            if isinstance(item, list):
                for msg in item:
                    self._output.send(msg)
            else:
                self._output.send(item)
            self._queue.task_done()

    # --- Emitter parameter methods ---

    async def volume(self, emitter_num: int, value: int):
        """Change Emitter Volume."""
        if emitter_num not in self._emitters:
            raise ValueError(f"Invalid emitter number: {emitter_num}. Must be 1-4.")
        msg = self._emitters[emitter_num].volume(value)
        await self._queue.put(msg)

    async def grain(
        self,
        emitter_num: int,
        *,
        length_cell: int = None,
        length_note: int = None,
        density: int = None,
        shape: int = None,
        shape_attack: int = None,
        pan: int = None,
        tune_spread: int = None
    ):
        """Change Emitter Grain Parameters."""
        msgs = self._emitters[emitter_num].grain(
            length_cell=length_cell,
            length_note=length_note,
            density=density,
            shape=shape,
            shape_attack=shape_attack,
            pan=pan,
            tune_spread=tune_spread
        )
        await self._queue.put(msgs)

    async def octave(self, emitter_num: int, value: int):
        """Change Emitter Octave."""
        msg = self._emitters[emitter_num].octave(value)
        await self._queue.put(msg)

    async def relative_position(self, emitter_num: int, *, x: int = None, y: int = None):
        """Change Emitter Position along X and Y axes."""
        msgs = self._emitters[emitter_num].relative_position(x=x, y=y)
        await self._queue.put(msgs)

    async def spray(self, emitter_num: int, *, x: int = None, y: int = None):
        """Change Emitter Spray along X and Y axes."""
        msgs = self._emitters[emitter_num].spray(x=x, y=y)
        await self._queue.put(msgs)

    async def tone_filter(self, emitter_num: int, *, width: int = None, center: int = None):
        """Change Emitter Filter width and center."""
        msgs = self._emitters[emitter_num].tone_filter(width=width, center=center)
        await self._queue.put(msgs)

    async def effects_send(self, emitter_num: int, value: int):
        """Change Emitter Effects Send."""
        msg = self._emitters[emitter_num].effects_send(value)
        await self._queue.put(msg)

    # --- Emitter control methods ---

    async def set_active(self, emitter_num: int):
        """Set Emitter as Active."""
        msg = self._emitters[emitter_num].set_active()
        await self._queue.put(msg)

    async def place_in_cell(self, emitter_num: int, column: int, cell: int):
        """Place Emitter in a given Cell in a given Column."""
        msg = self._emitters[emitter_num].place_in_cell(column, cell)
        await self._queue.put(msg)

    async def play(self, emitter_num: int, note: int = 60, velocity: int = 127, duration: float = 1.0):
        """Play a note on the Emitter's MIDI channel. Results in all placed cells playing the note."""
        await self._queue.put(self._emitters[emitter_num].midi.note_on(note, velocity, 0))
        await asyncio.sleep(duration)
        await self._queue.put(self._emitters[emitter_num].midi.note_off(note, 0))

    async def play_all(
        self,
        emitter_nums: list[int],
        note: int = 60,
        velocity: int = 127,
        duration: float = 1.0
    ):
        """Play a note on multiple emitters concurrently.

        Sends all note_on messages, waits for duration, then sends all note_off messages.

        Args:
            emitter_nums: List of emitter numbers (1-4) to play.
            note: MIDI note number.
            velocity: Note velocity.
            duration: Note duration in seconds.
        """
        if not emitter_nums:
            return

        # Default is all on same channel so check that first
        if not self._emitters_on_own_channels:
            await self._queue.put(self._midi.note_on(note, velocity, 0))
            await asyncio.sleep(duration)
            await self._queue.put(self._midi.note_off(note, 0))
        else:
            # Send all note_on messages
            for emitter_num in emitter_nums:
                await self._queue.put(self._emitters[emitter_num].midi.note_on(note, velocity, 0))
            await asyncio.sleep(duration)
            # Send all note_off messages
            for emitter_num in emitter_nums:
                await self._queue.put(self._emitters[emitter_num].midi.note_off(note, 0))

    async def remove_from_cell(self, emitter_num: int, column: int, cell: int):
        """Remove Emitter placement from a given Cell in a given Column."""
        msg = self._emitters[emitter_num].remove_from_cell(column, cell)
        await self._queue.put(msg)

    # --- Generic dispatch ---

    async def dispatch(self, event: dict):
        """
        Dispatch an event to the appropriate emitter method.

        Args:
            event: Dictionary with keys:
                - emitter: Emitter number (1-4)
                - method: Method name (e.g., 'volume', 'grain', 'place_in_cell')
                - args: Optional list of positional arguments
                - kwargs: Optional dict of keyword arguments

        Example:
            await pool.dispatch({'emitter': 1, 'method': 'volume', 'args': [64]})
            await pool.dispatch({'emitter': 2, 'method': 'grain', 'kwargs': {'density': 80}})
        """
        emitter_num = event['emitter']
        method_name = event['method']
        args = event.get('args', [])
        kwargs = event.get('kwargs', {})

        method = getattr(self, method_name)
        await method(emitter_num, *args, **kwargs)

    # --- Low-level escape hatch ---
    async def send_raw(self, message: Union[Message, list[Message]]):
        """Send a raw MIDI message or list of messages through the queue."""
        await self._queue.put(message)
