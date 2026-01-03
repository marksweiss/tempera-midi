"""Sequencer classes for composing Tempera patterns."""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional

from tempera import EmitterPool


class BaseSequencer(ABC):
    """
    Abstract base class for sequencers.

    Provides common functionality for timing, looping, and playback control.

    Args:
        pool: EmitterPool instance for sending MIDI messages.
        step_duration: Duration of each step in seconds. Mutually exclusive with bpm.
        bpm: Beats per minute. Mutually exclusive with step_duration.
        steps_per_beat: Number of steps per beat (default 1). Only used with bpm.
    """

    # noinspection PyTypeHints
    def __init__(
        self,
        pool: EmitterPool,
        step_duration: Optional[float] = None,
        bpm: Optional[float] = None,
        steps_per_beat: int = 1
    ):
        self.pool = pool
        self._running = False
        self._paused = False
        self._current_step = 0
        self._loop_count = 0
        self._target_loops = 0
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Not paused initially

        # Calculate step duration
        if bpm is not None and step_duration is not None:
            raise ValueError("Cannot specify both bpm and step_duration")
        elif bpm is not None:
            self._step_duration = 60.0 / bpm / steps_per_beat
        elif step_duration is not None:
            self._step_duration = step_duration
        else:
            self._step_duration = 0.5  # Default 0.5 seconds

    @property
    def step_duration(self) -> float:
        """Current step duration in seconds."""
        return self._step_duration

    @step_duration.setter
    def step_duration(self, value: float):
        """Set step duration in seconds."""
        self._step_duration = value

    def set_bpm(self, bpm: float, steps_per_beat: int = 1):
        """Set tempo using BPM."""
        self._step_duration = 60.0 / bpm / steps_per_beat

    async def run(self, loops: int = 0):
        """
        Run the sequencer.

        Args:
            loops: Number of loops to run. 0 = infinite.
        """
        self._running = True
        self._target_loops = loops
        self._loop_count = 0
        self._current_step = 0

        total_steps = self._get_total_steps()

        while self._running:
            # Check if paused
            await self._pause_event.wait()

            if not self._running:
                break

            # Execute current step
            active_emitters = await self._execute_step(self._current_step, self._loop_count)

            # Play notes on active emitters concurrently, then wait for step duration
            if active_emitters:
                await self.pool.play_all(
                    list(active_emitters),
                    duration=self._step_duration * 0.999  # Slightly shorter to avoid overlap
                )
                # Small gap after notes end before next step
                await asyncio.sleep(self._step_duration * 0.001)
            else:
                # No active emitters - still need to maintain step timing
                await asyncio.sleep(self._step_duration)

            # Advance step
            self._current_step += 1
            if self._current_step >= total_steps:
                self._current_step = 0
                self._loop_count += 1

                # Check if we've completed target loops
                if 0 < self._target_loops <= self._loop_count:
                    self._running = False
                    break

    async def stop(self):
        """Stop the sequencer."""
        self._running = False
        self._pause_event.set()  # Unblock if paused

    async def pause(self):
        """Pause the sequencer."""
        self._paused = True
        self._pause_event.clear()

    async def resume(self):
        """Resume the sequencer."""
        self._paused = False
        self._pause_event.set()

    def set_loops(self, loops: int):
        """Change the target loop count while running."""
        self._target_loops = loops

    @abstractmethod
    async def _execute_step(self, step: int, loop: int) -> set[int]:
        """Execute a single step. Implemented by subclasses.

        Returns:
            Set of emitter numbers (1-4) that are active in this step.
        """
        pass

    @abstractmethod
    def _get_total_steps(self) -> int:
        """Return total number of steps in sequence. Implemented by subclasses."""
        pass

    @abstractmethod
    async def dispatch(self, event: dict):
        """Handle an event from external source. Implemented by subclasses."""
        pass


