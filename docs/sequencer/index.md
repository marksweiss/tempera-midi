Module sequencer
================
Composition tools for sequencing Tempera patterns.

Sub-modules
-----------
* sequencer.sequencer

Classes
-------

`BaseSequencer(pool: tempera.emitter_pool.EmitterPool, step_duration: float = None, bpm: float = None, steps_per_beat: int = 1)`
:   Abstract base class for sequencers.
    
    Provides common functionality for timing, looping, and playback control.
    
    Args:
        pool: EmitterPool instance for sending MIDI messages.
        step_duration: Duration of each step in seconds. Mutually exclusive with bpm.
        bpm: Beats per minute. Mutually exclusive with step_duration.
        steps_per_beat: Number of steps per beat (default 1). Only used with bpm.

### Ancestors (in MRO)

* abc.ABC

### Descendants

* sequencer.sequencer.ColumnSequencer
* sequencer.sequencer.GridSequencer

### Instance variables

`step_duration: float`
:   Current step duration in seconds.

### Methods

`dispatch(self, event: dict)`
:   Handle an event from external source. Implemented by subclasses.

`pause(self)`
:   Pause the sequencer.

`resume(self)`
:   Resume the sequencer.

`run(self, loops: int = 0)`
:   Run the sequencer.
    
    Args:
        loops: Number of loops to run. 0 = infinite.

`set_bpm(self, bpm: float, steps_per_beat: int = 1)`
:   Set tempo using BPM.

`set_loops(self, loops: int)`
:   Change the target loop count while running.

`stop(self)`
:   Stop the sequencer.

---------

`ColumnSequencer(pool: tempera.emitter_pool.EmitterPool, step_duration: float = None, bpm: float = None, steps_per_beat: int = 1)`
:   Sequencer that treats the grid as 8 independent columns (samples).
    
    Each column has 8 cells (steps). Pattern format per column: sparse dict {cell: emitter_num}
    - cell: 1-8
    - emitter_num: 1-4
    
    Supports mute patterns for each column that control which loops the column plays.
    
    Example:
        sequencer.set_column_pattern(1, {1: 1, 3: 1, 5: 1, 7: 1})  # Column 1, odd cells, emitter 1
        sequencer.set_mute_pattern(1, [1, 0])  # Column 1 plays every other loop

### Ancestors (in MRO)

* sequencer.sequencer.BaseSequencer
* abc.ABC

### Methods

`clear_column(self, column: int)`
:   Clear pattern for a column.

`dispatch(self, event: dict)`
:   Handle an event from external source.
    
    Supported actions:
        - set_column_pattern: Set pattern for a column. Requires 'column' and 'pattern' keys.
        - clear_column: Clear pattern for a column. Requires 'column' key.
        - mute_column: Mute a column. Requires 'column' key.
        - unmute_column: Unmute a column. Requires 'column' key.
        - set_mute_pattern: Set mute pattern. Requires 'column' and 'pattern' keys.
        - set_loops: Set loop count. Requires 'loops' key.
        - pause: Pause the sequencer.
        - resume: Resume the sequencer.
        - stop: Stop the sequencer.

`get_column_state(self, column: int) ‑> dict`
:   Get state for a specific column.

`get_state(self) ‑> dict`
:   Get full sequencer state.

`mute_column(self, column: int)`
:   Mute a column.

`set_column_pattern(self, column: int, pattern: dict[int, int])`
:   Set pattern for a column.
    
    Args:
        column: Column number (1-8).
        pattern: Sparse dict mapping cell index (1-8) to emitter number (1-4).

`set_mute_pattern(self, column: int, pattern: list)`
:   Set mute pattern for a column.
    
    The mute pattern determines which loops the column plays.
    Pattern is indexed by loop number modulo pattern length.
    
    Args:
        column: Column number (1-8).
        pattern: List of 0/1 or bool values. 1/True = play, 0/False = mute.

`unmute_column(self, column: int)`
:   Unmute a column.

---------

`GridSequencer(pool: tempera.emitter_pool.EmitterPool, step_duration: float = None, bpm: float = None, steps_per_beat: int = 1)`
:   Sequencer that treats all 64 cells as one continuous sequence.
    
    Pattern format: sparse dict {step_index: emitter_num}
    - step_index: 0-63 (column-major: 0-7 in col 1, 8-15 in col 2, etc.)
    - emitter_num: 1-4
    
    Example:
        pattern = {0: 1, 4: 2, 8: 1}  # Steps 0 and 8 use emitter 1, step 4 uses emitter 2

### Ancestors (in MRO)

* sequencer.sequencer.BaseSequencer
* abc.ABC

### Methods

`clear(self)`
:   Clear the pattern, removing all cells.

`dispatch(self, event: dict)`
:   Handle an event from external source.
    
    Supported actions:
        - set_pattern: Set the pattern. Requires 'pattern' key.
        - clear: Clear the pattern.
        - set_loops: Set loop count. Requires 'loops' key.
        - pause: Pause the sequencer.
        - resume: Resume the sequencer.
        - stop: Stop the sequencer.

`get_state(self) ‑> dict`
:   Get current sequencer state.

`set_pattern(self, pattern: dict[int, int])`
:   Set the 64-step pattern.
    
    Args:
        pattern: Sparse dict mapping step index (0-63) to emitter number (1-4).

---------