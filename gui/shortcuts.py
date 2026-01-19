"""Keyboard shortcut management for Tempera GUI."""

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget


class ShortcutManager:
    """
    Manages keyboard shortcuts for the Tempera GUI.

    Uses QShortcut which works alongside mouse events without blocking,
    enabling concurrent keyboard + mouse input.

    Default bindings:
    - 1-4: Select emitter 1-4
    - Space/Return: Play note
    - Escape: Stop
    - E: Focus emitter panel
    - C: Focus cell grid
    - T: Focus track panel
    - G: Focus global panel
    - Ctrl+Z: Undo
    - Ctrl+Shift+Z: Redo
    - Ctrl+S: Save preset
    - Ctrl+O: Load preset
    """

    def __init__(self, parent: QWidget):
        """
        Initialize shortcut manager.

        Args:
            parent: Parent widget for shortcuts (typically MainWindow)
        """
        self._parent = parent
        self._shortcuts: dict[str, QShortcut] = {}
        self._callbacks: dict[str, Callable] = {}

    def register(self, name: str, key_sequence: str, callback: Callable):
        """
        Register a keyboard shortcut.

        Args:
            name: Unique name for the shortcut
            key_sequence: Key sequence string (e.g., "Ctrl+Z", "1", "Space")
            callback: Function to call when shortcut triggered
        """
        shortcut = QShortcut(QKeySequence(key_sequence), self._parent)
        shortcut.activated.connect(callback)
        self._shortcuts[name] = shortcut
        self._callbacks[name] = callback

    def unregister(self, name: str):
        """Unregister a shortcut by name."""
        if name in self._shortcuts:
            shortcut = self._shortcuts.pop(name)
            shortcut.setEnabled(False)
            shortcut.deleteLater()
            self._callbacks.pop(name, None)

    def set_enabled(self, name: str, enabled: bool):
        """Enable or disable a shortcut."""
        if name in self._shortcuts:
            self._shortcuts[name].setEnabled(enabled)

    def set_all_enabled(self, enabled: bool):
        """Enable or disable all shortcuts."""
        for shortcut in self._shortcuts.values():
            shortcut.setEnabled(enabled)

    def setup_defaults(
        self,
        select_emitter: Callable[[int], None],
        play: Callable[[], None],
        stop: Callable[[], None],
        focus_emitter: Callable[[], None],
        focus_grid: Callable[[], None],
        focus_tracks: Callable[[], None],
        focus_global: Callable[[], None],
        undo: Callable[[], None],
        redo: Callable[[], None],
        save_preset: Callable[[], None],
        load_preset: Callable[[], None],
    ):
        """
        Set up all default shortcuts.

        Args:
            select_emitter: Callback for emitter selection (receives emitter num 1-4)
            play: Callback for play action
            stop: Callback for stop action
            focus_emitter: Callback to focus emitter panel
            focus_grid: Callback to focus cell grid
            focus_tracks: Callback to focus track panel
            focus_global: Callback to focus global panel
            undo: Callback for undo
            redo: Callback for redo
            save_preset: Callback for save preset
            load_preset: Callback for load preset
        """
        # Emitter selection
        for i in range(1, 5):
            self.register(f'emitter_{i}', str(i), lambda n=i: select_emitter(n))

        # Transport
        self.register('play_space', 'Space', play)
        self.register('play_return', 'Return', play)
        self.register('stop', 'Escape', stop)

        # Focus navigation
        self.register('focus_emitter', 'E', focus_emitter)
        self.register('focus_grid', 'C', focus_grid)
        self.register('focus_tracks', 'T', focus_tracks)
        self.register('focus_global', 'G', focus_global)

        # Edit
        self.register('undo', 'Ctrl+Z', undo)
        self.register('redo', 'Ctrl+Shift+Z', redo)

        # File
        self.register('save_preset', 'Ctrl+S', save_preset)
        self.register('load_preset', 'Ctrl+O', load_preset)

    def get_shortcut_text(self, name: str) -> str:
        """Get the key sequence text for a shortcut."""
        if name in self._shortcuts:
            return self._shortcuts[name].key().toString()
        return ''