class GridSequencer(BaseSequencer):
    """
    Sequencer that treats all 64 cells as one continuous sequence.

    Pattern format: sparse dict {step_index: emitter_num}
    - step_index: 0-63 (column-major: 0-7 in col 1, 8-15 in col 2, etc.)
    - emitter_num: 1-4

    Example:
        pattern = {0: 1, 4: 2, 8: 1}  # Steps 0 and 8 use emitter 1, step 4 uses emitter 2
    """

    DISPATCH_HANDLERS = {
        'set_pattern': lambda self, event: self.set_pattern(event['pattern']),
        'clear': lambda self, event: self.clear(),
        'cleanup': lambda self, event: self.cleanup(),
        'set_loops': lambda self, event: self.set_loops(event['loops']),
        'pause': lambda self, event: self.pause(),
        'resume': lambda self, event: self.resume(),
        'stop': lambda self, event: self.stop(),
    }

    # noinspection PyTypeHints
    def __init__(
        self,
        pool: EmitterPool,
        step_duration: Optional[float] = None,
        bpm: Optional[float] = None,
        steps_per_beat: int = 1
    ):
        super().__init__(pool, step_duration, bpm, steps_per_beat)
        self._pattern: dict[int, int] = {}
        self._prev_step_cells: dict[int, int] = {}  # {step: emitter} for cells active in previous step

    async def set_pattern(self, pattern: dict[int, int]):
        """
        Set the 64-step pattern.

        Args:
            pattern: Sparse dict mapping step index (0-63) to emitter number (1-4).
        """
        old_pattern = self._pattern
        self._pattern = dict(pattern)

        # Remove cells that were in old pattern but not in new
        for step, emitter_num in old_pattern.items():
            if step not in self._pattern:
                column = (step // 8) + 1
                cell = (step % 8) + 1
                await self.pool.remove_from_cell(emitter_num, column, cell)

    async def clear(self):
        """Clear the pattern, removing all cells."""
        await self.set_pattern({})

    async def cleanup(self):
        """Remove all cells that were placed by this sequencer."""
        for step, emitter_num in self._prev_step_cells.items():
            column = (step // 8) + 1
            cell = (step % 8) + 1
            await self.pool.remove_from_cell(emitter_num, column, cell)
        self._prev_step_cells.clear()

    def get_state(self) -> dict:
        """Get current sequencer state."""
        return {
            'pattern': dict(self._pattern),
            'current_step': self._current_step,
            'loop_count': self._loop_count,
            'running': self._running,
            'paused': self._paused
        }

    def _get_total_steps(self) -> int:
        """Return total steps based on pattern. Defaults to 8 (column count) for empty pattern."""
        if not self._pattern:
            return 8
        return max(self._pattern.keys()) + 1

    async def _execute_step(self, step: int, loop: int) -> set[int]:
        """Execute a single step of the sequence."""
        active_emitters: set[int] = set()

        # Calculate column and cell from step index
        column = (step // 8) + 1
        cell = (step % 8) + 1

        # Check if this step is in the pattern
        if step in self._pattern:
            emitter_num = self._pattern[step]
            await self.pool.place_in_cell(emitter_num, column, cell)
            self._prev_step_cells[step] = emitter_num
            active_emitters.add(emitter_num)
        elif step in self._prev_step_cells:
            # Cell was active but no longer - remove it
            prev_emitter = self._prev_step_cells.pop(step)
            await self.pool.remove_from_cell(prev_emitter, column, cell)

        return active_emitters

    async def dispatch(self, event: dict):
        """
        Handle an event from external source.

        Supported actions:
            - set_pattern: Set the pattern. Requires 'pattern' key.
            - clear: Clear the pattern.
            - cleanup: Remove all placed cells.
            - set_loops: Set loop count. Requires 'loops' key.
            - pause: Pause the sequencer.
            - resume: Resume the sequencer.
            - stop: Stop the sequencer.
        """
        action = event.get('action')

        handler = self.DISPATCH_HANDLERS.get(action)
        if handler is None:
            raise ValueError(f"Unknown action: {action}")

        result = handler(self, event)
        if asyncio.iscoroutine(result):
            await result


class ColumnSequencer(BaseSequencer):
    """
    Sequencer that treats the grid as 8 independent columns (samples).

    Each column has 8 cells (steps). Pattern format per column: sparse dict {cell: emitter_num}
    - cell: 1-8
    - emitter_num: 1-4

    Supports mute patterns for each column that control which loops the column plays.

    Example:
        sequencer.set_column_pattern(1, {1: 1, 3: 1, 5: 1, 7: 1})  # Column 1, odd cells, emitter 1
        sequencer.set_mute_pattern(1, [1, 0])  # Column 1 plays every other loop
    """

    DISPATCH_HANDLERS = {
        'set_column_pattern': lambda self, event: self.set_column_pattern(event['column'], event['pattern']),
        'clear_column': lambda self, event: self.clear_column(event['column']),
        'cleanup': lambda self, event: self.cleanup(),
        'mute_column': lambda self, event: self.mute_column(event['column']),
        'unmute_column': lambda self, event: self.unmute_column(event['column']),
        'set_mute_pattern': lambda self, event: self.set_column_mute_pattern(event['column'], event['pattern']),
        'set_loops': lambda self, event: self.set_loops(event['loops']),
        'pause': lambda self, event: self.pause(),
        'resume': lambda self, event: self.resume(),
        'stop': lambda self, event: self.stop(),
    }

    # noinspection PyTypeHints
    def __init__(
        self,
        pool: EmitterPool,
        step_duration: Optional[float] = None,
        bpm: Optional[float] = None,
        steps_per_beat: int = 1
    ):
        super().__init__(pool, step_duration, bpm, steps_per_beat)
        # Patterns per column: {column: {cell: emitter}}
        self._patterns: dict[int, dict[int, int]] = {i: {} for i in range(1, 9)}
        # Mute state per column
        self._muted: dict[int, bool] = {i: False for i in range(1, 9)}
        # Mute patterns per column: {column: [bool, ...]}
        self._mute_patterns: dict[int, list] = {i: [] for i in range(1, 9)}
        # Track previously active cells per column: {column: {cell: emitter}}
        self._prev_step_cells: dict[int, dict[int, int]] = {i: {} for i in range(1, 9)}

    async def set_column_pattern(self, column: int, pattern: dict[int, int]):
        """
        Set pattern for a column.

        Args:
            column: Column number (1-8).
            pattern: Sparse dict mapping cell index (1-8) to emitter number (1-4).
        """
        if column < 1 or column > 8:
            raise ValueError(f"column must be 1-8, got {column}")

        old_pattern = self._patterns[column]
        self._patterns[column] = dict(pattern)

        # Remove cells that were in old pattern but not in new
        for cell, emitter in old_pattern.items():
            if cell not in self._patterns[column]:
                await self.pool.remove_from_cell(emitter, column, cell)

    async def clear_column(self, column: int):
        """Clear pattern for a column."""
        if column < 1 or column > 8:
            raise ValueError(f"column must be 1-8, got {column}")
        await self.set_column_pattern(column, {})

    async def cleanup(self):
        """Remove all cells that were placed by this sequencer."""
        for column in range(1, 9):
            for cell, emitter_num in self._prev_step_cells[column].items():
                await self.pool.remove_from_cell(emitter_num, column, cell)
            self._prev_step_cells[column].clear()

    def mute_column(self, column: int):
        """Mute a column."""
        if column < 1 or column > 8:
            raise ValueError(f"column must be 1-8, got {column}")
        self._muted[column] = True

    def unmute_column(self, column: int):
        """Unmute a column."""
        if column < 1 or column > 8:
            raise ValueError(f"column must be 1-8, got {column}")
        self._muted[column] = False

    def set_column_mute_pattern(self, column: int, pattern: list):
        """
        Set mute pattern for a column.

        The mute pattern determines which loops the column plays.
        Pattern is indexed by loop number modulo pattern length.

        Args:
            column: Column number (1-8).
            pattern: List of 0/1 or bool values. 1/True = play, 0/False = mute.
        """
        if column < 1 or column > 8:
            raise ValueError(f"column must be 1-8, got {column}")
        self._mute_patterns[column] = [bool(v) for v in pattern]

    def get_column_state(self, column: int) -> dict:
        """Get state for a specific column."""
        if column < 1 or column > 8:
            raise ValueError(f"column must be 1-8, got {column}")
        return {
            'pattern': dict(self._patterns[column]),
            'muted': self._muted[column],
            'mute_pattern': list(self._mute_patterns[column])
        }

    def get_state(self) -> dict:
        """Get full sequencer state."""
        return {
            'columns': {i: self.get_column_state(i) for i in range(1, 9)},
            'current_step': self._current_step,
            'loop_count': self._loop_count,
            'running': self._running,
            'paused': self._paused
        }

    def _get_total_steps(self) -> int:
        return 8

    def _is_column_muted_this_loop(self, column: int, loop: int) -> bool:
        """Check if column should be muted for current loop."""
        if self._muted[column]:
            return True
        mute_pattern = self._mute_patterns[column]
        if not mute_pattern:
            return False
        # Pattern value: True = play, False = mute
        return not mute_pattern[loop % len(mute_pattern)]

    async def _execute_step(self, step: int, loop: int) -> set[int]:
        """Execute a single step across all columns."""
        active_emitters: set[int] = set()
        cell = step + 1  # Convert 0-indexed step to 1-indexed cell

        for column in range(1, 9):
            # Check if column is muted this loop
            if self._is_column_muted_this_loop(column, loop):
                # If muted and cell was previously active, remove it
                if cell in self._prev_step_cells[column]:
                    prev_emitter_num = self._prev_step_cells[column].pop(cell)
                    await self.pool.remove_from_cell(prev_emitter_num, column, cell)
                continue

            pattern = self._patterns[column]

            if cell in pattern:
                emitter_num = pattern[cell]
                await self.pool.place_in_cell(emitter_num, column, cell)
                self._prev_step_cells[column][cell] = emitter_num
                active_emitters.add(emitter_num)
            elif cell in self._prev_step_cells[column]:
                # Cell was active but no longer - remove it
                prev_emitter_num = self._prev_step_cells[column].pop(cell)
                await self.pool.remove_from_cell(prev_emitter_num, column, cell)

        return active_emitters

    async def dispatch(self, event: dict):
        """
        Handle an event from external source.

        Supported actions:
            - set_column_pattern: Set pattern for a column. Requires 'column' and 'pattern' keys.
            - clear_column: Clear pattern for a column. Requires 'column' key.
            - cleanup: Remove all placed cells.
            - mute_column: Mute a column. Requires 'column' key.
            - unmute_column: Unmute a column. Requires 'column' key.
            - set_mute_pattern: Set mute pattern. Requires 'column' and 'pattern' keys.
            - set_loops: Set loop count. Requires 'loops' key.
            - pause: Pause the sequencer.
            - resume: Resume the sequencer.
            - stop: Stop the sequencer.
        """
        action = event.get('action')

        handler = self.DISPATCH_HANDLERS.get(action)
        if handler is None:
            raise ValueError(f"Unknown action: {action}")

        result = handler(self, event)
        if asyncio.iscoroutine(result):
            await result
