"""Keyboard shortcuts reference dialog."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QWidget, QScrollArea, QFrame, QPushButton, QGridLayout
)

from gui.preferences import KeyboardLayout, get_preferences


class ShortcutsDialog(QDialog):
    """
    Dialog showing all available keyboard shortcuts.

    Displays shortcuts organized by category, with current layout highlighted.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._prefs = get_preferences()

        self.setWindowTitle('Keyboard Shortcuts')
        self.setMinimumSize(500, 600)

        self._setup_ui()

        # Update when layout changes
        self._prefs.keyboardLayoutChanged.connect(self._update_display)

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Header with layout toggle
        header = QHBoxLayout()
        header.addWidget(QLabel('Current Layout:'))

        self._layout_label = QLabel()
        self._layout_label.setStyleSheet('font-weight: bold; color: #4A90D9;')
        header.addWidget(self._layout_label)

        header.addStretch()

        toggle_btn = QPushButton('Switch Layout')
        toggle_btn.clicked.connect(self._toggle_layout)
        header.addWidget(toggle_btn)

        layout.addLayout(header)

        # Tab widget for categories
        tabs = QTabWidget()
        tabs.addTab(self._create_navigation_tab(), 'Navigation')
        tabs.addTab(self._create_grid_tab(), 'Grid')
        tabs.addTab(self._create_controls_tab(), 'Controls')
        tabs.addTab(self._create_global_tab(), 'Global')

        layout.addWidget(tabs)

        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self._update_display()

    def _create_navigation_tab(self) -> QWidget:
        """Create the navigation shortcuts tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Section navigation
        section_group = self._create_shortcut_group('Section Navigation', [
            ('Next Section', 'Tab', 'Page Down'),
            ('Previous Section', 'Shift+Tab', 'Page Up'),
            ('Go to Grid', 'Q', 'Home'),
            ('Go to Emitter', 'E', 'Insert'),
            ('Go to Tracks', 'T', '-'),
            ('Go to Global', 'G', 'End'),
        ])
        layout.addWidget(section_group)

        # Movement
        movement_group = self._create_shortcut_group('Movement', [
            ('Up / Previous', 'W', 'Up'),
            ('Down / Next', 'S', 'Down'),
            ('Left', 'A', 'Left'),
            ('Right', 'D', 'Right'),
        ])
        layout.addWidget(movement_group)

        # Focus
        focus_group = self._create_shortcut_group('Focus Control', [
            ('Toggle Focus Level', 'F', 'Enter'),
            ('(Section → Subsection → Control → back)', '', ''),
        ])
        layout.addWidget(focus_group)

        layout.addStretch()
        return widget

    def _create_grid_tab(self) -> QWidget:
        """Create the grid shortcuts tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        grid_group = self._create_shortcut_group('Grid Controls', [
            ('Move Cursor Up', 'W', 'Up'),
            ('Move Cursor Down', 'S', 'Down'),
            ('Move Cursor Left', 'A', 'Left'),
            ('Move Cursor Right', 'D', 'Right'),
            ('Toggle Cell', 'Space', 'Enter'),
            ('Clear Cell', 'X', 'Delete'),
        ])
        layout.addWidget(grid_group)

        layout.addStretch()
        return widget

    def _create_controls_tab(self) -> QWidget:
        """Create the slider controls shortcuts tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        adjust_group = self._create_shortcut_group('Value Adjustment', [
            ('Increase Value', 'D / Right', 'Right'),
            ('Decrease Value', 'A / Left', 'Left'),
            ('Increase +10', 'Shift+D', 'Shift+Right'),
            ('Decrease -10', 'Shift+A', 'Shift+Left'),
            ('Reset to Default', 'X', 'Delete'),
        ])
        layout.addWidget(adjust_group)

        nav_group = self._create_shortcut_group('Control Navigation', [
            ('Previous Control', 'W', 'Up'),
            ('Next Control', 'S', 'Down'),
        ])
        layout.addWidget(nav_group)

        layout.addStretch()
        return widget

    def _create_global_tab(self) -> QWidget:
        """Create the global shortcuts tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        emitter_group = self._create_shortcut_group('Emitter Selection', [
            ('Select Emitter 1', '1', '1'),
            ('Select Emitter 2', '2', '2'),
            ('Select Emitter 3', '3', '3'),
            ('Select Emitter 4', '4', '4'),
        ])
        layout.addWidget(emitter_group)

        transport_group = self._create_shortcut_group('Transport', [
            ('Play', 'Space / Enter', 'Space / Enter'),
            ('Stop', 'Escape', 'Escape'),
        ])
        layout.addWidget(transport_group)

        edit_group = self._create_shortcut_group('Edit', [
            ('Undo', 'Ctrl+Z', 'Ctrl+Z'),
            ('Redo', 'Ctrl+Shift+Z', 'Ctrl+Shift+Z'),
        ])
        layout.addWidget(edit_group)

        file_group = self._create_shortcut_group('File', [
            ('Save Preset', 'Ctrl+S', 'Ctrl+S'),
            ('Load Preset', 'Ctrl+O', 'Ctrl+O'),
        ])
        layout.addWidget(file_group)

        view_group = self._create_shortcut_group('View', [
            ('Toggle Hints', '? / F1', '? / F1'),
        ])
        layout.addWidget(view_group)

        layout.addStretch()
        return widget

    def _create_shortcut_group(self, title: str, shortcuts: list) -> QFrame:
        """Create a group of shortcuts.

        Args:
            title: Group title
            shortcuts: List of (action, left_hand_key, right_hand_key) tuples
        """
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet('''
            QFrame {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
            }
        ''')

        layout = QVBoxLayout(frame)
        layout.setSpacing(8)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet('font-weight: bold; font-size: 14px; color: #E0E0E0;')
        layout.addWidget(title_label)

        # Grid of shortcuts
        grid = QGridLayout()
        grid.setSpacing(4)

        # Headers
        grid.addWidget(QLabel('Action'), 0, 0)
        left_header = QLabel('Left Hand')
        left_header.setStyleSheet('color: #4A90D9;')
        grid.addWidget(left_header, 0, 1)
        right_header = QLabel('Right Hand')
        right_header.setStyleSheet('color: #4A90D9;')
        grid.addWidget(right_header, 0, 2)

        # Shortcut rows
        for i, (action, left_key, right_key) in enumerate(shortcuts, 1):
            action_label = QLabel(action)
            action_label.setStyleSheet('color: #C0C0C0;')
            grid.addWidget(action_label, i, 0)

            left_label = QLabel(left_key)
            left_label.setObjectName('left_key')
            grid.addWidget(left_label, i, 1)

            right_label = QLabel(right_key)
            right_label.setObjectName('right_key')
            grid.addWidget(right_label, i, 2)

        layout.addLayout(grid)

        # Store frame for updating
        if not hasattr(self, '_shortcut_frames'):
            self._shortcut_frames = []
        self._shortcut_frames.append(frame)

        return frame

    def _update_display(self):
        """Update the display based on current layout."""
        layout = self._prefs.keyboard_layout

        if layout == KeyboardLayout.LEFT_HAND:
            self._layout_label.setText('Left Hand (WASD)')
            left_style = 'font-weight: bold; color: #4A90D9;'
            right_style = 'color: #808080;'
        else:
            self._layout_label.setText('Right Hand (Arrows)')
            left_style = 'color: #808080;'
            right_style = 'font-weight: bold; color: #4A90D9;'

        # Update all key labels
        for frame in getattr(self, '_shortcut_frames', []):
            for label in frame.findChildren(QLabel):
                if label.objectName() == 'left_key':
                    label.setStyleSheet(left_style)
                elif label.objectName() == 'right_key':
                    label.setStyleSheet(right_style)

    def _toggle_layout(self):
        """Toggle keyboard layout."""
        self._prefs.toggle_layout()
