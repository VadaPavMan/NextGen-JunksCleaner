"""Themes and styling for JunksCleaner, matching Pav Play design language."""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #181818;
    color: #f3f4f6;
}

QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Inter", "Ubuntu", sans-serif;
    font-size: 13px;
    color: #f3f4f6;
}

/* Scroll Area & Scrollbars */
QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    width: 8px;
    background: transparent;
    margin: 4px 0 4px 0;
}

QScrollBar::handle:vertical {
    background: #383838;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #e53e3e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Sidebar navigation */
QFrame#Sidebar {
    background-color: #141414;
    border-right: 1px solid #282828;
}

QLabel#AppTitle {
    font-size: 18px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.4px;
}

QLabel#SidebarSubtitle {
    font-size: 11px;
    color: #888888;
    font-weight: 500;
}

QPushButton#NavButton {
    text-align: left;
    padding: 10px 14px;
    border: 1px solid #2e2e2e;
    border-radius: 12px;
    background-color: #202020;
    color: #d4d4d8;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#NavButton:hover {
    background-color: #272727;
    color: #ffffff;
    border: 1px solid #e53e3e;
}

QPushButton#NavButton:checked {
    background-color: #1a1a1a;
    color: #e53e3e;
    font-weight: 700;
    border: 2px solid #e53e3e;
}

/* Content cards (Pav Play container style) */
QFrame#Card {
    background-color: #212121;
    border: 1px solid #303030;
    border-radius: 16px;
}

QFrame#HeroCard {
    background-color: #212121;
    border: 2px solid #e53e3e;
    border-radius: 16px;
}

QFrame#OptionCard {
    background-color: #262626;
    border: 1px solid #363636;
    border-radius: 12px;
}

QFrame#OptionCard:hover {
    border: 1px solid #4a4a4a;
    background-color: #2b2b2b;
}

QLabel#PageTitle {
    font-size: 24px;
    font-weight: 800;
    color: #e53e3e;
    letter-spacing: -0.4px;
}

QLabel#CardTitle {
    font-size: 12px;
    font-weight: 700;
    color: #e53e3e;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

QLabel#MetricValue {
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}

QLabel#MetricSubtext {
    font-size: 12px;
    color: #9ca3af;
}

/* Primary / Secondary / Danger Buttons (Pav Play style) */
QPushButton#PrimaryButton {
    background-color: #e53e3e;
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    border-radius: 12px;
    padding: 10px 22px;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background-color: #ef4444;
}

QPushButton#PrimaryButton:pressed {
    background-color: #c53030;
}

QPushButton#PrimaryButton:disabled {
    background-color: #2c2c2c;
    color: #666666;
    border: 1px solid #383838;
}

QPushButton#SecondaryButton {
    background-color: #242424;
    color: #e5e5dc;
    border: 1px solid #383838;
    border-radius: 12px;
    padding: 9px 18px;
    font-weight: 600;
}

QPushButton#SecondaryButton:hover {
    background-color: #2e2e2e;
    color: #ffffff;
    border: 1px solid #e53e3e;
}

QPushButton#DangerButton {
    background-color: #dc2626;
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    border-radius: 12px;
    padding: 10px 22px;
    border: 1px solid #ef4444;
}

QPushButton#DangerButton:hover {
    background-color: #b91c1c;
}

/* Tables and Lists */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #1a1a1a;
    border: 1px solid #2e2e2e;
    border-radius: 14px;
    gridline-color: #252525;
    selection-background-color: #2a2a2a;
    selection-color: #e53e3e;
}

QHeaderView::section {
    background-color: #222222;
    color: #e53e3e;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: none;
    padding: 10px 12px;
}

/* Progress Bars (Pav Play red slider/bar style) */
QProgressBar {
    border: 1px solid #2e2e2e;
    border-radius: 7px;
    text-align: center;
    background-color: #1a1a1a;
    color: #e5e5dc;
    font-size: 11px;
    font-weight: 700;
}

QProgressBar::chunk {
    background-color: #e53e3e;
    border-radius: 6px;
}

/* Checkboxes (Pav Play solid red checked box) */
QCheckBox {
    spacing: 10px;
    color: #f3f4f6;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #484848;
    border-radius: 4px;
    background-color: #1a1a1a;
}

QCheckBox::indicator:hover {
    border: 1px solid #e53e3e;
}

QCheckBox::indicator:checked {
    background-color: #e53e3e;
    border: 1px solid #e53e3e;
}

/* Inputs & Combos */
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #262626;
    border: 1px solid #363636;
    border-radius: 10px;
    padding: 7px 12px;
    color: #f3f4f6;
    font-weight: 600;
}

QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #e53e3e;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #212121;
    border: 1px solid #363636;
    selection-background-color: #e53e3e;
    selection-color: #ffffff;
    border-radius: 8px;
    padding: 4px;
}
"""

LIGHT_THEME_QSS = """
QMainWindow {
    background-color: #eae8df;
    color: #1c1917;
}

QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Inter", "Ubuntu", sans-serif;
    font-size: 13px;
    color: #1c1917;
}

/* Scroll Area & Scrollbars */
QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    width: 8px;
    background: transparent;
    margin: 4px 0 4px 0;
}

QScrollBar::handle:vertical {
    background: #ccc8be;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #e53e3e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Sidebar navigation */
QFrame#Sidebar {
    background-color: #dfdcd2;
    border-right: 1px solid #ccc8be;
}

QLabel#AppTitle {
    font-size: 18px;
    font-weight: 800;
    color: #1c1917;
    letter-spacing: -0.4px;
}

QLabel#SidebarSubtitle {
    font-size: 11px;
    color: #78716c;
    font-weight: 500;
}

QPushButton#NavButton {
    text-align: left;
    padding: 10px 14px;
    border: 1px solid #d5d1c4;
    border-radius: 12px;
    background-color: #f5f4ee;
    color: #44403c;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#NavButton:hover {
    background-color: #ffffff;
    color: #1c1917;
    border: 1px solid #e53e3e;
}

QPushButton#NavButton:checked {
    background-color: #eae8df;
    color: #e53e3e;
    font-weight: 700;
    border: 2px solid #e53e3e;
}

/* Content cards */
QFrame#Card {
    background-color: #f7f6f0;
    border: 1px solid #d5d1c4;
    border-radius: 16px;
}

QFrame#HeroCard {
    background-color: #f7f6f0;
    border: 2px solid #e53e3e;
    border-radius: 16px;
}

QFrame#OptionCard {
    background-color: #edebe2;
    border: 1px solid #dcd8cc;
    border-radius: 12px;
}

QFrame#OptionCard:hover {
    border: 1px solid #b5b0a2;
    background-color: #ffffff;
}

QLabel#PageTitle {
    font-size: 24px;
    font-weight: 800;
    color: #e53e3e;
    letter-spacing: -0.4px;
}

QLabel#CardTitle {
    font-size: 12px;
    font-weight: 700;
    color: #e53e3e;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

QLabel#MetricValue {
    font-size: 30px;
    font-weight: 800;
    color: #1c1917;
    letter-spacing: -0.5px;
}

QLabel#MetricSubtext {
    font-size: 12px;
    color: #78716c;
}

/* Primary / Secondary / Danger Buttons */
QPushButton#PrimaryButton {
    background-color: #e53e3e;
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    border-radius: 12px;
    padding: 10px 22px;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background-color: #ef4444;
}

QPushButton#PrimaryButton:pressed {
    background-color: #c53030;
}

QPushButton#PrimaryButton:disabled {
    background-color: #dcd8cc;
    color: #a8a29e;
    border: 1px solid #ccc8be;
}

QPushButton#SecondaryButton {
    background-color: #ffffff;
    color: #1c1917;
    border: 1px solid #d5d1c4;
    border-radius: 12px;
    padding: 9px 18px;
    font-weight: 600;
}

QPushButton#SecondaryButton:hover {
    background-color: #f5f4ee;
    border: 1px solid #e53e3e;
}

QPushButton#DangerButton {
    background-color: #dc2626;
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    border-radius: 12px;
    padding: 10px 22px;
    border: 1px solid #b91c1c;
}

QPushButton#DangerButton:hover {
    background-color: #b91c1c;
}

/* Tables and Lists */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #ffffff;
    border: 1px solid #d5d1c4;
    border-radius: 14px;
    gridline-color: #f0eee7;
    selection-background-color: #edebe2;
    selection-color: #e53e3e;
}

QHeaderView::section {
    background-color: #edebe2;
    color: #e53e3e;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: none;
    padding: 10px 12px;
}

/* Progress Bars */
QProgressBar {
    border: 1px solid #d5d1c4;
    border-radius: 7px;
    text-align: center;
    background-color: #edebe2;
    color: #1c1917;
    font-size: 11px;
    font-weight: 700;
}

QProgressBar::chunk {
    background-color: #e53e3e;
    border-radius: 6px;
}

/* Checkboxes */
QCheckBox {
    spacing: 10px;
    color: #1c1917;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #b5b0a2;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border: 1px solid #e53e3e;
}

QCheckBox::indicator:checked {
    background-color: #e53e3e;
    border: 1px solid #e53e3e;
}

/* Inputs & Combos */
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #d5d1c4;
    border-radius: 10px;
    padding: 7px 12px;
    color: #1c1917;
    font-weight: 600;
}

QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #e53e3e;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d5d1c4;
    selection-background-color: #e53e3e;
    selection-color: #ffffff;
    border-radius: 8px;
    padding: 4px;
}
"""


def get_stylesheet(theme_name: str) -> str:
    """Return the Qt stylesheet matching the requested theme name."""
    if theme_name.lower() == "light":
        return LIGHT_THEME_QSS
    return DARK_THEME_QSS
