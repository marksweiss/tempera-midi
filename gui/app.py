"""Main application window and entry point for Tempera GUI."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMenuBar, QMenu, QFileDialog, QMessageBox
)

import qasync

from gui.adapter import TemperaAdapter
from gui.widgets import (
    CellGrid, EmitterPanel, TrackPanel, GlobalPanel, TransportPanel
)
from gui.shortcuts import ShortcutManager
from gui.styles import MAIN_STYLESHEET


class MainWindow(QMainWindow):
    """
    Main application window for Tempera MIDI controller.

    Layout:
    - Left: Cell grid (8x8) + Transport controls
    - Right: Emitter panel (tabbed, most prominent)
    - Bottom: Track panel + Global effects panel
    """

    def __init__(self, adapter: TemperaAdapter):
        super().__init__()

        self._adapter = adapter
        self._adapter.set_status_callback(self._update_status)

        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()

        # Load initial state into UI
        self._sync_ui_from_state()

    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle('Tempera MIDI Controller')
        self.setMinimumSize(900, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Top section: Grid + Emitter panel
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left column: Grid + Transport
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        self._cell_grid = CellGrid()
        left_layout.addWidget(self._cell_grid)

        self._transport = TransportPanel()
        left_layout.addWidget(self._transport)

        left_layout.addStretch()
        top_splitter.addWidget(left_widget)

        # Right: Emitter panel
        self._emitter_panel = EmitterPanel()
        top_splitter.addWidget(self._emitter_panel)

        # Set splitter proportions (grid:emitter = 1:2)
        top_splitter.setSizes([300, 600])

        main_layout.addWidget(top_splitter, stretch=2)

        # Bottom section: Tracks + Global
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)

        self._track_panel = TrackPanel()
        bottom_splitter.addWidget(self._track_panel)

        self._global_panel = GlobalPanel()
        bottom_splitter.addWidget(self._global_panel)

        bottom_splitter.setSizes([400, 500])

        main_layout.addWidget(bottom_splitter, stretch=1)

        # Menu bar
        self._setup_menu()

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage('Not connected')

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

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        self._shortcuts = ShortcutManager(self)
        self._shortcuts.setup_defaults(
            select_emitter=self._on_select_emitter,
            play=self._on_play,
            stop=self._on_stop,
            focus_emitter=lambda: self._emitter_panel.setFocus(),
            focus_grid=lambda: self._cell_grid.setFocus(),
            focus_tracks=lambda: self._track_panel.setFocus(),
            focus_global=lambda: self._global_panel.setFocus(),
            undo=self._on_undo,
            redo=self._on_redo,
            save_preset=self._on_save_preset,
            load_preset=self._on_load_preset,
        )

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
        asyncio.ensure_future(self._adapter.toggle_cell(column, cell))
        # Update grid immediately for responsiveness
        current = self._adapter.state.get_cell(column, cell)
        self._cell_grid.set_cell(column, cell, current)

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
        """Handle play button/shortcut."""
        asyncio.ensure_future(self._adapter.play_note())

    def _on_stop(self):
        """Handle stop button/shortcut."""
        asyncio.ensure_future(self._adapter.transport_stop())

    def _on_state_changed(self, path: str, value):
        """Handle state change notifications (for undo/redo)."""
        if path == '*':
            # Full state restore
            self._sync_ui_from_state()

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
