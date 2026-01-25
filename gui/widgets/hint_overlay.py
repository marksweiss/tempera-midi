"""Keyboard shortcut hint overlay system for Tempera GUI."""

from typing import Optional

from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from gui.styles import HINT_BADGE_STYLE
from gui.preferences import get_preferences, KeyboardLayout


class HintBadge(QLabel):
    """
    Small floating badge showing a keyboard shortcut hint.

    Displays a key name (e.g., "W", "Tab", "Space") near a control.
    """

    def __init__(self, key_text: str, parent: QWidget = None):
        """
        Create a hint badge.

        Args:
            key_text: The key to display (e.g., "W", "Tab")
            parent: Parent widget
        """
        super().__init__(key_text, parent)
        self.setStyleSheet(HINT_BADGE_STYLE)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

    def set_key(self, key_text: str):
        """Update the key text displayed."""
        self.setText(key_text)
        self.adjustSize()


class HintOverlay(QWidget):
    """
    Manages keyboard shortcut hint badges across the application.

    Creates and positions hint badges near relevant controls.
    Visibility is controlled by user preference.
    Badge text updates when keyboard layout changes.
    """

    def __init__(self, main_window: QWidget):
        """
        Initialize the hint overlay.

        Args:
            main_window: The main application window
        """
        super().__init__(main_window)
        self._main_window = main_window
        self._prefs = get_preferences()

        # Dictionary of hint badges: (widget, position) -> HintBadge
        self._badges: dict[tuple[QWidget, str], HintBadge] = {}

        # Hints configuration: list of (widget_attr, position, action_name, offset)
        # position: 'top', 'bottom', 'left', 'right'
        # action_name: key in the layout maps
        self._hint_configs: list[tuple[str, str, str, tuple[int, int]]] = []

        # Make overlay transparent to mouse events
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Connect to preference changes
        self._prefs.hintsVisibleChanged.connect(self._on_visibility_changed)
        self._prefs.keyboardLayoutChanged.connect(self._on_layout_changed)

        # Initial visibility
        self.setVisible(self._prefs.hints_visible)

        # Delay initial setup to allow widgets to be created
        QTimer.singleShot(100, self._setup_hints)

    def _setup_hints(self):
        """Set up hint badges for all relevant controls."""
        # Get references to widgets from main window
        try:
            cell_grid = self._main_window._cell_grid
            emitter_panel = self._main_window._emitter_panel
            track_panel = self._main_window._track_panel
            global_panel = self._main_window._global_panel
        except AttributeError:
            # Widgets not ready yet
            QTimer.singleShot(100, self._setup_hints)
            return

        # Create section hint badges
        self._create_section_hints(cell_grid, emitter_panel, track_panel, global_panel)

        # Update all badge texts for current layout
        self._update_badge_texts()

    def _create_section_hints(self, cell_grid, emitter_panel, track_panel, global_panel):
        """Create hint badges for section navigation.

        Only shows section jump keys (Q/E/T/G for left-hand, Home/End for right-hand).
        Grid navigation hints (W/A/S/D) are not shown as they would clutter the UI.
        """
        # Grid section hint - positioned inside the grid area (no title to avoid)
        self._add_badge(cell_grid, 'inside-top-left', 'section_grid', (8, 8))

        # Emitter section hint - positioned to the left of the title
        self._add_badge(emitter_panel, 'title-left', 'section_emitter', (0, 0))

        # Tracks section hint - positioned to the left of the title
        self._add_badge(track_panel, 'title-left', 'section_tracks', (0, 0))

        # Global section hint - positioned to the left of the title
        self._add_badge(global_panel, 'title-left', 'section_global', (0, 0))

    def _add_badge(
        self,
        widget: QWidget,
        position: str,
        action: str,
        offset: tuple[int, int] = (0, 0)
    ):
        """Add a hint badge for a widget.

        Args:
            widget: The widget to attach the badge to
            position: 'top', 'bottom', 'left', 'right', 'center', 'top-left', etc.
            action: The action name from the key maps
            offset: (x, y) offset from calculated position
        """
        badge = HintBadge('', self._main_window)
        badge.setProperty('action', action)
        badge.setProperty('target_widget', widget)
        badge.setProperty('position', position)
        badge.setProperty('offset', offset)

        self._badges[(widget, position)] = badge

    def _update_badge_texts(self):
        """Update all badge texts based on current keyboard layout."""
        from gui.shortcuts import LEFT_HAND_KEYS, RIGHT_HAND_KEYS, SHARED_KEYS

        layout = self._prefs.keyboard_layout
        keys = LEFT_HAND_KEYS if layout == KeyboardLayout.LEFT_HAND else RIGHT_HAND_KEYS

        for (widget, position), badge in self._badges.items():
            action = badge.property('action')
            key_text = keys.get(action) or SHARED_KEYS.get(action) or ''

            if key_text:
                # Simplify key text for display
                key_text = self._simplify_key(key_text)
                badge.set_key(key_text)
            else:
                badge.hide()

    def _simplify_key(self, key: str) -> str:
        """Simplify a key sequence for compact display."""
        # Remove modifier prefixes for single keys
        key = key.replace('Shift+', '')

        # Shorten common key names
        replacements = {
            'Space': 'Spc',
            'Return': 'Ret',
            'Escape': 'Esc',
            'Delete': 'Del',
            'PgDown': 'PgD',
            'PgUp': 'PgU',
        }
        return replacements.get(key, key)

    def _position_badges(self):
        """Position all badges relative to their target widgets.

        Badges are clamped to stay within window bounds to prevent cutoff.
        """
        window_rect = self._main_window.rect()
        margin = 4  # Minimum margin from window edges

        for (widget, position), badge in self._badges.items():
            if not badge.text():
                badge.hide()
                continue

            # Get widget position in main window coordinates
            target = badge.property('target_widget')
            if not target or not target.isVisible():
                badge.hide()
                continue

            # Calculate position
            widget_rect = target.rect()
            global_pos = target.mapToGlobal(widget_rect.topLeft())
            local_pos = self._main_window.mapFromGlobal(global_pos)

            offset = badge.property('offset') or (0, 0)
            badge_size = badge.sizeHint()

            if position == 'top':
                x = local_pos.x() + widget_rect.width() // 2 - badge_size.width() // 2
                y = local_pos.y() - badge_size.height()
            elif position == 'bottom':
                x = local_pos.x() + widget_rect.width() // 2 - badge_size.width() // 2
                y = local_pos.y() + widget_rect.height()
            elif position == 'left':
                x = local_pos.x() - badge_size.width()
                y = local_pos.y() + widget_rect.height() // 2 - badge_size.height() // 2
            elif position == 'right':
                x = local_pos.x() + widget_rect.width()
                y = local_pos.y() + widget_rect.height() // 2 - badge_size.height() // 2
            elif position == 'center':
                x = local_pos.x() + widget_rect.width() // 2 - badge_size.width() // 2
                y = local_pos.y() + widget_rect.height() // 2 - badge_size.height() // 2
            elif position == 'top-left':
                x = local_pos.x()
                y = local_pos.y() - badge_size.height()
            elif position == 'top-right':
                x = local_pos.x() + widget_rect.width() - badge_size.width()
                y = local_pos.y() - badge_size.height()
            elif position == 'inside-top-left':
                # Position inside the widget, near top-left corner
                x = local_pos.x()
                y = local_pos.y()
            elif position == 'title-left':
                # Position OUTSIDE the widget, to the left of the title
                # Title is in the margin-top area (12px margin-top in styles)
                x = local_pos.x() - badge_size.width() - 4  # Outside widget, 4px gap
                y = local_pos.y() - 10 + badge_size.height()  # Top of badge aligns with title text top
            else:
                x = local_pos.x()
                y = local_pos.y()

            # Apply offset
            x += offset[0]
            y += offset[1]

            # Clamp to window bounds to prevent cutoff
            x = max(margin, min(x, window_rect.width() - badge_size.width() - margin))
            y = max(margin, min(y, window_rect.height() - badge_size.height() - margin))

            badge.move(int(x), int(y))
            badge.show()
            badge.raise_()

    def _on_visibility_changed(self, visible: bool):
        """Handle hints visibility preference change."""
        if visible:
            self._update_badge_texts()
            self._position_badges()
            for badge in self._badges.values():
                if badge.text():
                    badge.show()
        else:
            for badge in self._badges.values():
                badge.hide()

    def _on_layout_changed(self, layout: KeyboardLayout):
        """Handle keyboard layout preference change."""
        self._update_badge_texts()
        if self._prefs.hints_visible:
            self._position_badges()

    def showEvent(self, event):
        """Handle show event - position badges."""
        super().showEvent(event)
        if self._prefs.hints_visible:
            self._position_badges()

    def resizeEvent(self, event):
        """Handle resize - reposition badges."""
        super().resizeEvent(event)
        if self._prefs.hints_visible:
            self._position_badges()


def create_hint_overlay(main_window: QWidget) -> HintOverlay:
    """Create and return a hint overlay for the main window."""
    return HintOverlay(main_window)
