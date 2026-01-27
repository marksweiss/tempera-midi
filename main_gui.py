#!/usr/bin/env python3
"""Entry point for Tempera MIDI GUI application.

Usage:
    uv run python main_gui.py

Or with a specific MIDI port:
    TEMPERA_PORT='Tempera' uv run python main_gui.py
"""

import os

from gui.app import run_app

if __name__ == '__main__':
    run_app()
