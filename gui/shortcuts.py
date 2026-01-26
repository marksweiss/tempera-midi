"""Keyboard shortcut management for Tempera GUI."""

from enum import Enum, auto
from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget

from gui.preferences import KeyboardLayout, get_preferences


class Section(Enum):
    """Main navigation sections."""
    GRID = auto()
    EMITTER = auto()
    TRACKS = auto()
    GLOBAL = auto()


class NavigationMode(Enum):
    """Navigation focus modes."""
    SECTION = auto()      # Navigating between sections
    SUBSECTION = auto()   # Navigating within a section (tabs, groups)
    CONTROL = auto()      # Navigating between controls
    VALUE = auto()        # Adjusting a control's value


# Key mappings for left-hand (WASD) layout
# Navigation keys (W/S) are now handled centrally by NavigationManager
LEFT_HAND_KEYS = {
    # Section navigation
    'section_next': 'Tab',
    'section_prev': 'Shift+Tab',
    'section_grid': 'Q',
    'section_emitter': 'E',
    'section_tracks': 'T',
    'section_global': 'G',
    # Navigation within section (W/S for prev/next)
    'nav_prev': 'W',
    'nav_next': 'S',
    # Actions
    'toggle_focus': 'F',  # Single toggle action for enter/exit focus
    'toggle_cell': 'Space',
    'reset_default': 'X',
    'toggle_envelope': 'R',  # Toggle envelope for focused control
}

# Key mappings for right-hand (Arrow) layout
# Navigation keys (Up/Down arrows) are now handled centrally by NavigationManager
RIGHT_HAND_KEYS = {
    # Section navigation
    'section_next': 'Page Down',
    'section_prev': 'Page Up',
    'section_grid': 'Home',
    'section_emitter': 'Insert',
    'section_tracks': None,  # Use Page Up/Down to cycle
    'section_global': 'End',
    # Navigation within section (Up/Down for prev/next)
    'nav_prev': 'Up',
    'nav_next': 'Down',
    # Actions
    'toggle_focus': 'Return',  # Single toggle action
    'toggle_cell': 'Space',  # Use Space for cell toggle, Return for focus
    'reset_default': 'Del',
    'toggle_envelope': 'R',  # Toggle envelope for focused control (same as left-hand)
}

# Shared shortcuts (work with both layouts)
SHARED_KEYS = {
    'emitter_1': '1',
    'emitter_2': '2',
    'emitter_3': '3',
    'emitter_4': '4',
    'stop': 'Escape',
    'undo': 'Ctrl+Z',
    'redo': 'Ctrl+Shift+Z',
    'save_preset': 'Ctrl+S',
    'load_preset': 'Ctrl+O',
    'toggle_hints': '?',
    'toggle_hints_alt': 'F1',
}


