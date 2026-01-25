"""Base test case class for GUI tests."""

import os
import sys
import unittest
from typing import Optional

# Set offscreen rendering before importing Qt
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')


class GUITestCase(unittest.TestCase):
    """Base class for GUI tests with Qt application setup.

    This class handles:
    - Creating a single QApplication instance for all tests
    - Setting up headless rendering via offscreen platform
    - Providing access to the test harness

    Usage:
        class TestMyFeature(GUITestCase):
            def test_something(self):
                self.harness.press_key(Qt.Key_Q)
                self.harness.assert_state_consistent()
    """

    _app: Optional['QApplication'] = None

    @classmethod
    def setUpClass(cls):
        """Create QApplication once for all tests in the class."""
        # Import here to ensure env var is set first
        from PySide6.QtWidgets import QApplication

        # Create QApplication if it doesn't exist
        if QApplication.instance() is None:
            # Pass empty args for headless testing
            cls._app = QApplication([])
        else:
            cls._app = QApplication.instance()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests complete."""
        # Note: We don't quit the app here as other test classes may use it
        pass

    def setUp(self):
        """Set up the test harness before each test."""
        from test.gui_tests.harness import GUITestHarness

        self.harness = GUITestHarness()
        self.harness.setup()

    def tearDown(self):
        """Tear down the test harness after each test."""
        if hasattr(self, 'harness'):
            self.harness.teardown()
