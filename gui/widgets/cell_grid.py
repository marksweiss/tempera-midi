"""8x8 clickable cell grid for emitter placement."""

from typing import Optional

from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent
from PySide6.QtWidgets import QWidget, QSizePolicy

from gui.styles import EMITTER_COLORS, CELL_EMPTY, CELL_HOVER, CELL_BORDER


class CellGrid(QWidget):
    """
    8x8 clickable grid representing Tempera's cell layout.

    Columns are tracks (1-8), rows are cells within each track (1-8).
    Each cell can be empty or assigned to one of 4 emitters, shown by color.

    Signals:
        cellClicked(int, int): Emitted when a cell is clicked (column, cell)
        cellRightClicked(int, int): Emitted on right-click (column, cell)
    """

    cellClicked = Signal(int, int)
    cellRightClicked = Signal(int, int)

    CELL_SIZE = 36
    CELL_SPACING = 2
    PADDING = 4

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        # Cell states: (column, cell) -> emitter_num or None
        self._cells: dict[tuple[int, int], int] = {}

        # Currently hovered cell
        self._hover_cell: Optional[tuple[int, int]] = None

        # Active emitter for visual feedback
        self._active_emitter = 1

        self._setup_ui()

    def _setup_ui(self):
        """Set up the widget."""
        # Calculate size
        total_size = (self.CELL_SIZE * 8) + (self.CELL_SPACING * 7) + (self.PADDING * 2)
        self.setFixedSize(total_size, total_size)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setMouseTracking(True)

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

        border_pen = QPen(QColor(CELL_BORDER))
        border_pen.setWidth(1)

        for col in range(1, 9):
            for cell in range(1, 9):
                rect = self._cell_rect(col, cell)
                key = (col, cell)

                # Determine cell color
                emitter = self._cells.get(key)
                if emitter is not None:
                    color = QColor(EMITTER_COLORS[emitter])
                elif self._hover_cell == key:
                    color = QColor(CELL_HOVER)
                else:
                    color = QColor(CELL_EMPTY)

                # Draw cell
                painter.setPen(border_pen)
                painter.setBrush(QBrush(color))
                painter.drawRoundedRect(rect, 4, 4)

                # Draw emitter number if assigned
                if emitter is not None:
                    painter.setPen(QPen(Qt.GlobalColor.white))
                    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(emitter))

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
