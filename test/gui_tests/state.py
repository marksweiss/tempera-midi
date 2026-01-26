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
    """Snapshot of a panel's visual state.

    Note: Panels are now purely reactive to NavigationManager signals.
    They don't track navigation state themselves, only visual highlighting.
    """
    panel_focused: bool
    visual_subsection: int  # Which subsection is visually highlighted (-1 = none)
    visual_control: int  # Which control is visually highlighted (-1 = none)
    stylesheet: str

    # Compatibility properties for tests that use old names
    @property
    def focused_subsection(self) -> int:
        """Alias for visual_subsection for backwards compatibility."""
        return self.visual_subsection

    @property
    def in_control_mode(self) -> bool:
        """Returns True if a control is visually highlighted."""
        return self.visual_control >= 0


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
