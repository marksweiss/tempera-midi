"""8x8 clickable cell grid for emitter placement."""

from typing import Optional

from PySide6.QtCore import Qt, Signal, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent, QKeyEvent
from PySide6.QtWidgets import QWidget, QSizePolicy

from gui.styles import EMITTER_COLORS, CELL_EMPTY, CELL_HOVER, CELL_BORDER, CELL_CURSOR


class CellGrid(QWidget):
    """
    8x8 clickable grid representing Tempera's cell layout.

    Columns are tracks (1-8), rows are cells within each track (1-8).
    Each cell can be empty or assigned to one of 4 emitters, shown by color.

    Supports keyboard cursor navigation for one-handed control.

    Signals:
        cellClicked(int, int): Emitted when a cell is clicked (column, cell)
        cellRightClicked(int, int): Emitted on right-click (column, cell)
        cursorMoved(int, int): Emitted when keyboard cursor moves (column, cell)
    """

    cellClicked = Signal(int, int)
    cellRightClicked = Signal(int, int)
    cursorMoved = Signal(int, int)

    CELL_SIZE = 36
    CELL_SPACING = 2
    PADDING = 8

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        # Cell states: (column, cell) -> emitter_num or None
        self._cells: dict[tuple[int, int], int] = {}

        # Currently hovered cell
        self._hover_cell: Optional[tuple[int, int]] = None

        # Active emitter for visual feedback
        self._active_emitter = 1

        # Keyboard cursor position (1-indexed)
        self._cursor_col = 1
        self._cursor_row = 1
        self._cursor_visible = False

        # Cursor animation (pulsing effect)
        self._cursor_pulse = 0
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self._update_cursor_pulse)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget."""
        # Calculate size
        total_size = (self.CELL_SIZE * 8) + (self.CELL_SPACING * 7) + (self.PADDING * 2)
        self.setFixedSize(total_size, total_size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _update_cursor_pulse(self):
        """Update cursor pulse animation."""
        self._cursor_pulse = (self._cursor_pulse + 1) % 20
        self.update()

    def _cell_rect(self, column: int, cell: int) -> QRect:
        """Get the rectangle for a cell (1-indexed)."""
        x = self.PADDING + (column - 1) * (self.CELL_SIZE + self.CELL_SPACING)
        y = self.PADDING + (cell - 1) * (self.CELL_SIZE + self.CELL_SPACING)
        return QRect(x, y, self.CELL_SIZE, self.CELL_SIZE)

    def _cell_at_pos(self, x: int, y: int) -> Optional[tuple[int, int]]:
        """Get the cell at a pixel position, or None if outside grid."""
        for col in range(1, 9):
            for cell in range(1, 9):
                if self._cell_rect(col, cell).contains(x, y):
                    return (col, cell)
        return None

    def paintEvent(self, event):
        """Draw the cell grid."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for col in range(1, 9):
            for cell in range(1, 9):
                rect = self._cell_rect(col, cell)
                key = (col, cell)

                emitter = self._cells.get(key)

                if emitter is not None:
                    # Cell has emitter: draw colored border only, no fill
                    border_pen = QPen(QColor(EMITTER_COLORS[emitter]))
                    border_pen.setWidth(3)
                    painter.setPen(border_pen)
                    painter.setBrush(QBrush(QColor(CELL_EMPTY)))
                else:
                    # Empty cell: subtle border, dark fill
                    if self._hover_cell == key:
                        fill_color = QColor(CELL_HOVER)
                    else:
                        fill_color = QColor(CELL_EMPTY)
                    border_pen = QPen(QColor(CELL_BORDER))
                    border_pen.setWidth(1)
                    painter.setPen(border_pen)
                    painter.setBrush(QBrush(fill_color))

                painter.drawRoundedRect(rect, 4, 4)

        # Draw cursor if visible
        if self._cursor_visible:
            cursor_rect = self._cell_rect(self._cursor_col, self._cursor_row)

            # Pulsing effect: vary opacity based on pulse value
            # pulse goes 0-19, map to opacity 0.4-1.0
            pulse_factor = abs(10 - self._cursor_pulse) / 10.0  # 0.0 to 1.0
            opacity = 0.4 + (0.6 * pulse_factor)

            cursor_color = QColor(CELL_CURSOR)
            cursor_color.setAlphaF(opacity)

            cursor_pen = QPen(cursor_color)
            cursor_pen.setWidth(3)
            painter.setPen(cursor_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            # Draw cursor slightly outside the cell
            cursor_rect = cursor_rect.adjusted(-2, -2, 2, 2)
            painter.drawRoundedRect(cursor_rect, 6, 6)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse movement for hover effect."""
        pos = event.position().toPoint()
        new_hover = self._cell_at_pos(pos.x(), pos.y())

        if new_hover != self._hover_cell:
            self._hover_cell = new_hover
            self.update()

    def leaveEvent(self, event):
        """Handle mouse leaving widget."""
        self._hover_cell = None
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse click on cell."""
        pos = event.position().toPoint()
        cell = self._cell_at_pos(pos.x(), pos.y())

        if cell is not None:
            col, row = cell
            if event.button() == Qt.MouseButton.LeftButton:
                self.cellClicked.emit(col, row)
            elif event.button() == Qt.MouseButton.RightButton:
                self.cellRightClicked.emit(col, row)

    def set_cell(self, column: int, cell: int, emitter: Optional[int]):
        """Set or clear a cell's emitter assignment.

        Args:
            column: Track number (1-8)
            cell: Cell number within track (1-8)
            emitter: Emitter number (1-4) or None to clear
        """
        key = (column, cell)
        if emitter is None:
            self._cells.pop(key, None)
        else:
            self._cells[key] = emitter
        self.update()

    def get_cell(self, column: int, cell: int) -> Optional[int]:
        """Get the emitter assigned to a cell, or None if empty."""
        return self._cells.get((column, cell))

    def clear_cell(self, column: int, cell: int):
        """Clear a cell's emitter assignment."""
        self.set_cell(column, cell, None)

    def clear_all(self):
        """Clear all cell assignments."""
        self._cells.clear()
        self.update()

    def set_all_cells(self, cells: dict[tuple[int, int], int]):
        """Set all cell assignments at once."""
        self._cells = dict(cells)
        self.update()

    def get_all_cells(self) -> dict[tuple[int, int], int]:
        """Get all cell assignments."""
        return dict(self._cells)

    def set_active_emitter(self, emitter_num: int):
        """Set the active emitter for visual feedback."""
        self._active_emitter = emitter_num
        self.update()

    @property
    def active_emitter(self) -> int:
        """Get the active emitter number."""
        return self._active_emitter

    # --- Keyboard cursor navigation ---

    def focusInEvent(self, event):
        """Handle focus gained - show cursor and start animation."""
        super().focusInEvent(event)
        self._cursor_visible = True
        self._cursor_timer.start(50)  # 50ms for smooth pulsing
        self.update()

    def focusOutEvent(self, event):
        """Handle focus lost - hide cursor and stop animation."""
        super().focusOutEvent(event)
        self._cursor_visible = False
        self._cursor_timer.stop()
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input for cursor navigation."""
        key = event.key()

        # Arrow keys and WASD for cursor movement
        if key in (Qt.Key.Key_Up, Qt.Key.Key_W):
            self.move_cursor(0, -1)
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            self.move_cursor(0, 1)
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self.move_cursor(-1, 0)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self.move_cursor(1, 0)
        # Space or Enter to toggle cell at cursor
        elif key in (Qt.Key.Key_Space, Qt.Key.Key_Return):
            self.toggle_cell_at_cursor()
        # X or Delete to clear cell at cursor
        elif key in (Qt.Key.Key_X, Qt.Key.Key_Delete):
            self.clear_cell_at_cursor()
        else:
            super().keyPressEvent(event)

    def move_cursor(self, dcol: int, drow: int):
        """Move cursor by delta, wrapping at edges.

        Args:
            dcol: Column delta (-1, 0, or 1)
            drow: Row delta (-1, 0, or 1)
        """
        new_col = self._cursor_col + dcol
        new_row = self._cursor_row + drow

        # Wrap around
        if new_col < 1:
            new_col = 8
        elif new_col > 8:
            new_col = 1
        if new_row < 1:
            new_row = 8
        elif new_row > 8:
            new_row = 1

        if new_col != self._cursor_col or new_row != self._cursor_row:
            self._cursor_col = new_col
            self._cursor_row = new_row
            self.cursorMoved.emit(self._cursor_col, self._cursor_row)
            self.update()

    def move_cursor_up(self):
        """Move cursor up (for external navigation manager)."""
        self.move_cursor(0, -1)

    def move_cursor_down(self):
        """Move cursor down (for external navigation manager)."""
        self.move_cursor(0, 1)

    def move_cursor_left(self):
        """Move cursor left (for external navigation manager)."""
        self.move_cursor(-1, 0)

    def move_cursor_right(self):
        """Move cursor right (for external navigation manager)."""
        self.move_cursor(1, 0)

    def toggle_cell_at_cursor(self):
        """Toggle the cell at current cursor position."""
        self.cellClicked.emit(self._cursor_col, self._cursor_row)

    def clear_cell_at_cursor(self):
        """Clear (right-click equivalent) the cell at cursor position."""
        self.cellRightClicked.emit(self._cursor_col, self._cursor_row)

    def set_cursor_position(self, column: int, cell: int):
        """Set cursor position directly.

        Args:
            column: Column (1-8)
            cell: Cell/row (1-8)
        """
        column = max(1, min(8, column))
        cell = max(1, min(8, cell))
        if column != self._cursor_col or cell != self._cursor_row:
            self._cursor_col = column
            self._cursor_row = cell
            self.cursorMoved.emit(self._cursor_col, self._cursor_row)
            self.update()

    @property
    def cursor_position(self) -> tuple[int, int]:
        """Get current cursor position (column, row)."""
        return (self._cursor_col, self._cursor_row)

    @property
    def cursor_visible(self) -> bool:
        """Check if cursor is currently visible."""
        return self._cursor_visible

    def show_cursor(self):
        """Show cursor (for external control)."""
        if not self._cursor_visible:
            self._cursor_visible = True
            self._cursor_timer.start(50)
            self.update()

    def hide_cursor(self):
        """Hide cursor (for external control)."""
        if self._cursor_visible:
            self._cursor_visible = False
            self._cursor_timer.stop()
            self.update()
