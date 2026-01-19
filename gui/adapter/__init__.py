"""Adapter layer for GUI-to-library communication."""

from gui.adapter.tempera_adapter import TemperaAdapter
from gui.adapter.state_manager import StateManager
from gui.adapter.debouncer import Debouncer

__all__ = ['TemperaAdapter', 'StateManager', 'Debouncer']
