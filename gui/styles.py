"""QSS styling constants for Tempera GUI."""

# Emitter colors (for cell grid and emitter selection)
# Matches Tempera hardware: 1-Blue, 2-Yellow, 3-Pink, 4-Green
EMITTER_COLORS = {
    1: '#00BFFF',  # Blue (cyan-blue)
    2: '#FFD700',  # Yellow (golden)
    3: '#FF69B4',  # Pink (hot pink)
    4: '#00FF7F',  # Green (spring green)
}

EMITTER_COLORS_LIGHT = {
    1: '#87CEFA',  # Light blue
    2: '#FFEC8B',  # Light yellow
    3: '#FFB6C1',  # Light pink
    4: '#98FB98',  # Light green
}

# Cell grid colors
CELL_EMPTY = '#3A3A3A'
CELL_HOVER = '#5A5A5A'
CELL_BORDER = '#2A2A2A'
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
    background-color: #2B2B2B;
}

QWidget {
    background-color: #2B2B2B;
    color: #E0E0E0;
    font-family: "Helvetica Neue", Helvetica, Arial;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #404040;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
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
    border: 1px solid #404040;
    height: 6px;
    background: #3A3A3A;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #606060;
    border: 1px solid #505050;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #707070;
}

QSlider::handle:horizontal:pressed {
    background: #4A90D9;
}

QSlider::sub-page:horizontal {
    background: #4A90D9;
    border-radius: 3px;
}

QSlider::groove:vertical {
    border: 1px solid #404040;
    width: 6px;
    background: #3A3A3A;
    border-radius: 3px;
}

QSlider::handle:vertical {
    background: #606060;
    border: 1px solid #505050;
    height: 14px;
    margin: 0 -5px;
    border-radius: 7px;
}

QSlider::handle:vertical:hover {
    background: #707070;
}

QSlider::handle:vertical:pressed {
    background: #4A90D9;
}

QSlider::sub-page:vertical {
    background: #4A90D9;
    border-radius: 3px;
}

QPushButton {
    background-color: #404040;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 6px 12px;
    color: #E0E0E0;
}

QPushButton:hover {
    background-color: #4A4A4A;
    border-color: #606060;
}

QPushButton:pressed {
    background-color: #3A3A3A;
}

QPushButton:checked {
    background-color: #4A90D9;
    border-color: #5AA0E9;
}

QPushButton:disabled {
    background-color: #353535;
    color: #606060;
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
    background-color: #3A3A3A;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 4px 8px;
    color: #E0E0E0;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #404040;
    border: none;
    width: 16px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #4A4A4A;
}

QTabWidget::pane {
    border: 1px solid #404040;
    border-radius: 4px;
    background-color: #2B2B2B;
}

QTabBar::tab {
    background-color: #353535;
    border: 1px solid #404040;
    border-bottom: none;
    padding: 6px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #2B2B2B;
    border-bottom: 1px solid #2B2B2B;
}

QTabBar::tab:hover:!selected {
    background-color: #3A3A3A;
}

QStatusBar {
    background-color: #252525;
    border-top: 1px solid #404040;
    color: #A0A0A0;
}

QMenuBar {
    background-color: #2B2B2B;
    border-bottom: 1px solid #404040;
}

QMenuBar::item {
    padding: 4px 12px;
}

QMenuBar::item:selected {
    background-color: #404040;
}

QMenu {
    background-color: #2B2B2B;
    border: 1px solid #404040;
}

QMenu::item {
    padding: 6px 24px;
}

QMenu::item:selected {
    background-color: #4A90D9;
}

QMenu::separator {
    height: 1px;
    background-color: #404040;
    margin: 4px 0;
}

QScrollBar:vertical {
    background-color: #2B2B2B;
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
    background-color: #2B2B2B;
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
    """Get style for a section container (GroupBox) with focus indicator."""
    if focused:
        return f"""
            QGroupBox {{
                border: 2px solid {SECTION_ACTIVE_BORDER};
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {SECTION_ACTIVE_BORDER};
            }}
        """
    else:
        return """
            QGroupBox {
                border: 1px solid #404040;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #A0A0A0;
            }
        """


def get_slider_focus_style(focused: bool = False) -> str:
    """Get style for a slider with focus glow effect."""
    if focused:
        return f"""
            QSlider::handle:horizontal {{
                background: {FOCUS_GLOW};
                border: 2px solid {SECTION_ACTIVE_BORDER};
                width: 16px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QSlider::handle:vertical {{
                background: {FOCUS_GLOW};
                border: 2px solid {SECTION_ACTIVE_BORDER};
                height: 16px;
                margin: 0 -6px;
                border-radius: 9px;
            }}
        """
    else:
        return """
            QSlider::handle:horizontal {
                background: #606060;
                border: 1px solid #505050;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:vertical {
                background: #606060;
                border: 1px solid #505050;
                height: 14px;
                margin: 0 -5px;
                border-radius: 7px;
            }
        """


def get_combobox_focus_style(focused: bool = False) -> str:
    """Get style for a combobox with focus indicator."""
    if focused:
        return f"""
            QComboBox {{
                border: 2px solid {SECTION_ACTIVE_BORDER};
                border-radius: 4px;
                padding: 4px 8px;
                background-color: #3A3A3A;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """
    else:
        return """
            QComboBox {
                border: 1px solid #505050;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: #3A3A3A;
            }
            QComboBox::drop-down {
                border: none;
            }
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
