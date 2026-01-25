"""Keyboard shortcuts help dialog."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton
)


class ShortcutsDialog(QDialog):
    """
    Simple dialog showing keyboard shortcut help.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Keyboard Shortcuts Help')
        self.setFixedSize(400, 420)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel('Keyboard Shortcuts')
        title.setStyleSheet('font-weight: bold; font-size: 16px; color: #E0E0E0;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Help text
        help_text = QLabel(
            '<p><b>F1</b> - Toggle keyboard hints</p>'
            '<p><b>Q</b> - Grid &nbsp;&nbsp; '
            '<b>E</b> - Emitters &nbsp;&nbsp; '
            '<b>T</b> - Tracks &nbsp;&nbsp; '
            '<b>G</b> - Global</p>'
            '<p><b>F</b> - Select a section, then a control in a section, then go back</p>'
            '<p><b>W/S</b> - Move between controls</p>'
            '<p><b>A/D</b> - Adjust control value</p>'
            '<p><b>R</b> - Toggle envelope for focused control</p>'
            '<p><b>1-4</b> - Select emitter 1-4</p>'
            '<p><b>Space</b> - Toggle cell / Play</p>'
            '<p><b>Escape</b> - Stop</p>'
        )
        help_text.setStyleSheet('''
            QLabel {
                color: #C0C0C0;
                font-size: 13px;
                line-height: 1.6;
            }
        ''')
        help_text.setWordWrap(True)
        help_text.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(help_text)

        layout.addStretch()

        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(80)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
