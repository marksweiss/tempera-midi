"""Main application window and entry point for Tempera GUI."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QFileDialog, QMessageBox, QPushButton
)

import qasync

from gui.adapter import TemperaAdapter
from gui.widgets import (
    CellGrid, EmitterPanel, TrackPanel, GlobalPanel, TransportPanel,
    create_hint_overlay, ShortcutsDialog
)
from gui.envelope.envelope_panel import EnvelopePanel
from gui.shortcuts import ShortcutManager, NavigationManager, Section, NavigationMode
from gui.preferences import get_preferences
from gui.styles import MAIN_STYLESHEET


class MainWindow(QMainWindow):
    """
    Main application window for Tempera MIDI controller.

    Layout:
    - Top row: Cell grid + Transport (left) | Emitter panel (right, expands)
    - Bottom row: Track panel (left) | Global effects panel (right, expands)
    """

    def __init__(self, adapter: TemperaAdapter):
        super().__init__()

        self._adapter = adapter
        self._adapter.set_status_callback(self._update_status)
        self._prefs = get_preferences()

        # Grid mode: 'hardware' | 'column' | 'grid'
        self._grid_mode = 'hardware'

        self._setup_ui()
        self._setup_shortcuts()
        self._setup_navigation()
        self._connect_signals()

        # Create hint overlay (after UI is set up)
        self._hint_overlay = create_hint_overlay(self)

        # Load initial state into UI
        self._sync_ui_from_state()

    def _schedule_async(self, coro):
        """Safely schedule an async coroutine if an event loop is running.

        In test environments without a running event loop, this is a no-op
        to avoid 'Task was destroyed but pending' warnings.
        """
        try:
            asyncio.get_running_loop()
            asyncio.ensure_future(coro)
        except RuntimeError:
            # No running event loop (e.g., in tests) - close the coroutine
            # to avoid 'coroutine was never awaited' warning
            coro.close()

    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle('Tempera MIDI Controller')

        # Calculate initial window size based on screen
        self._set_initial_size()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Calculate grid width (matches CellGrid._setup_ui calculation)
        grid_width = (CellGrid.CELL_SIZE * 8) + (CellGrid.CELL_SPACING * 7) + (CellGrid.PADDING * 2)

        # Top row: Envelope panel + Help button
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        self._envelope_panel = EnvelopePanel()
        top_row.addWidget(self._envelope_panel, stretch=1)

        # Help button (top-right corner)
        help_btn = QPushButton('?')
        help_btn.setFixedSize(32, 32)
        help_btn.setToolTip('Keyboard Shortcuts Help (F1)')
        help_btn.setStyleSheet('''
            QPushButton {
                font-weight: bold;
                font-size: 16px;
                border-radius: 16px;
                background-color: #404040;
                color: #C0C0C0;
            }
            QPushButton:hover {
                background-color: #505050;
                color: #E0E0E0;
            }
        ''')
        help_btn.clicked.connect(self._show_shortcuts_dialog)
        top_row.addWidget(help_btn, alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addLayout(top_row)

        # Top section: Grid + Transport (left) | Emitter panel (right)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(16)

        # Left column: Cell grid + Transport (stacked vertically)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(11)

        self._cell_grid = CellGrid()
        left_layout.addWidget(self._cell_grid, alignment=Qt.AlignmentFlag.AlignTop)

        left_layout.addStretch()

        # Transport panel - constrained to cell grid width, aligned to bottom
        self._transport = TransportPanel()
        self._transport.setFixedWidth(grid_width)
        left_layout.addWidget(self._transport, alignment=Qt.AlignmentFlag.AlignBottom)
        left_widget.setFixedWidth(grid_width + 8)  # Small margin
        # Calculate minimum height: grid + spacing + transport (estimated ~100px)
        grid_height = (CellGrid.CELL_SIZE * 8) + (CellGrid.CELL_SPACING * 7) + (CellGrid.PADDING * 2)
        left_widget.setMinimumHeight(grid_height + 16 + 100)
        top_layout.addWidget(left_widget)

        # Right: Emitter panel (expands)
        self._emitter_panel = EmitterPanel()
        top_layout.addWidget(self._emitter_panel, stretch=1)

        main_layout.addLayout(top_layout, stretch=2)

        # Bottom section: Track panel (left) | Global/Effects panel (right)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        self._track_panel = TrackPanel()
        self._track_panel.setFixedWidth(grid_width + 8)  # Match left column width
        bottom_layout.addWidget(self._track_panel, alignment=Qt.AlignmentFlag.AlignBottom)

        self._global_panel = GlobalPanel()
        bottom_layout.addWidget(self._global_panel, stretch=1)

        main_layout.addLayout(bottom_layout, stretch=1)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage('Not connected')

    def _set_initial_size(self):
        """Calculate and set initial window size to fit all UI elements.

        Uses 90% of screen size or a minimum of 1200x850, whichever fits.
        If the required size exceeds screen, opens maximized.
        """
        # Minimum size needed to show all UI elements comfortably
        min_width = 1200
        min_height = 850

        # Get the primary screen's available geometry
        screen = QApplication.primaryScreen()
        if screen is None:
            # Fallback if no screen detected
            self.setMinimumSize(min_width, min_height)
            self.resize(min_width, min_height)
            return

        available = screen.availableGeometry()
        screen_width = available.width()
        screen_height = available.height()

        # Target 90% of screen size
        target_width = int(screen_width * 0.9)
        target_height = int(screen_height * 0.9)

        # Use the larger of minimum or target (capped at screen size)
        final_width = max(min_width, target_width)
        final_height = max(min_height, target_height)

        # If we need more space than available, maximize the window
        if final_width >= screen_width or final_height >= screen_height:
            self.setMinimumSize(800, 600)  # Allow some flexibility when maximized
            self.showMaximized()
        else:
            self.setMinimumSize(min_width, min_height)
            self.resize(final_width, final_height)

            # Center the window on screen
            x = available.x() + (screen_width - final_width) // 2
            y = available.y() + (screen_height - final_height) // 2
            self.move(x, y)

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts.

        Note: Section navigation (Q/E/T/G) is handled by NavigationManager.
        ShortcutManager only handles non-conflicting shortcuts.
        """
        self._shortcuts = ShortcutManager(self)
        self._shortcuts.setup_defaults(
            select_emitter=self._on_select_emitter,
            play=self._on_play,
            stop=self._on_stop,
            undo=self._on_undo,
            redo=self._on_redo,
            save_preset=self._on_save_preset,
            load_preset=self._on_load_preset,
        )

    def _setup_navigation(self):
        """Set up the keyboard navigation manager."""
        self._nav = NavigationManager(self)

        # Register section structures with NavigationManager
        # This tells NavigationManager how many subsections and controls each section has
        # Emitter: 4 subsections (Basic=3, Filter=2, Grain=7, Position=4)
        self._nav.register_section_structure(Section.EMITTER, [3, 2, 7, 4])
        # Global: 6 subsections (ADSR=4, Reverb=3, Delay=4, Filter=2, Chorus=4, Modulator=2)
        self._nav.register_section_structure(Section.GLOBAL, [4, 3, 4, 2, 4, 2])
        # Tracks: 8 subsections (one per track), each with 1 control (volume)
        self._nav.register_section_structure(Section.TRACKS, [1, 1, 1, 1, 1, 1, 1, 1])
        # Grid: 8 columns, 8 cells each (handled differently, but register for consistency)
        self._nav.register_section_structure(Section.GRID, [8, 8, 8, 8, 8, 8, 8, 8])

        # Connect navigation signals
        self._nav.sectionChanged.connect(self._on_section_changed)
        self._nav.subsectionChanged.connect(self._on_subsection_changed)
        self._nav.controlChanged.connect(self._on_control_changed)
        self._nav.modeChanged.connect(self._on_mode_changed)
        self._nav.valueAdjust.connect(self._on_value_adjust)
        self._nav.navigationPathChanged.connect(self._on_nav_path_changed)
        self._nav.actionTriggered.connect(self._on_nav_action)

        # Set callbacks for shared shortcuts
        self._nav.set_callback('emitter_1', lambda: self._on_select_emitter(1))
        self._nav.set_callback('emitter_2', lambda: self._on_select_emitter(2))
        self._nav.set_callback('emitter_3', lambda: self._on_select_emitter(3))
        self._nav.set_callback('emitter_4', lambda: self._on_select_emitter(4))
        self._nav.set_callback('stop', self._on_stop)
        self._nav.set_callback('undo', self._on_undo)
        self._nav.set_callback('redo', self._on_redo)
        self._nav.set_callback('save_preset', self._on_save_preset)
        self._nav.set_callback('load_preset', self._on_load_preset)

    def _connect_signals(self):
        """Connect widget signals to handlers."""
        # Emitter panel
        self._emitter_panel.emitterSelected.connect(self._on_emitter_selected)
        self._emitter_panel.parameterChanged.connect(self._on_emitter_param_changed)
        self._emitter_panel.parameterSet.connect(self._on_emitter_param_set)

        # Cell grid
        self._cell_grid.cellClicked.connect(self._on_cell_clicked)
        self._cell_grid.cellRightClicked.connect(self._on_cell_right_clicked)

        # Track panel
        self._track_panel.volumeChanged.connect(self._on_track_volume_changed)
        self._track_panel.volumeSet.connect(self._on_track_volume_set)
        self._track_panel.recordClicked.connect(self._on_track_record)

        # Global panel
        self._global_panel.modulatorSizeChanged.connect(self._on_modulator_size_changed)
        self._global_panel.modulatorSizeSet.connect(self._on_modulator_size_set)
        self._global_panel.modulatorSelected.connect(self._on_modulator_selected)
        self._global_panel.parameterChanged.connect(self._on_global_param_changed)
        self._global_panel.parameterSet.connect(self._on_global_param_set)

        # Transport
        self._transport.playClicked.connect(self._on_play)
        self._transport.stopClicked.connect(self._on_stop)
        self._transport.sequencerChanged.connect(self._on_sequencer_changed)
        self._transport.bpmChanged.connect(self._on_bpm_changed)

        # State manager listener for undo/redo updates
        self._adapter.state.add_listener(self._on_state_changed)

        # Envelope panel
        self._envelope_panel.envelopeChanged.connect(self._on_envelope_changed)
        self._envelope_panel.enabledToggled.connect(self._on_envelope_toggled)

        # Envelope position callback for playhead
        self._adapter.set_envelope_position_callback(self._on_envelope_position)

        # Panel control focus requests (mouse click focus)
        self._emitter_panel.controlFocusRequested.connect(
            lambda sub, ctrl: self._nav.focus_control(Section.EMITTER, sub, ctrl)
        )
        self._global_panel.controlFocusRequested.connect(
            lambda sub, ctrl: self._nav.focus_control(Section.GLOBAL, sub, ctrl)
        )
        self._track_panel.controlFocusRequested.connect(
            lambda sub, ctrl: self._nav.focus_control(Section.TRACKS, sub, ctrl)
        )

        # Panel section click signals (mouse click on panel background)
        self._emitter_panel.sectionClicked.connect(
            lambda: self._nav.focus_section(Section.EMITTER)
        )
        self._global_panel.sectionClicked.connect(
            lambda: self._nav.focus_section(Section.GLOBAL)
        )
        self._track_panel.sectionClicked.connect(
            lambda: self._nav.focus_section(Section.TRACKS)
        )

        # Panel subsection focus requests (mouse click on subsection header)
        self._emitter_panel.subsectionFocusRequested.connect(
            lambda sub: self._nav.focus_subsection(Section.EMITTER, sub)
        )
        self._global_panel.subsectionFocusRequested.connect(
            lambda sub: self._nav.focus_subsection(Section.GLOBAL, sub)
        )

        # Note: Panel keyboard navigation signals (subsectionNavigated, controlNavigated)
        # have been removed. NavigationManager is now the single source of truth for
        # navigation state, and panels are purely reactive to its signals.

    def _sync_ui_from_state(self):
        """Synchronize UI from current state."""
        state = self._adapter.state.state

        # Sync emitter parameters
        for emitter_num, params in state['emitters'].items():
            self._emitter_panel.set_all_parameters(emitter_num, params)

        # Sync track volumes
        track_volumes = {t: p['volume'] for t, p in state['tracks'].items()}
        self._track_panel.set_all_volumes(track_volumes)

        # Sync global parameters
        self._global_panel.set_all_parameters(state['global'])

        # Sync cells based on current grid mode
        if self._grid_mode == 'hardware':
            self._cell_grid.set_all_cells(state['cells'])
        elif self._grid_mode == 'column':
            self._load_column_patterns_to_grid()
        else:  # 'grid'
            self._load_grid_pattern_to_grid()

        # Sync active emitter
        self._emitter_panel.select_emitter(state['active_emitter'])
        self._cell_grid.set_active_emitter(state['active_emitter'])

    def _update_status(self, message: str):
        """Update status bar message."""
        self._status_bar.showMessage(message)

    # --- Event handlers ---

    def _on_connect(self):
        """Handle connect menu action."""
        self._schedule_async(self._connect())

    async def _connect(self):
        """Connect to Tempera."""
        success = await self._adapter.connect()
        if success:
            self._sync_ui_from_state()

    def _on_disconnect(self):
        """Handle disconnect menu action."""
        self._schedule_async(self._adapter.disconnect())

    def _on_save_preset(self):
        """Handle save preset action."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Save Preset', '', 'JSON Files (*.json)'
        )
        if filepath:
            if not filepath.endswith('.json'):
                filepath += '.json'
            self._adapter.save_preset(Path(filepath))

    def _on_load_preset(self):
        """Handle load preset action."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, 'Load Preset', '', 'JSON Files (*.json)'
        )
        if filepath:
            self._schedule_async(self._adapter.load_preset(Path(filepath)))
            self._sync_ui_from_state()

    def _on_undo(self):
        """Handle undo action."""
        self._schedule_async(self._do_undo())

    async def _do_undo(self):
        if await self._adapter.undo():
            self._sync_ui_from_state()

    def _on_redo(self):
        """Handle redo action."""
        self._schedule_async(self._do_redo())

    async def _do_redo(self):
        if await self._adapter.redo():
            self._sync_ui_from_state()

    def _on_reset(self):
        """Handle reset to defaults action."""
        reply = QMessageBox.question(
            self, 'Reset to Defaults',
            'Reset all parameters to default values?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._schedule_async(self._adapter.reset_to_defaults())
            self._sync_ui_from_state()

    def _on_select_emitter(self, emitter_num: int):
        """Handle emitter selection via keyboard."""
        # Update state directly (synchronously) so it's immediately available
        self._adapter.state.set_active_emitter(emitter_num)
        self._emitter_panel.select_emitter(emitter_num)
        self._cell_grid.set_active_emitter(emitter_num)
        # Update envelope panel to reflect the new emitter
        self._update_envelope_panel_for_focus()

    def _on_emitter_selected(self, emitter_num: int):
        """Handle emitter selection from panel."""
        self._schedule_async(self._adapter.set_active_emitter(emitter_num))
        self._cell_grid.set_active_emitter(emitter_num)

    def _on_emitter_param_changed(self, emitter_num: int, param: str, value: int):
        """Handle emitter parameter change during drag."""
        self._adapter.set_emitter_param(emitter_num, param, value, immediate=False)

    def _on_emitter_param_set(self, emitter_num: int, param: str, value: int):
        """Handle emitter parameter set on release."""
        self._adapter.set_emitter_param(emitter_num, param, value, immediate=True)

    def _on_cell_clicked(self, column: int, cell: int):
        """Handle cell click (left button).

        Behavior depends on current grid mode:
        - hardware: Toggle emitter placement on Tempera hardware
        - column: Toggle cell in column sequencer pattern
        - grid: Toggle cell in grid sequencer pattern
        """
        if self._grid_mode == 'hardware':
            self._on_cell_clicked_hardware(column, cell)
        elif self._grid_mode == 'column':
            self._on_cell_clicked_column(column, cell)
        else:  # 'grid'
            self._on_cell_clicked_grid(column, cell)

    def _on_cell_clicked_hardware(self, column: int, cell: int):
        """Handle cell click in hardware mode."""
        # Get current state BEFORE toggling to predict new state
        current = self._adapter.state.get_cell(column, cell)
        if current is None:
            new_value = self._adapter.state.get_active_emitter()
        else:
            new_value = None

        # Schedule the async operation
        self._schedule_async(self._adapter.toggle_cell(column, cell))

        # Update grid immediately with predicted new value for responsiveness
        self._cell_grid.set_cell(column, cell, new_value)

    def _on_cell_clicked_column(self, column: int, cell: int):
        """Handle cell click in column sequencer mode."""
        # Get current pattern cell state
        pattern = self._adapter.state.get_column_pattern(column)
        current = pattern.get(cell)
        emitter = self._adapter.state.get_active_emitter()

        if current is None:
            # Empty cell - add with active emitter
            self._adapter.set_column_pattern_cell(column, cell, True, emitter)
            self._cell_grid.set_cell(column, cell, emitter)
        else:
            # Occupied cell - clear it
            self._adapter.set_column_pattern_cell(column, cell, False, emitter)
            self._cell_grid.clear_cell(column, cell)

        # Update running sequencer if active
        self._schedule_async(self._adapter.update_running_column_pattern(column))

    def _on_cell_clicked_grid(self, column: int, cell: int):
        """Handle cell click in grid sequencer mode."""
        # Convert (column, cell) to step_index
        step_index = ((column - 1) * 8) + (cell - 1)

        # Get current pattern cell state
        pattern = self._adapter.state.get_grid_pattern()
        current = pattern.get(step_index)
        emitter = self._adapter.state.get_active_emitter()

        if current is None:
            # Empty cell - add with active emitter
            self._adapter.set_grid_pattern_cell(step_index, True, emitter)
            self._cell_grid.set_cell(column, cell, emitter)
        else:
            # Occupied cell - clear it
            self._adapter.set_grid_pattern_cell(step_index, False, emitter)
            self._cell_grid.clear_cell(column, cell)

        # Update running sequencer if active
        self._schedule_async(self._adapter.update_running_grid_pattern())

    def _on_cell_right_clicked(self, column: int, cell: int):
        """Handle cell right-click (clear).

        Behavior depends on current grid mode:
        - hardware: Remove emitter from Tempera hardware cell
        - column: Remove cell from column sequencer pattern
        - grid: Remove cell from grid sequencer pattern
        """
        if self._grid_mode == 'hardware':
            self._schedule_async(self._adapter.remove_from_cell(column, cell))
            self._cell_grid.clear_cell(column, cell)
        elif self._grid_mode == 'column':
            emitter = self._adapter.state.get_active_emitter()
            self._adapter.set_column_pattern_cell(column, cell, False, emitter)
            self._cell_grid.clear_cell(column, cell)
            self._schedule_async(self._adapter.update_running_column_pattern(column))
        else:  # 'grid'
            step_index = ((column - 1) * 8) + (cell - 1)
            emitter = self._adapter.state.get_active_emitter()
            self._adapter.set_grid_pattern_cell(step_index, False, emitter)
            self._cell_grid.clear_cell(column, cell)
            self._schedule_async(self._adapter.update_running_grid_pattern())

    def _on_track_volume_changed(self, track_num: int, value: int):
        """Handle track volume change during drag."""
        self._adapter.set_track_volume(track_num, value, immediate=False)

    def _on_track_volume_set(self, track_num: int, value: int):
        """Handle track volume set on release."""
        self._adapter.set_track_volume(track_num, value, immediate=True)

    def _on_track_record(self, track_num: int):
        """Handle track record button."""
        self._schedule_async(self._adapter.track_record_on(track_num))

    def _on_modulator_size_changed(self, value: int):
        """Handle modulator size change during drag."""
        self._adapter.set_modulator_size(value, immediate=False)

    def _on_modulator_size_set(self, value: int):
        """Handle modulator size set on release."""
        self._adapter.set_modulator_size(value, immediate=True)

    def _on_modulator_selected(self, modulator_num: int):
        """Handle modulator selection change."""
        self._adapter.set_modulator_selected(modulator_num)
        # Update envelope panel to show the newly selected modulator's envelope
        self._update_envelope_panel_for_focus()

    def _on_global_param_changed(self, category: str, param: str, value: int):
        """Handle global parameter change during drag."""
        self._adapter.set_global_param(category, param, value, immediate=False)

    def _on_global_param_set(self, category: str, param: str, value: int):
        """Handle global parameter set on release."""
        self._adapter.set_global_param(category, param, value, immediate=True)

    def _on_play(self):
        """Handle play button/shortcut.

        If a sequencer is selected, starts that sequencer.
        Otherwise, plays a single note on the active emitter.
        """
        seq_type = self._transport.get_sequencer()
        if seq_type is not None:
            # Start the selected sequencer
            self._schedule_async(self._adapter.start_sequencer())
        else:
            # No sequencer selected, play a single note
            self._schedule_async(self._adapter.play_note())

    def _on_stop(self):
        """Handle stop button/shortcut.

        If a sequencer is running, stops it.
        Also sends MIDI stop message.
        """
        self._schedule_async(self._do_stop())

    async def _do_stop(self):
        """Stop sequencer and send MIDI stop."""
        await self._adapter.stop_sequencer()
        await self._adapter.transport_stop()

    def _on_sequencer_changed(self, seq_type):
        """Handle sequencer type selection change.

        Args:
            seq_type: 'column' for 8 Track, 'grid' for 1 Track, or None for neither.
        """
        if seq_type is not None:
            self._adapter.set_sequencer_mode(seq_type)
            # Sync BPM to adapter when sequencer is selected
            bpm = self._transport.get_bpm()
            self._adapter.set_sequencer_bpm(bpm)

        # Switch grid mode based on sequencer selection
        if seq_type is None:
            self._switch_grid_mode('hardware')
            # Stop the sequencer and hide the playhead when no sequencer is selected
            self._schedule_async(self._adapter.stop_sequencer())
            self._envelope_panel.set_playhead_position(None)
        elif seq_type == 'column':
            self._switch_grid_mode('column')
        else:
            self._switch_grid_mode('grid')

    def _switch_grid_mode(self, mode: str):
        """Switch the grid display mode.

        Args:
            mode: 'hardware', 'column', or 'grid'
        """
        self._grid_mode = mode

        # Clear grid and load appropriate data
        self._cell_grid.clear_all()

        if mode == 'hardware':
            self._cell_grid.set_all_cells(self._adapter.state.state['cells'])
        elif mode == 'column':
            self._load_column_patterns_to_grid()
        else:  # 'grid'
            self._load_grid_pattern_to_grid()

    def _load_column_patterns_to_grid(self):
        """Load column sequencer patterns to the grid display."""
        state = self._adapter.state.state
        cells = {}
        for col in range(1, 9):
            pattern = state['sequencer']['column_patterns'].get(col, {})
            for cell, emitter in pattern.items():
                cells[(col, cell)] = emitter
        self._cell_grid.set_all_cells(cells)

    def _load_grid_pattern_to_grid(self):
        """Load grid sequencer pattern to the grid display.

        Grid pattern uses step indices 0-63 which map to columns/cells:
        - column = (step_index // 8) + 1
        - cell = (step_index % 8) + 1
        """
        state = self._adapter.state.state
        cells = {}
        for step_index, emitter in state['sequencer']['grid_pattern'].items():
            column = (step_index // 8) + 1
            cell = (step_index % 8) + 1
            cells[(column, cell)] = emitter
        self._cell_grid.set_all_cells(cells)

    def _on_bpm_changed(self, bpm: int):
        """Handle BPM change from transport."""
        self._adapter.set_sequencer_bpm(bpm)

    def _on_state_changed(self, path: str, value):
        """Handle state change notifications (for undo/redo)."""
        if path == '*':
            # Full state restore
            self._sync_ui_from_state()

    # --- Navigation handlers ---

    def _ensure_section_panel_focused(self, section: Section):
        """Ensure the panel for the given section is focused and all others are not.

        This is the ONLY place panel highlighting should be managed to ensure
        exactly one section is highlighted at a time.

        Args:
            section: The section to focus. If GRID, all panels will be unfocused.
        """
        section_panels = {
            Section.EMITTER: self._emitter_panel,
            Section.GLOBAL: self._global_panel,
            Section.TRACKS: self._track_panel,
        }

        for sec, panel in section_panels.items():
            panel.set_panel_focused(sec == section)

    def _on_section_changed(self, section: Section):
        """Handle navigation section change."""
        # Ensure exactly one panel is focused
        self._ensure_section_panel_focused(section)

        # Set Qt focus for keyboard events
        section_widgets = {
            Section.GRID: self._cell_grid,
            Section.EMITTER: self._emitter_panel,
            Section.TRACKS: self._track_panel,
            Section.GLOBAL: self._global_panel,
        }
        widget = section_widgets.get(section)
        if widget:
            widget.setFocus()

        # Update envelope panel for new section
        self._update_envelope_panel_for_focus()

    def _on_nav_path_changed(self, path: str):
        """Handle navigation path update for status bar."""
        # Only show navigation path when actively navigating
        if hasattr(self, '_nav') and self._nav.mode.name != 'SECTION':
            self._status_bar.showMessage(path)

    def _on_nav_action(self, action: str):
        """Handle navigation action from NavigationManager."""
        # Grid navigation actions
        if action == 'grid_up':
            self._cell_grid.move_cursor_up()
        elif action == 'grid_down':
            self._cell_grid.move_cursor_down()
        elif action == 'grid_left':
            self._cell_grid.move_cursor_left()
        elif action == 'grid_right':
            self._cell_grid.move_cursor_right()
        elif action == 'toggle_cell':
            if self._nav.section == Section.GRID:
                self._cell_grid.toggle_cell_at_cursor()
        elif action == 'reset_default':
            # Reset focused control to default
            self._reset_focused_control()
        elif action == 'toggle_envelope':
            # Toggle envelope for focused control
            self._toggle_focused_envelope()

    def _on_subsection_changed(self, index: int):
        """Handle subsection focus change from NavigationManager."""
        section = self._nav.section

        # CRITICAL: Ensure parent panel is focused and others are cleared
        self._ensure_section_panel_focused(section)

        if section == Section.GLOBAL:
            self._global_panel.set_subsection_focus(index)
        elif section == Section.EMITTER:
            self._emitter_panel.set_subsection_focus(index)
        elif section == Section.TRACKS:
            # Track panel shows track focus in control mode
            if index >= 0:
                self._track_panel.set_track_focus(index + 1)

        # Update envelope panel to show envelope for newly focused control
        self._update_envelope_panel_for_focus()

    def _on_control_changed(self, index: int):
        """Handle control focus change from NavigationManager.

        NOTE: This handler does NOT call _ensure_section_panel_focused() because:
        1. If section changed, _on_section_changed was already called first
        2. _on_subsection_changed was already called and set the subsection highlight
        Calling _ensure_section_panel_focused() here would clear that subsection highlight.
        """
        section = self._nav.section

        if section == Section.GLOBAL:
            self._global_panel.enter_control_mode(index)
        elif section == Section.EMITTER:
            self._emitter_panel.enter_control_mode(index)
        elif section == Section.TRACKS:
            self._track_panel.enter_control_mode(index)

        # Update envelope panel for newly focused control
        self._update_envelope_panel_for_focus()

    def _on_mode_changed(self, mode: NavigationMode):
        """Handle mode change from NavigationManager.

        NOTE: This handler does NOT call _ensure_section_panel_focused() because
        modeChanged is emitted AFTER sectionChanged/subsectionChanged/controlChanged.
        Those handlers already ensure the correct panel is focused. Calling it here
        would clear the subsection/control highlighting that was just set.
        """
        section = self._nav.section

        # When switching to SECTION mode, clear all subsection/control state on panels
        if mode == NavigationMode.SECTION:
            if section == Section.GLOBAL:
                self._global_panel.exit_control_mode()
                # Clear subsection highlighting
                for group in self._global_panel.slider_groups:
                    group.set_group_focused(False)
            elif section == Section.EMITTER:
                self._emitter_panel.exit_control_mode()
                # Clear subsection highlighting
                for group in self._emitter_panel.slider_groups:
                    group.set_group_focused(False)
            elif section == Section.TRACKS:
                self._track_panel.exit_control_mode()

        # When switching back to SUBSECTION mode, exit control mode on panels
        elif mode == NavigationMode.SUBSECTION:
            if section == Section.GLOBAL:
                self._global_panel.exit_control_mode()
            elif section == Section.EMITTER:
                self._emitter_panel.exit_control_mode()
            elif section == Section.TRACKS:
                self._track_panel.exit_control_mode()

    # Note: _on_panel_subsection_navigated and _on_panel_control_navigated have been
    # removed. NavigationManager now handles all navigation via navigate_prev/navigate_next,
    # and panels are purely reactive to NavigationManager signals.

    def _on_value_adjust(self, delta: int):
        """Handle value adjustment from NavigationManager."""
        section = self._nav.section
        if section == Section.GLOBAL:
            subsection = self._nav.subsection
            control = self._nav.control
            if subsection == 5:  # Modulator
                if control == 0:
                    # Dropdown - adjust modulator selection
                    self._global_panel.adjust_modulator_selection(delta)
                else:
                    # Slider - adjust modulator size
                    self._global_panel.adjust_modulator_size(delta)
            elif subsection < 5:
                groups = self._global_panel.slider_groups
                if 0 <= subsection < len(groups):
                    groups[subsection].adjust_focused_value(delta)
        elif section == Section.EMITTER:
            subsection = self._nav.subsection
            groups = self._emitter_panel.slider_groups
            if 0 <= subsection < len(groups):
                groups[subsection].adjust_focused_value(delta)
        elif section == Section.TRACKS:
            # Track volume adjustment - uses visually focused track
            self._track_panel.adjust_focused_volume(delta)

    def _reset_focused_control(self):
        """Reset the currently focused control to its default value."""
        section = self._nav.section
        if section == Section.GLOBAL:
            subsection = self._nav.subsection
            if subsection == 5:  # Modulator
                self._global_panel.set_modulator_size(0)
                self._global_panel.modulatorSizeChanged.emit(0)
                self._global_panel.modulatorSizeSet.emit(0)
            elif subsection < 5:
                groups = self._global_panel.slider_groups
                if 0 <= subsection < len(groups):
                    groups[subsection].reset_focused_to_default()
        elif section == Section.EMITTER:
            subsection = self._nav.subsection
            groups = self._emitter_panel.slider_groups
            if 0 <= subsection < len(groups):
                groups[subsection].reset_focused_to_default()

    def _show_shortcuts_dialog(self):
        """Show the keyboard shortcuts reference dialog."""
        dialog = ShortcutsDialog(self)
        dialog.exec()

    # --- Envelope handlers ---

    def _get_focused_control_key(self) -> tuple[str, str]:
        """Get the control key and display name for the currently focused control.

        Returns:
            Tuple of (control_key, display_name) or (None, None) if no control focused.
        """
        section = self._nav.section
        subsection = self._nav.subsection
        control = self._nav.control

        if section == Section.EMITTER:
            emitter_num = self._adapter.state.get_active_emitter()
            # Map subsection + control to parameter
            # Subsection 0: Basic (volume, octave, effects_send)
            # Subsection 1: Tone Filter (tone_filter_width, tone_filter_center)
            # Subsection 2: Grain (grain_length_cell, grain_length_note, grain_density,
            #                      grain_shape, grain_shape_attack, grain_pan, grain_tune_spread)
            # Subsection 3: Position/Spray (relative_x, relative_y, spray_x, spray_y)
            params_by_subsection = [
                [('volume', 'Volume'), ('octave', 'Octave'), ('effects_send', 'Effects Send')],
                [('tone_filter_width', 'Filter Width'), ('tone_filter_center', 'Filter Center')],
                [('grain_length_cell', 'Grain Length Cell'), ('grain_length_note', 'Grain Length Note'),
                 ('grain_density', 'Grain Density'), ('grain_shape', 'Grain Shape'),
                 ('grain_shape_attack', 'Grain Shape Attack'), ('grain_pan', 'Grain Pan'),
                 ('grain_tune_spread', 'Grain Tune Spread')],
                [('relative_x', 'Position X'), ('relative_y', 'Position Y'),
                 ('spray_x', 'Spray X'), ('spray_y', 'Spray Y')],
            ]
            if 0 <= subsection < len(params_by_subsection):
                params = params_by_subsection[subsection]
                if 0 <= control < len(params):
                    param, name = params[control]
                    return f'emitter.{emitter_num}.{param}', f'Emitter {emitter_num} - {name}'

        elif section == Section.TRACKS:
            track_num = subsection + 1
            if 1 <= track_num <= 8:
                return f'track.{track_num}.volume', f'Track {track_num} - Volume'

        elif section == Section.GLOBAL:
            # Map subsection + control to global parameter
            # Subsection 0: ADSR (attack, decay, sustain, release)
            # Subsection 1: Reverb (size, color, mix)
            # Subsection 2: Delay (feedback, time, color, mix)
            # Subsection 3: Filter (cutoff, resonance)
            # Subsection 4: Chorus (depth, speed, flange, mix)
            # Subsection 5: Modulator (dropdown, size slider)
            #   - Both controls (dropdown and slider) show envelope for selected modulator

            # Special handling for modulator subsection
            if subsection == 5:
                # Both controls (dropdown index 0, slider index 1) show the same envelope
                # for the currently selected modulator
                selected_mod = self._adapter.state.get_modulator_selected()
                return f'global.modulator.{selected_mod}.size', f'Modulator {selected_mod}'

            params_by_subsection = [
                [('adsr', 'attack', 'ADSR Attack'), ('adsr', 'decay', 'ADSR Decay'),
                 ('adsr', 'sustain', 'ADSR Sustain'), ('adsr', 'release', 'ADSR Release')],
                [('reverb', 'size', 'Reverb Size'), ('reverb', 'color', 'Reverb Color'),
                 ('reverb', 'mix', 'Reverb Mix')],
                [('delay', 'feedback', 'Delay Feedback'), ('delay', 'time', 'Delay Time'),
                 ('delay', 'color', 'Delay Color'), ('delay', 'mix', 'Delay Mix')],
                [('filter', 'cutoff', 'Filter Cutoff'), ('filter', 'resonance', 'Filter Resonance')],
                [('chorus', 'depth', 'Chorus Depth'), ('chorus', 'speed', 'Chorus Speed'),
                 ('chorus', 'flange', 'Chorus Flange'), ('chorus', 'mix', 'Chorus Mix')],
            ]
            if 0 <= subsection < len(params_by_subsection):
                params = params_by_subsection[subsection]
                if 0 <= control < len(params):
                    category, param, name = params[control]
                    return f'global.{category}.{param}', name

        return None, None

    def _update_envelope_panel_for_focus(self):
        """Update envelope panel to show envelope for focused control."""
        control_key, display_name = self._get_focused_control_key()
        if control_key:
            envelope = self._adapter.state.get_envelope(control_key)
            self._envelope_panel.set_control(control_key, envelope, display_name)
        else:
            self._envelope_panel.set_control(None, None, None)

    def _toggle_focused_envelope(self):
        """Toggle envelope for the currently focused control."""
        control_key, _ = self._get_focused_control_key()
        if control_key:
            self._envelope_panel.toggle_enabled()

    def _on_envelope_changed(self, control_key: str, envelope):
        """Handle envelope modification from panel."""
        self._adapter.state.set_envelope(control_key, envelope)

    def _on_envelope_toggled(self, control_key: str, enabled: bool):
        """Handle envelope enable/disable from panel."""
        self._adapter.state.set_envelope_enabled(control_key, enabled)

    def _on_envelope_position(self, position: float):
        """Handle envelope position update for playhead display."""
        self._envelope_panel.set_playhead_position(position)

    def closeEvent(self, event):
        """Handle window close."""
        self._schedule_async(self._adapter.disconnect())
        event.accept()


def run_app():
    """Run the Tempera GUI application."""
    app = QApplication(sys.argv)
    app.setStyleSheet(MAIN_STYLESHEET)

    # Set up asyncio event loop with Qt integration
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Create adapter and main window
    adapter = TemperaAdapter()
    window = MainWindow(adapter)
    window.show()

    # Auto-connect to Tempera
    async def auto_connect():
        await adapter.connect()

    asyncio.ensure_future(auto_connect())

    # Run the event loop
    with loop:
        loop.run_forever()


if __name__ == '__main__':
    run_app()