class ShortcutManager:
    """
    Manages keyboard shortcuts for the Tempera GUI.

    Uses QShortcut which works alongside mouse events without blocking,
    enabling concurrent keyboard + mouse input.

    Default bindings:
    - 1-4: Select emitter 1-4
    - Space/Return: Play note
    - Escape: Stop
    - E: Focus emitter panel
    - C: Focus cell grid
    - T: Focus track panel
    - G: Focus global panel
    - Ctrl+Z: Undo
    - Ctrl+Shift+Z: Redo
    - Ctrl+S: Save preset
    - Ctrl+O: Load preset
    """

    def __init__(self, parent: QWidget):
        """
        Initialize shortcut manager.

        Args:
            parent: Parent widget for shortcuts (typically MainWindow)
        """
        self._parent = parent
        self._shortcuts: dict[str, QShortcut] = {}
        self._callbacks: dict[str, Callable] = {}

    def register(self, name: str, key_sequence: str, callback: Callable):
        """
        Register a keyboard shortcut.

        Args:
            name: Unique name for the shortcut
            key_sequence: Key sequence string (e.g., "Ctrl+Z", "1", "Space")
            callback: Function to call when shortcut triggered
        """
        shortcut = QShortcut(QKeySequence(key_sequence), self._parent)
        shortcut.activated.connect(callback)
        self._shortcuts[name] = shortcut
        self._callbacks[name] = callback

    def unregister(self, name: str):
        """Unregister a shortcut by name."""
        if name in self._shortcuts:
            shortcut = self._shortcuts.pop(name)
            shortcut.setEnabled(False)
            shortcut.deleteLater()
            self._callbacks.pop(name, None)

    def set_enabled(self, name: str, enabled: bool):
        """Enable or disable a shortcut."""
        if name in self._shortcuts:
            self._shortcuts[name].setEnabled(enabled)

    def set_all_enabled(self, enabled: bool):
        """Enable or disable all shortcuts."""
        for shortcut in self._shortcuts.values():
            shortcut.setEnabled(enabled)

    def setup_defaults(
        self,
        select_emitter: Callable[[int], None],
        play: Callable[[], None],
        stop: Callable[[], None],
        undo: Callable[[], None],
        redo: Callable[[], None],
        save_preset: Callable[[], None],
        load_preset: Callable[[], None],
    ):
        """
        Set up all default shortcuts.

        Note: Section navigation (Q/E/T/G) and emitter selection (1-4) are
        handled by NavigationManager via SHARED_KEYS, not here.

        Args:
            select_emitter: Callback for emitter selection (receives emitter num 1-4)
            play: Callback for play action
            stop: Callback for stop action
            undo: Callback for undo
            redo: Callback for redo
            save_preset: Callback for save preset
            load_preset: Callback for load preset
        """
        # Note: Emitter selection (1-4 keys) is handled by NavigationManager
        # via SHARED_KEYS to avoid duplicate QShortcut registration which
        # causes Qt to treat shortcuts as ambiguous and fire neither.

        # Transport - Note: Space/Return may conflict with NavigationManager
        # so we only register Escape for stop here
        self.register('stop', 'Escape', stop)

        # Edit
        self.register('undo', 'Ctrl+Z', undo)
        self.register('redo', 'Ctrl+Shift+Z', redo)

        # File
        self.register('save_preset', 'Ctrl+S', save_preset)
        self.register('load_preset', 'Ctrl+O', load_preset)

    def get_shortcut_text(self, name: str) -> str:
        """Get the key sequence text for a shortcut."""
        if name in self._shortcuts:
            return self._shortcuts[name].key().toString()
        return ''


