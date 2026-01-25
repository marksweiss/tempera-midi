"""GUI test harness package for Tempera MIDI Controller.

This package provides a test harness for test-first development of UI
interaction logic. It enables sending events to the UI, verifying state
consistency across all layers, and asserting visual focus matches logical state.
"""

from test.gui_tests.state import NavState, PanelState, SliderGroupState, EnvelopePanelState
from test.gui_tests.mocks import MockTemperaAdapter
from test.gui_tests.base import GUITestCase
from test.gui_tests.harness import GUITestHarness

__all__ = [
    'NavState',
    'PanelState',
    'SliderGroupState',
    'EnvelopePanelState',
    'MockTemperaAdapter',
    'GUITestCase',
    'GUITestHarness',
]
