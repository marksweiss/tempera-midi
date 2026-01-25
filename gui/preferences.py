"""User preferences management for Tempera GUI."""

from enum import Enum
from typing import Optional

from PySide6.QtCore import QSettings, Signal, QObject


class KeyboardLayout(Enum):
    """Keyboard layout options for one-handed navigation."""
    LEFT_HAND = 'left'   # WASD cluster
    RIGHT_HAND = 'right'  # Arrow cluster


class Preferences(QObject):
    """
    Manages persistent user preferences for the Tempera GUI.

    Uses QSettings for cross-platform storage:
    - macOS: ~/Library/Preferences/com.tempera.midi.plist
    - Windows: Registry HKEY_CURRENT_USER/Software/Tempera/MIDI
    - Linux: ~/.config/Tempera/MIDI.conf

    Signals:
        keyboardLayoutChanged(KeyboardLayout): Emitted when layout preference changes
        hintsVisibleChanged(bool): Emitted when hints visibility changes
    """

    keyboardLayoutChanged = Signal(KeyboardLayout)
    hintsVisibleChanged = Signal(bool)

    # Settings keys
    KEY_KEYBOARD_LAYOUT = 'navigation/keyboard_layout'
    KEY_HINTS_VISIBLE = 'navigation/hints_visible'

    # Defaults
    DEFAULT_KEYBOARD_LAYOUT = KeyboardLayout.LEFT_HAND
    DEFAULT_HINTS_VISIBLE = False

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize preferences with QSettings backend."""
        super().__init__(parent)
        self._settings = QSettings('Tempera', 'MIDI')

    @property
    def keyboard_layout(self) -> KeyboardLayout:
        """Get current keyboard layout preference."""
        value = self._settings.value(
            self.KEY_KEYBOARD_LAYOUT,
            self.DEFAULT_KEYBOARD_LAYOUT.value
        )
        try:
            return KeyboardLayout(value)
        except ValueError:
            return self.DEFAULT_KEYBOARD_LAYOUT

    @keyboard_layout.setter
    def keyboard_layout(self, layout: KeyboardLayout):
        """Set keyboard layout preference."""
        if layout != self.keyboard_layout:
            self._settings.setValue(self.KEY_KEYBOARD_LAYOUT, layout.value)
            self._settings.sync()
            self.keyboardLayoutChanged.emit(layout)

    @property
    def hints_visible(self) -> bool:
        """Get hints visibility preference."""
        return self._settings.value(
            self.KEY_HINTS_VISIBLE,
            self.DEFAULT_HINTS_VISIBLE,
            type=bool
        )

    @hints_visible.setter
    def hints_visible(self, visible: bool):
        """Set hints visibility preference."""
        if visible != self.hints_visible:
            self._settings.setValue(self.KEY_HINTS_VISIBLE, visible)
            self._settings.sync()
            self.hintsVisibleChanged.emit(visible)

    def toggle_hints(self):
        """Toggle hints visibility."""
        self.hints_visible = not self.hints_visible

    def toggle_layout(self):
        """Toggle between left-hand and right-hand layouts."""
        if self.keyboard_layout == KeyboardLayout.LEFT_HAND:
            self.keyboard_layout = KeyboardLayout.RIGHT_HAND
        else:
            self.keyboard_layout = KeyboardLayout.LEFT_HAND

    def reset_to_defaults(self):
        """Reset all preferences to defaults."""
        self.keyboard_layout = self.DEFAULT_KEYBOARD_LAYOUT
        self.hints_visible = self.DEFAULT_HINTS_VISIBLE


# Singleton instance for global access
_preferences: Optional[Preferences] = None


def get_preferences() -> Preferences:
    """Get the global Preferences instance."""
    global _preferences
    if _preferences is None:
        _preferences = Preferences()
    return _preferences
