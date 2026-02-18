"""QSS styling constants for Tempera GUI."""

# Emitter colors (for cell grid and emitter selection)
# Matches Tempera hardware: 1-Blue, 2-Yellow, 3-Pink, 4-Green
EMITTER_COLORS = {
    1: '#00BFFF',  # Blue (cyan-blue)
    2: '#FFD700',  # Yellow (golden)
    3: '#FF69B4',  # Pink (hot pink)
    4: '#00FF7F',  # Green (spring green)
}

# Darker variants for slider tracks
EMITTER_COLORS_DARK = {
    1: '#004466',  # Dark blue
    2: '#665500',  # Dark yellow
    3: '#662244',  # Dark pink
    4: '#004422',  # Dark green
}

# Font families
FONT_PRIMARY = '"Helvetica Neue", Helvetica, Arial'
FONT_MONO = '"SF Mono", Menlo, Consolas, "Liberation Mono", monospace'

EMITTER_COLORS_LIGHT = {
    1: '#87CEFA',  # Light blue
    2: '#FFEC8B',  # Light yellow
    3: '#FFB6C1',  # Light pink
    4: '#98FB98',  # Light green
}

# Cell grid colors
CELL_EMPTY = '#2A2A2A'
CELL_HOVER = '#404040'
CELL_BORDER = '#1A1A1A'
CELL_CURSOR = '#4A90D9'  # Blue cursor outline

# Focus colors
FOCUS_BORDER = '#4A90D9'  # Blue focus ring
FOCUS_GLOW = '#4A90D9'    # Blue glow for focused controls
SECTION_ACTIVE_BORDER = '#5AA0E9'  # Lighter blue for active section

# Hint badge colors
HINT_BADGE_BG = 'rgba(60, 60, 60, 0.9)'
HINT_BADGE_TEXT = '#FFFFFF'
HINT_BADGE_BORDER = '#606060'

# Envelope colors
ENVELOPE_ACTIVE_CYAN = '#00CED1'  # Dark turquoise - active envelope
ENVELOPE_INACTIVE_GREY = '#606060'  # Grey - inactive envelope
ENVELOPE_BACKGROUND = '#1E1E1E'  # Dark background for canvas
ENVELOPE_TOGGLE_ON = '#4A90D9'  # Blue for enabled toggle (matches sequencer buttons)
ENVELOPE_TOGGLE_OFF = '#404040'  # Standard button grey
ENVELOPE_PLAYHEAD = '#FFFFFF'  # White playhead line