class NavigationManager(QObject):
    """
    Manages contextual keyboard navigation for one-handed control.

    Supports both left-hand (WASD) and right-hand (Arrow) layouts.
    Handles navigation state: section, subsection, control, and value modes.

    This is the SINGLE SOURCE OF TRUTH for navigation state. Panels are purely
    reactive - they query NavigationManager and respond to its signals but
    never manage navigation state themselves.

    Signals:
        sectionChanged(Section): Current section changed
        subsectionChanged(int): Subsection index changed
        controlChanged(int): Control index changed
        modeChanged(NavigationMode): Navigation mode changed
        navigationPathChanged(str): Full navigation path string changed
        valueAdjust(int): Value adjustment requested (-10, -1, +1, +10)
        actionTriggered(str): Action triggered (toggle_cell, reset_default, etc.)
    """

    sectionChanged = Signal(Section)
    subsectionChanged = Signal(int)
    controlChanged = Signal(int)
    modeChanged = Signal(NavigationMode)
    navigationPathChanged = Signal(str)
    valueAdjust = Signal(int)
    actionTriggered = Signal(str)

    # Section order for Tab navigation
    SECTION_ORDER = [Section.GRID, Section.EMITTER, Section.TRACKS, Section.GLOBAL]

    def __init__(self, parent: QWidget):
        """
        Initialize navigation manager.

        Args:
            parent: Parent widget (typically MainWindow)
        """
        super().__init__(parent)
        self._parent = parent
        self._prefs = get_preferences()

        # Navigation state
        self._section = Section.GRID
        self._subsection = 0
        self._control = 0
        self._mode = NavigationMode.SECTION

        # Section structure: maps section -> list of control counts per subsection
        self._section_structure: dict[Section, list[int]] = {}

        # Layout-specific shortcuts
        self._nav_shortcuts: dict[str, QShortcut] = {}
        self._shared_shortcuts: dict[str, QShortcut] = {}

        # Callbacks for actions
        self._callbacks: dict[str, Callable] = {}

        # Set up shared shortcuts
        self._setup_shared_shortcuts()

        # Set up layout-specific shortcuts
        self._apply_layout(self._prefs.keyboard_layout)

        # Listen for layout changes
        self._prefs.keyboardLayoutChanged.connect(self._on_layout_changed)

    def _setup_shared_shortcuts(self):
        """Set up shortcuts that work with both layouts."""
        for name, key in SHARED_KEYS.items():
            if key:
                shortcut = QShortcut(QKeySequence(key), self._parent)
                shortcut.activated.connect(lambda n=name: self._on_shared_shortcut(n))
                self._shared_shortcuts[name] = shortcut

    def _on_shared_shortcut(self, name: str):
        """Handle shared shortcut activation."""
        if name in self._callbacks:
            self._callbacks[name]()
        elif name == 'toggle_hints' or name == 'toggle_hints_alt':
            self._prefs.toggle_hints()

    def _apply_layout(self, layout: KeyboardLayout):
        """Apply keyboard layout shortcuts."""
        # Remove existing layout-specific shortcuts
        for shortcut in self._nav_shortcuts.values():
            shortcut.setEnabled(False)
            shortcut.deleteLater()
        self._nav_shortcuts.clear()

        # Get key mapping for layout
        keys = LEFT_HAND_KEYS if layout == KeyboardLayout.LEFT_HAND else RIGHT_HAND_KEYS

        # Create shortcuts for each action
        for name, key in keys.items():
            if key:
                shortcut = QShortcut(QKeySequence(key), self._parent)
                shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
                # Use default argument to capture value at creation time
                shortcut.activated.connect(lambda n=name: self._on_nav_shortcut(n))
                self._nav_shortcuts[name] = shortcut

    def _on_layout_changed(self, layout: KeyboardLayout):
        """Handle layout preference change."""
        self._apply_layout(layout)

    def _on_nav_shortcut(self, name: str):
        """Handle navigation shortcut activation."""
        # Section navigation
        if name == 'section_next':
            self._cycle_section(1)
        elif name == 'section_prev':
            self._cycle_section(-1)
        elif name == 'section_grid':
            self.go_to_section(Section.GRID)
        elif name == 'section_emitter':
            self.go_to_section(Section.EMITTER)
        elif name == 'section_tracks':
            self.go_to_section(Section.TRACKS)
        elif name == 'section_global':
            self.go_to_section(Section.GLOBAL)

        # W/S navigation (navigate within section)
        elif name == 'nav_prev':
            self.navigate_prev()
        elif name == 'nav_next':
            self.navigate_next()

        # Actions
        elif name == 'toggle_focus':
            self._toggle_focus()
        elif name == 'toggle_cell':
            self.actionTriggered.emit('toggle_cell')
        elif name == 'reset_default':
            self.actionTriggered.emit('reset_default')
        elif name == 'toggle_envelope':
            self.actionTriggered.emit('toggle_envelope')

    def _cycle_section(self, delta: int):
        """Cycle through sections."""
        current_idx = self.SECTION_ORDER.index(self._section)
        new_idx = (current_idx + delta) % len(self.SECTION_ORDER)
        self.go_to_section(self.SECTION_ORDER[new_idx])

    def go_to_section(self, section: Section):
        """Navigate to a specific section."""
        if section != self._section:
            self._section = section
            self._subsection = 0
            self._control = 0
            self._mode = NavigationMode.SECTION
            self.sectionChanged.emit(section)
            self.modeChanged.emit(self._mode)
            self._update_path()

    def _toggle_focus(self):
        """Toggle focus level - enter deeper or exit to shallower."""
        if self._mode == NavigationMode.SECTION:
            # Enter subsection mode
            self._mode = NavigationMode.SUBSECTION
            self.subsectionChanged.emit(self._subsection)
        elif self._mode == NavigationMode.SUBSECTION:
            # Enter control mode
            self._mode = NavigationMode.CONTROL
            self._control = 0
            self.controlChanged.emit(self._control)
        elif self._mode == NavigationMode.CONTROL:
            # Exit back to subsection mode
            self._mode = NavigationMode.SUBSECTION
        elif self._mode == NavigationMode.VALUE:
            # Exit back to control mode
            self._mode = NavigationMode.CONTROL
        self.modeChanged.emit(self._mode)
        self._update_path()

    def _update_path(self):
        """Update and emit the navigation path string."""
        section_names = {
            Section.GRID: 'Grid',
            Section.EMITTER: 'Emitter',
            Section.TRACKS: 'Tracks',
            Section.GLOBAL: 'Global',
        }
        path = section_names[self._section]

        if self._mode != NavigationMode.SECTION:
            # The actual subsection/control names come from the widgets
            # This emits a generic path that MainWindow will enhance
            if self._subsection > 0:
                path += f' > Sub {self._subsection}'
            if self._mode in (NavigationMode.CONTROL, NavigationMode.VALUE):
                path += f' > Control {self._control}'
            if self._mode == NavigationMode.VALUE:
                path += ' [Adjusting]'

        self.navigationPathChanged.emit(path)

    @property
    def section(self) -> Section:
        """Get current section."""
        return self._section

    @property
    def subsection(self) -> int:
        """Get current subsection index."""
        return self._subsection

    @subsection.setter
    def subsection(self, value: int):
        """Set subsection index (used by widgets to sync state)."""
        self._subsection = value
        self._update_path()

    @property
    def control(self) -> int:
        """Get current control index."""
        return self._control

    @control.setter
    def control(self, value: int):
        """Set control index (used by widgets to sync state)."""
        self._control = value
        self._update_path()

    @property
    def mode(self) -> NavigationMode:
        """Get current navigation mode."""
        return self._mode

    @mode.setter
    def mode(self, value: NavigationMode):
        """Set navigation mode."""
        if value != self._mode:
            self._mode = value
            self.modeChanged.emit(self._mode)
            self._update_path()

    def set_callback(self, name: str, callback: Callable):
        """Set callback for a shared shortcut action."""
        self._callbacks[name] = callback

    def get_key_for_action(self, action: str) -> str:
        """Get the current key binding for an action.

        Useful for displaying hints.
        """
        layout = self._prefs.keyboard_layout
        keys = LEFT_HAND_KEYS if layout == KeyboardLayout.LEFT_HAND else RIGHT_HAND_KEYS

        # Check layout-specific keys first
        if action in keys and keys[action]:
            return keys[action]

        # Then check shared keys
        if action in SHARED_KEYS and SHARED_KEYS[action]:
            return SHARED_KEYS[action]

        return ''

    def get_layout_keys(self) -> dict[str, str]:
        """Get all keys for current layout (for hint display)."""
        layout = self._prefs.keyboard_layout
        keys = dict(LEFT_HAND_KEYS if layout == KeyboardLayout.LEFT_HAND else RIGHT_HAND_KEYS)
        keys.update(SHARED_KEYS)
        return keys

    def focus_section(self, section: Section):
        """Set focus to a section from mouse click.

        This allows mouse clicks to focus sections, achieving the same state
        as keyboard navigation. The NavigationManager remains the single
        source of truth for focus state.

        Args:
            section: The section to focus
        """
        if section != self._section:
            self._section = section
            self._subsection = 0
            self._control = 0
            self._mode = NavigationMode.SECTION
            self.sectionChanged.emit(section)
            self.modeChanged.emit(self._mode)
        elif self._mode != NavigationMode.SECTION:
            # Same section but deeper mode - reset to SECTION
            self._subsection = 0
            self._control = 0
            self._mode = NavigationMode.SECTION
            self.modeChanged.emit(self._mode)
        self._update_path()

    def focus_subsection(self, section: Section, subsection: int):
        """Set focus to a subsection from mouse click (enters SUBSECTION mode).

        This allows mouse clicks to focus subsections, achieving the same state
        as keyboard navigation. The NavigationManager remains the single
        source of truth for focus state.

        Args:
            section: The section containing the subsection
            subsection: The subsection index within the section
        """
        section_changed = section != self._section

        self._section = section
        self._subsection = subsection
        self._control = 0
        self._mode = NavigationMode.SUBSECTION

        if section_changed:
            self.sectionChanged.emit(section)
        self.subsectionChanged.emit(subsection)
        self.modeChanged.emit(self._mode)
        self._update_path()

    def focus_control(self, section: Section, subsection: int, control: int):
        """Set focus to a specific control (from mouse click).

        This allows mouse clicks to focus controls, achieving the same state
        as keyboard navigation. The NavigationManager remains the single
        source of truth for focus state.

        Args:
            section: The section containing the control
            subsection: The subsection index within the section
            control: The control index within the subsection
        """
        section_changed = section != self._section

        self._section = section
        self._subsection = subsection
        self._control = control
        self._mode = NavigationMode.CONTROL

        if section_changed:
            self.sectionChanged.emit(section)
        self.subsectionChanged.emit(subsection)
        self.controlChanged.emit(control)
        self.modeChanged.emit(self._mode)
        self._update_path()

    # --- Section structure and navigation ---

    def register_section_structure(self, section: Section, control_counts: list[int]):
        """Register the structure of a section.

        This allows NavigationManager to know how many subsections and controls
        exist in each section, enabling it to handle W/S navigation without
        querying panels.

        Args:
            section: The section to register
            control_counts: List of control counts per subsection.
                           For example, [3, 2, 7, 4] means subsection 0 has 3 controls,
                           subsection 1 has 2, etc.
        """
        self._section_structure[section] = control_counts

    def navigate_prev(self):
        """Navigate to previous item (W key / Up arrow).

        In SUBSECTION mode: go to previous subsection
        In CONTROL mode: go to previous control (wrap within subsection)
        In SECTION mode: no-op (use Q/E/T/G for section navigation)
        """
        if self._mode == NavigationMode.SUBSECTION:
            self._navigate_subsection(-1)
        elif self._mode == NavigationMode.CONTROL:
            self._navigate_control(-1)
        # In SECTION mode, do nothing - use section shortcuts instead

    def navigate_next(self):
        """Navigate to next item (S key / Down arrow).

        In SUBSECTION mode: go to next subsection
        In CONTROL mode: go to next control (wrap within subsection)
        In SECTION mode: no-op (use Q/E/T/G for section navigation)
        """
        if self._mode == NavigationMode.SUBSECTION:
            self._navigate_subsection(1)
        elif self._mode == NavigationMode.CONTROL:
            self._navigate_control(1)
        # In SECTION mode, do nothing - use section shortcuts instead

    def _navigate_subsection(self, delta: int):
        """Navigate between subsections within the current section.

        Args:
            delta: -1 for previous, +1 for next
        """
        counts = self._section_structure.get(self._section, [])
        if not counts:
            return

        num_subsections = len(counts)
        new_subsection = self._subsection + delta

        # Clamp to valid range (no wrapping at subsection level)
        new_subsection = max(0, min(num_subsections - 1, new_subsection))

        if new_subsection != self._subsection:
            self._subsection = new_subsection
            self._control = 0  # Reset control when changing subsection
            self.subsectionChanged.emit(self._subsection)
            self._update_path()

    def _navigate_control(self, delta: int):
        """Navigate between controls within the current subsection.

        Args:
            delta: -1 for previous, +1 for next
        """
        counts = self._section_structure.get(self._section, [])
        if not counts or self._subsection >= len(counts):
            return

        control_count = counts[self._subsection]
        if control_count == 0:
            return

        # Wrap within the subsection
        new_control = (self._control + delta) % control_count

        if new_control != self._control:
            self._control = new_control
            self.controlChanged.emit(self._control)
            self._update_path()

    def get_subsection_count(self, section: Optional[Section] = None) -> int:
        """Get number of subsections in a section.

        Args:
            section: Section to query, or None for current section.

        Returns:
            Number of subsections, or 0 if section not registered.
        """
        if section is None:
            section = self._section
        counts = self._section_structure.get(section, [])
        return len(counts)

    def get_control_count(self, section: Optional[Section] = None,
                          subsection: Optional[int] = None) -> int:
        """Get number of controls in a subsection.

        Args:
            section: Section to query, or None for current section.
            subsection: Subsection index to query, or None for current subsection.

        Returns:
            Number of controls, or 0 if section/subsection not registered.
        """
        if section is None:
            section = self._section
        if subsection is None:
            subsection = self._subsection
        counts = self._section_structure.get(section, [])
        if 0 <= subsection < len(counts):
            return counts[subsection]
        return 0
