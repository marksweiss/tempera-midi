"""Main application window and entry point for Tempera GUI."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QScreen, QAction, QActionGroup
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QMenuBar, QMenu, QFileDialog, QMessageBox
)

import qasync

from gui.adapter import TemperaAdapter
from gui.widgets import (
    CellGrid, EmitterPanel, TrackPanel, GlobalPanel, TransportPanel,
    create_hint_overlay, ShortcutsDialog
)
from gui.shortcuts import ShortcutManager, NavigationManager, Section, NavigationMode
from gui.preferences import KeyboardLayout, get_preferences
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

        self._setup_ui()
        self._setup_shortcuts()
        self._setup_navigation()
        self._connect_signals()

        # Create hint overlay (after UI is set up)
        self._hint_overlay = create_hint_overlay(self)

        # Load initial state into UI
        self._sync_ui_from_state()

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

        # Top section: Grid + Transport (left) | Emitter panel (right)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(16)

        # Left column: Cell grid + Transport (stacked vertically)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)

        self._cell_grid = CellGrid()
        left_layout.addWidget(self._cell_grid, alignment=Qt.AlignmentFlag.AlignTop)

        # Transport panel - constrained to cell grid width
        self._transport = TransportPanel()
        self._transport.setFixedWidth(grid_width)
        left_layout.addWidget(self._transport, alignment=Qt.AlignmentFlag.AlignTop)

        left_layout.addStretch()
        left_widget.setFixedWidth(grid_width + 8)  # Small margin
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
        bottom_layout.addWidget(self._track_panel, alignment=Qt.AlignmentFlag.AlignTop)

        self._global_panel = GlobalPanel()
        bottom_layout.addWidget(self._global_panel, stretch=1)

        main_layout.addLayout(bottom_layout, stretch=1)

        # Menu bar
        self._setup_menu()

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

    def _setup_menu(self):
        """Set up the menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu('File')

        connect_action = file_menu.addAction('Connect')
        connect_action.triggered.connect(self._on_connect)

        disconnect_action = file_menu.addAction('Disconnect')
        disconnect_action.triggered.connect(self._on_disconnect)

        file_menu.addSeparator()

        save_action = file_menu.addAction('Save Preset...')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self._on_save_preset)

        load_action = file_menu.addAction('Load Preset...')
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self._on_load_preset)

        file_menu.addSeparator()

        quit_action = file_menu.addAction('Quit')
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.close)

        # Edit menu
        edit_menu = menu_bar.addMenu('Edit')

        undo_action = edit_menu.addAction('Undo')
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self._on_undo)

        redo_action = edit_menu.addAction('Redo')
        redo_action.setShortcut('Ctrl+Shift+Z')
        redo_action.triggered.connect(self._on_redo)

        edit_menu.addSeparator()

        reset_action = edit_menu.addAction('Reset to Defaults')
        reset_action.triggered.connect(self._on_reset)

        # View menu
        view_menu = menu_bar.addMenu('View')

        # Keyboard Layout submenu
        layout_menu = view_menu.addMenu('Keyboard Layout')
        layout_group = QActionGroup(self)
        layout_group.setExclusive(True)

        self._left_hand_action = QAction('Left Hand (WASD)', self, checkable=True)
        self._left_hand_action.setChecked(
            self._prefs.keyboard_layout == KeyboardLayout.LEFT_HAND
        )
        self._left_hand_action.triggered.connect(
            lambda: self._set_keyboard_layout(KeyboardLayout.LEFT_HAND)
        )
        layout_group.addAction(self._left_hand_action)
        layout_menu.addAction(self._left_hand_action)

        self._right_hand_action = QAction('Right Hand (Arrows)', self, checkable=True)
        self._right_hand_action.setChecked(
            self._prefs.keyboard_layout == KeyboardLayout.RIGHT_HAND
        )
        self._right_hand_action.triggered.connect(
            lambda: self._set_keyboard_layout(KeyboardLayout.RIGHT_HAND)
        )
        layout_group.addAction(self._right_hand_action)
        layout_menu.addAction(self._right_hand_action)

        view_menu.addSeparator()

        # Show Keyboard Hints toggle
        self._hints_action = QAction('Show Keyboard Hints', self, checkable=True)
        self._hints_action.setShortcut('F1')
        self._hints_action.setChecked(self._prefs.hints_visible)
        self._hints_action.triggered.connect(self._toggle_hints)
        view_menu.addAction(self._hints_action)

        # Listen for preference changes to update menu state
        self._prefs.keyboardLayoutChanged.connect(self._on_layout_changed)
        self._prefs.hintsVisibleChanged.connect(self._on_hints_changed)

        # Help menu
        help_menu = menu_bar.addMenu('Help')

        shortcuts_action = help_menu.addAction('Keyboard Shortcuts...')
        shortcuts_action.setShortcut('Ctrl+/')
        shortcuts_action.triggered.connect(self._show_shortcuts_dialog)

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
        self._global_panel.modwheelChanged.connect(self._on_modwheel_changed)
        self._global_panel.modwheelSet.connect(self._on_modwheel_set)
        self._global_panel.parameterChanged.connect(self._on_global_param_changed)
        self._global_panel.parameterSet.connect(self._on_global_param_set)

        # Transport
        self._transport.playClicked.connect(self._on_play)
        self._transport.stopClicked.connect(self._on_stop)
        self._transport.sequencerChanged.connect(self._on_sequencer_changed)
        self._transport.bpmChanged.connect(self._on_bpm_changed)

        # State manager listener for undo/redo updates
        self._adapter.state.add_listener(self._on_state_changed)

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

        # Sync cells
        self._cell_grid.set_all_cells(state['cells'])

        # Sync active emitter
        self._emitter_panel.select_emitter(state['active_emitter'])
        self._cell_grid.set_active_emitter(state['active_emitter'])

    def _update_status(self, message: str):
        """Update status bar message."""
        self._status_bar.showMessage(message)

    # --- Event handlers ---

    def _on_connect(self):
        """Handle connect menu action."""
        asyncio.ensure_future(self._connect())

    async def _connect(self):
        """Connect to Tempera."""
        success = await self._adapter.connect()
        if success:
            self._sync_ui_from_state()

    def _on_disconnect(self):
        """Handle disconnect menu action."""
        asyncio.ensure_future(self._adapter.disconnect())

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
            asyncio.ensure_future(self._adapter.load_preset(Path(filepath)))
            self._sync_ui_from_state()

    def _on_undo(self):
        """Handle undo action."""
        asyncio.ensure_future(self._do_undo())

    async def _do_undo(self):
        if await self._adapter.undo():
            self._sync_ui_from_state()

    def _on_redo(self):
        """Handle redo action."""
        asyncio.ensure_future(self._do_redo())

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
            asyncio.ensure_future(self._adapter.reset_to_defaults())
            self._sync_ui_from_state()

    def _on_select_emitter(self, emitter_num: int):
        """Handle emitter selection via keyboard."""
        self._emitter_panel.select_emitter(emitter_num)

    def _on_emitter_selected(self, emitter_num: int):
        """Handle emitter selection from panel."""
        asyncio.ensure_future(self._adapter.set_active_emitter(emitter_num))
        self._cell_grid.set_active_emitter(emitter_num)

    def _on_emitter_param_changed(self, emitter_num: int, param: str, value: int):
        """Handle emitter parameter change during drag."""
        self._adapter.set_emitter_param(emitter_num, param, value, immediate=False)

    def _on_emitter_param_set(self, emitter_num: int, param: str, value: int):
        """Handle emitter parameter set on release."""
        self._adapter.set_emitter_param(emitter_num, param, value, immediate=True)

    def _on_cell_clicked(self, column: int, cell: int):
        """Handle cell click (left button)."""
        # Get current state BEFORE toggling to predict new state
        current = self._adapter.state.get_cell(column, cell)
        if current is None:
            # Cell is empty, will be set to active emitter
            new_value = self._adapter.state.get_active_emitter()
        else:
            # Cell has emitter, will be cleared
            new_value = None

        # Schedule the async operation
        asyncio.ensure_future(self._adapter.toggle_cell(column, cell))

        # Update grid immediately with predicted new value for responsiveness
        self._cell_grid.set_cell(column, cell, new_value)

    def _on_cell_right_clicked(self, column: int, cell: int):
        """Handle cell right-click (clear)."""
        asyncio.ensure_future(self._adapter.remove_from_cell(column, cell))
        self._cell_grid.clear_cell(column, cell)

    def _on_track_volume_changed(self, track_num: int, value: int):
        """Handle track volume change during drag."""
        self._adapter.set_track_volume(track_num, value, immediate=False)

    def _on_track_volume_set(self, track_num: int, value: int):
        """Handle track volume set on release."""
        self._adapter.set_track_volume(track_num, value, immediate=True)

    def _on_track_record(self, track_num: int):
        """Handle track record button."""
        asyncio.ensure_future(self._adapter.track_record_on(track_num))

    def _on_modwheel_changed(self, value: int):
        """Handle modwheel change during drag."""
        self._adapter.set_global_param('modwheel', None, value, immediate=False)

    def _on_modwheel_set(self, value: int):
        """Handle modwheel set on release."""
        self._adapter.set_global_param('modwheel', None, value, immediate=True)

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
            asyncio.ensure_future(self._adapter.start_sequencer())
        else:
            # No sequencer selected, play a single note
            asyncio.ensure_future(self._adapter.play_note())

    def _on_stop(self):
        """Handle stop button/shortcut.

        If a sequencer is running, stops it.
        Also sends MIDI stop message.
        """
        asyncio.ensure_future(self._do_stop())

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

    def _on_bpm_changed(self, bpm: int):
        """Handle BPM change from transport."""
        self._adapter.set_sequencer_bpm(bpm)

    def _on_state_changed(self, path: str, value):
        """Handle state change notifications (for undo/redo)."""
        if path == '*':
            # Full state restore
            self._sync_ui_from_state()

    # --- Navigation handlers ---

    def _on_section_changed(self, section: Section):
        """Handle navigation section change."""
        section_widgets = {
            Section.GRID: self._cell_grid,
            Section.EMITTER: self._emitter_panel,
            Section.TRACKS: self._track_panel,
            Section.GLOBAL: self._global_panel,
        }
        widget = section_widgets.get(section)
        if widget:
            widget.setFocus()

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

    def _on_subsection_changed(self, index: int):
        """Handle subsection focus change from NavigationManager."""
        section = self._nav.section
        if section == Section.GLOBAL:
            self._global_panel.set_subsection_focus(index)
        elif section == Section.EMITTER:
            self._emitter_panel.set_subsection_focus(index)
        elif section == Section.TRACKS:
            # Track panel shows track focus in control mode
            if index >= 0:
                self._track_panel.set_track_focus(index + 1)

    def _on_control_changed(self, index: int):
        """Handle control focus change from NavigationManager."""
        section = self._nav.section
        if section == Section.GLOBAL:
            self._global_panel.enter_control_mode()
        elif section == Section.EMITTER:
            self._emitter_panel.enter_control_mode()
        elif section == Section.TRACKS:
            self._track_panel.enter_control_mode()

    def _on_mode_changed(self, mode: NavigationMode):
        """Handle mode change from NavigationManager."""
        section = self._nav.section
        # When switching back to SUBSECTION mode, exit control mode on panels
        if mode == NavigationMode.SUBSECTION:
            if section == Section.GLOBAL:
                self._global_panel.exit_control_mode()
            elif section == Section.EMITTER:
                self._emitter_panel.exit_control_mode()
            elif section == Section.TRACKS:
                self._track_panel.exit_control_mode()

    def _on_value_adjust(self, delta: int):
        """Handle value adjustment from NavigationManager."""
        section = self._nav.section
        if section == Section.GLOBAL:
            subsection = self._nav.subsection
            if subsection == 4:  # Modwheel
                self._global_panel.adjust_modwheel(delta)
            elif subsection < 4:
                groups = self._global_panel.slider_groups
                if 0 <= subsection < len(groups):
                    groups[subsection].adjust_focused_value(delta)
        elif section == Section.EMITTER:
            subsection = self._nav.subsection
            groups = self._emitter_panel.slider_groups
            if 0 <= subsection < len(groups):
                groups[subsection].adjust_focused_value(delta)

    def _reset_focused_control(self):
        """Reset the currently focused control to its default value."""
        section = self._nav.section
        if section == Section.GLOBAL:
            subsection = self._nav.subsection
            if subsection == 4:  # Modwheel
                self._global_panel.set_modwheel(0)
                self._global_panel.modwheelChanged.emit(0)
                self._global_panel.modwheelSet.emit(0)
            elif subsection < 4:
                groups = self._global_panel.slider_groups
                if 0 <= subsection < len(groups):
                    groups[subsection].reset_focused_to_default()
        elif section == Section.EMITTER:
            subsection = self._nav.subsection
            groups = self._emitter_panel.slider_groups
            if 0 <= subsection < len(groups):
                groups[subsection].reset_focused_to_default()

    # --- View menu handlers ---

    def _set_keyboard_layout(self, layout: KeyboardLayout):
        """Set keyboard layout preference."""
        self._prefs.keyboard_layout = layout

    def _on_layout_changed(self, layout: KeyboardLayout):
        """Handle keyboard layout change."""
        self._left_hand_action.setChecked(layout == KeyboardLayout.LEFT_HAND)
        self._right_hand_action.setChecked(layout == KeyboardLayout.RIGHT_HAND)

    def _toggle_hints(self):
        """Toggle keyboard hints visibility."""
        self._prefs.toggle_hints()

    def _on_hints_changed(self, visible: bool):
        """Handle hints visibility change."""
        self._hints_action.setChecked(visible)
        # Update hint overlay visibility
        if hasattr(self, '_hint_overlay'):
            self._hint_overlay._on_visibility_changed(visible)

    def _show_shortcuts_dialog(self):
        """Show the keyboard shortcuts reference dialog."""
        dialog = ShortcutsDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        """Handle window close."""
        asyncio.ensure_future(self._adapter.disconnect())
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

    # Run the event loop
    with loop:
        loop.run_forever()


if __name__ == '__main__':
    run_app()