# Main application stylesheet
MAIN_STYLESHEET = """
QMainWindow {
    background-color: #1E1E1E;
}

QWidget {
    background-color: #1E1E1E;
    color: #E0E0E0;
    font-family: "Helvetica Neue", Helvetica, Arial;
    font-size: 13px;
}

QGroupBox {
    background-color: #1A1A1A;
    border: 2px solid #333333;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 4px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #A0A0A0;
}

QLabel {
    color: #C0C0C0;
    background: transparent;
}

QSlider::groove:horizontal {
    border: 1px solid #333333;
    height: 4px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #252525, stop:1 #3A3A3A);
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #707070, stop:1 #505050);
    border: 1px solid #404040;
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #808080, stop:1 #606060);
    border: 1px solid #404040;
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5AA0E9, stop:1 #4A90D9);
    border: 1px solid #404040;
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 7px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2A5080, stop:1 #4A90D9);
    border-radius: 2px;
}

QSlider::groove:vertical {
    border: 1px solid #333333;
    width: 4px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3A3A3A, stop:1 #252525);
    border-radius: 2px;
}

QSlider::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #707070, stop:1 #505050);
    border: 1px solid #404040;
    width: 14px;
    height: 14px;
    margin: 0 -6px;
    border-radius: 7px;
}

QSlider::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #808080, stop:1 #606060);
    border: 1px solid #404040;
    width: 14px;
    height: 14px;
    margin: 0 -6px;
    border-radius: 7px;
}

QSlider::handle:vertical:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5AA0E9, stop:1 #4A90D9);
    border: 1px solid #404040;
    width: 14px;
    height: 14px;
    margin: 0 -6px;
    border-radius: 7px;
}

QSlider::sub-page:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A90D9, stop:1 #2A5080);
    border-radius: 2px;
}

QPushButton {
    background-color: #353535;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 6px 12px;
    color: #E0E0E0;
}

QPushButton:hover {
    background-color: #404040;
    border-color: #505050;
}

QPushButton:pressed {
    background-color: #2A2A2A;
}

QPushButton:checked {
    background-color: #4A90D9;
    border-color: #5AA0E9;
}

QPushButton:disabled {
    background-color: #2A2A2A;
    color: #505050;
}

QRadioButton {
    spacing: 8px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #505050;
    border-radius: 10px;
    background: #3A3A3A;
}

QRadioButton::indicator:hover {
    border-color: #606060;
}

QRadioButton::indicator:checked {
    background-color: #4A90D9;
    border-color: #4A90D9;
}

QSpinBox {
    background-color: #2A2A2A;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 4px 8px;
    color: #E0E0E0;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #353535;
    border: none;
    width: 16px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #404040;
}

QTabWidget::pane {
    border: 1px solid #333333;
    border-top: none;
    background-color: #1E1E1E;
    padding: 2px;
}

QTabBar::tab {
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 6px 16px;
    margin-right: 2px;
    color: #808080;
}

QTabBar::tab:selected {
    color: #E0E0E0;
    border-bottom: 2px solid #4A90D9;
}

QTabBar::tab:hover:!selected {
    color: #A0A0A0;
    background-color: transparent;
}

QStatusBar {
    background-color: #1A1A1A;
    border-top: 1px solid #333333;
    color: #A0A0A0;
}

QMenuBar {
    background-color: #1E1E1E;
    border-bottom: 1px solid #333333;
}

QMenuBar::item {
    padding: 4px 12px;
}

QMenuBar::item:selected {
    background-color: #353535;
}

QMenu {
    background-color: #1E1E1E;
    border: 1px solid #333333;
}

QMenu::item {
    padding: 6px 24px;
}

QMenu::item:selected {
    background-color: #4A90D9;
}

QMenu::separator {
    height: 1px;
    background-color: #333333;
    margin: 4px 0;
}

QScrollBar:vertical {
    background-color: #1E1E1E;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #505050;
    min-height: 20px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #606060;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #1E1E1E;
    height: 12px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #505050;
    min-width: 20px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #606060;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
"""


