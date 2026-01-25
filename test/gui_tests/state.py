"""State dataclasses for GUI test harness.

These dataclasses represent snapshots of state at various layers of the UI hierarchy.
"""

from dataclasses import dataclass
from typing import Optional

from gui.shortcuts import Section, NavigationMode


@dataclass
class NavState:
    """Snapshot of NavigationManager state."""
    section: Section
    subsection: int
    control: int
    mode: NavigationMode


@dataclass
class PanelState:
    """Snapshot of a panel's focus state."""
    panel_focused: bool
    focused_subsection: int
    in_control_mode: bool
    stylesheet: str


@dataclass
class SliderGroupState:
    """Snapshot of a SliderGroup's focus state."""
    group_focused: bool
    focused_index: int
    slider_count: int
    stylesheet: str


@dataclass
class EnvelopePanelState:
    """Snapshot of EnvelopePanel state."""
    control_key: Optional[str]      # e.g., "emitter.1.volume"
    display_name: Optional[str]     # e.g., "Emitter 1 - Volume"
    enabled: bool
    has_envelope: bool