def get_emitter_button_style(emitter_num: int, selected: bool = False) -> str:
    """Get style for an emitter selection button."""
    color = EMITTER_COLORS[emitter_num]
    light_color = EMITTER_COLORS_LIGHT[emitter_num]

    if selected:
        return f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid {light_color};
                border-radius: 4px;
                padding: 6px 12px;
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {light_color};
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: #404040;
                border: 2px solid {color};
                border-radius: 4px;
                padding: 6px 12px;
                color: {color};
            }}
            QPushButton:hover {{
                background-color: #4A4A4A;
                border-color: {light_color};
            }}
        """


def get_section_focus_style(focused: bool = False) -> str:
    """Get style for a top-level section container (Emitter, Global, Tracks)."""
    border_color = SECTION_ACTIVE_BORDER if focused else '#404040'
    title_color = SECTION_ACTIVE_BORDER if focused else '#B0B0B0'
    return f"""
        QGroupBox {{
            border: 2px solid {border_color};
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 4px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {title_color};
            font-size: 14px;
        }}
    """


def get_subsection_focus_style(focused: bool = False) -> str:
    """Get style for a subsection container (ADSR, Effects, Modulator, etc.)."""
    border_color = SECTION_ACTIVE_BORDER if focused else '#404040'
    title_color = SECTION_ACTIVE_BORDER if focused else '#808080'
    return f"""
        QGroupBox {{
            border: 2px solid {border_color};
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 4px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {title_color};
            font-size: 11px;
        }}
    """


def get_slider_focus_style(focused: bool = False) -> str:
    """Get style for a slider with focus glow effect."""
    if focused:
        bg_color = FOCUS_GLOW
        border_color = SECTION_ACTIVE_BORDER
    else:
        bg_color = '#606060'
        border_color = '#505050'

    return f"""
        QSlider::handle:horizontal {{
            background: {bg_color};
            border: 2px solid {border_color};
            width: 14px;
            height: 14px;
            margin: -6px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {bg_color};
            border: 2px solid {border_color};
            width: 14px;
            height: 14px;
            margin: -6px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:pressed {{
            background: {bg_color};
            border: 2px solid {border_color};
            width: 14px;
            height: 14px;
            margin: -6px 0;
            border-radius: 7px;
        }}
        QSlider::handle:vertical {{
            background: {bg_color};
            border: 2px solid {border_color};
            width: 14px;
            height: 14px;
            margin: 0 -6px;
            border-radius: 7px;
        }}
        QSlider::handle:vertical:hover {{
            background: {bg_color};
            border: 2px solid {border_color};
            width: 14px;
            height: 14px;
            margin: 0 -6px;
            border-radius: 7px;
        }}
        QSlider::handle:vertical:pressed {{
            background: {bg_color};
            border: 2px solid {border_color};
            width: 14px;
            height: 14px;
            margin: 0 -6px;
            border-radius: 7px;
        }}
    """


def get_combobox_focus_style(focused: bool = False) -> str:
    """Get style for a combobox with focus indicator."""
    border_color = SECTION_ACTIVE_BORDER if focused else '#505050'
    return f"""
        QComboBox {{
            border: 2px solid {border_color};
            border-radius: 4px;
            padding: 4px 8px;
            background-color: #3A3A3A;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
    """


# Hint badge stylesheet
HINT_BADGE_STYLE = f"""
    QLabel {{
        background-color: {HINT_BADGE_BG};
        color: {HINT_BADGE_TEXT};
        border: 1px solid {HINT_BADGE_BORDER};
        border-radius: 3px;
        padding: 1px 4px;
        font-size: 10px;
        font-weight: bold;
    }}
"""


def get_emitter_slider_style(emitter_num: int) -> str:
    """Get slider style colored for a specific emitter.

    Args:
        emitter_num: Emitter number (1-4)

    Returns:
        QSS stylesheet string for horizontal sliders with emitter color gradient
    """
    color = EMITTER_COLORS[emitter_num]
    dark_color = EMITTER_COLORS_DARK[emitter_num]

    return f"""
        QSlider::groove:horizontal {{
            border: 1px solid #333333;
            height: 4px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #252525, stop:1 #3A3A3A);
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #707070, stop:1 #505050);
            border: 1px solid #404040;
            width: 14px;
            height: 14px;
            margin: -6px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #808080, stop:1 #606060);
            border: 1px solid #404040;
            width: 14px;
            height: 14px;
            margin: -6px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color}, stop:1 {dark_color});
            border: 1px solid #404040;
            width: 14px;
            height: 14px;
            margin: -6px 0;
            border-radius: 7px;
        }}
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {dark_color}, stop:1 {color});
            border-radius: 2px;
        }}
    """


def get_transport_button_style(button_type: str) -> str:
    """Get style for transport buttons (play/stop).

    Args:
        button_type: 'play' or 'stop'

    Returns:
        QSS stylesheet string for the button
    """
    if button_type == 'play':
        return """
            QPushButton {
                background-color: #2A4A2A;
                border: 1px solid #3A6A3A;
                border-radius: 4px;
                color: #7ACA7A;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3A5A3A;
                border-color: #4A8A4A;
            }
            QPushButton:pressed {
                background-color: #4A8A4A;
            }
        """
    else:  # stop
        return """
            QPushButton {
                background-color: #4A2A2A;
                border: 1px solid #6A3A3A;
                border-radius: 4px;
                color: #CA7A7A;
                font-size: 16px;
                padding-top: 3px;
            }
            QPushButton:hover {
                background-color: #5A3A3A;
                border-color: #8A4A4A;
            }
            QPushButton:pressed {
                background-color: #8A4A4A;
            }
        """
