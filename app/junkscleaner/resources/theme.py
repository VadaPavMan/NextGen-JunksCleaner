"""Themes and styling for JunksCleaner.

Design language adapted from Pav Play: warm-toned neutrals, crimson accent
used sparingly, left-edge active indicators, grouped content sections with
clean typographic hierarchy. No gratuitous rounded corners or floating cards.
"""

# -- Shared design tokens (referenced in both themes) -------------------------
# Accent:   #c0392b (dark crimson — assertive without screaming)
# Success:  #27ae60
# Warning:  #e67e22
# Info:     #2980b9
# Muted:    per-theme neutral

DARK_THEME_QSS = """
/* ========================================================================
   DARK THEME — JunksCleaner
   Base:    #1a1a1a  (deep charcoal, warm undertone)
   Surface: #242220  (cards / raised areas)
   Border:  #333130  (subtle separation)
   Text:    #e8e6e3  (high contrast warm white)
   Muted:   #8a8784  (secondary text)
   Accent:  #c0392b  (crimson — titles, active states only)
   ======================================================================== */

QMainWindow, QWidget#CentralWidget, QStackedWidget {
    background-color: #1a1a1a;
    color: #e8e6e3;
}

QWidget {
    font-family: "Segoe UI", "SF Pro Display", -apple-system, sans-serif;
    font-size: 13px;
    color: #e8e6e3;
}

/* --- Scrollbars --- */
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background: transparent;
    background-color: #1a1a1a;
    border: none;
}

QScrollBar:vertical {
    width: 6px;
    background: transparent;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #3d3b39;
    min-height: 30px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #5a5856;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    height: 0px;
    background: transparent;
}

/* --- Sidebar --- */
QFrame#Sidebar {
    background-color: #161514;
    border-right: 1px solid #2a2827;
}

QFrame#SidebarSeparator {
    background-color: #2a2827;
    border: none;
}

QLabel#AppTitle {
    font-size: 15px;
    font-weight: 700;
    color: #e8e6e3;
}

QLabel#SidebarSubtitle {
    font-size: 10px;
    color: #6b6966;
    font-weight: 400;
}

QPushButton#NavButton {
    text-align: left;
    padding: 9px 16px;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    background-color: transparent;
    color: #9e9b98;
    font-weight: 500;
    font-size: 13px;
}

QPushButton#NavButton:hover {
    background-color: #1f1e1c;
    color: #e8e6e3;
}

QPushButton#NavButton:checked {
    background-color: #1f1e1c;
    color: #c0392b;
    font-weight: 600;
    border-left: 3px solid #c0392b;
}

/* --- Content sections --- */
QFrame#Card {
    background-color: #242220;
    border: 1px solid #333130;
    border-radius: 8px;
}

QFrame#HeroCard {
    background-color: #1e3a2f;
    border: 1px solid #2a5a42;
    border-radius: 8px;
}

QFrame#OptionCard {
    background-color: #1f1e1c;
    border: 1px solid #2e2d2b;
    border-radius: 6px;
}

QFrame#OptionCard:hover {
    border-color: #454340;
    background-color: #262523;
}

QFrame#SectionGroup {
    background-color: transparent;
    border: 1px solid #2e2d2b;
    border-radius: 8px;
}

QLabel#PageTitle {
    font-size: 20px;
    font-weight: 700;
    color: #e8e6e3;
}

QLabel#PageSubtitle {
    font-size: 12px;
    color: #8a8784;
    font-weight: 400;
}

QLabel#SectionTitle {
    font-size: 13px;
    font-weight: 700;
    color: #c0392b;
}

QLabel#CardTitle {
    font-size: 11px;
    font-weight: 600;
    color: #8a8784;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

QLabel#MetricValue {
    font-size: 26px;
    font-weight: 700;
    color: #e8e6e3;
}

QLabel#MetricSubtext {
    font-size: 12px;
    color: #8a8784;
}

/* --- Buttons --- */
QPushButton#PrimaryButton {
    background-color: #c0392b;
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 6px;
    padding: 8px 20px;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background-color: #d44637;
}

QPushButton#PrimaryButton:pressed {
    background-color: #a5301f;
}

QPushButton#PrimaryButton:disabled {
    background-color: #2a2827;
    color: #5a5856;
    border: none;
}

QPushButton#SecondaryButton {
    background-color: transparent;
    color: #c8c5c2;
    border: 1px solid #3d3b39;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton#SecondaryButton:hover {
    background-color: #262523;
    color: #e8e6e3;
    border-color: #5a5856;
}

QPushButton#DangerButton {
    background-color: #c0392b;
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 6px;
    padding: 8px 20px;
    border: none;
}

QPushButton#DangerButton:hover {
    background-color: #a5301f;
}

/* --- Tables --- */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #1f1e1c;
    border: 1px solid #2e2d2b;
    border-radius: 6px;
    gridline-color: #2a2827;
    selection-background-color: #2a2827;
    selection-color: #e8e6e3;
    alternate-background-color: #232120;
}

QHeaderView::section {
    background-color: #242220;
    color: #8a8784;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: none;
    border-bottom: 1px solid #333130;
    padding: 8px 12px;
}

/* --- Progress bars --- */
QProgressBar {
    border: none;
    border-radius: 4px;
    text-align: center;
    background-color: #2a2827;
    color: #e8e6e3;
    font-size: 11px;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: #2980b9;
    border-radius: 4px;
}

/* --- Checkboxes --- */
QCheckBox {
    spacing: 8px;
    color: #e8e6e3;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #5a5856;
    border-radius: 3px;
    background-color: transparent;
}

QCheckBox::indicator:hover {
    border-color: #c0392b;
}

QCheckBox::indicator:checked {
    background-color: #c0392b;
    border-color: #c0392b;
}

/* --- Inputs --- */
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #1f1e1c;
    border: 1px solid #3d3b39;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e8e6e3;
    font-weight: 500;
}

QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #5a5856;
}

QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #c0392b;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #242220;
    border: 1px solid #3d3b39;
    selection-background-color: #c0392b;
    selection-color: #ffffff;
    padding: 2px;
}

/* --- Group Boxes (Pav Play section style) --- */
QGroupBox {
    border: 1px solid #2e2d2b;
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px 14px 14px 14px;
    font-weight: 600;
    font-size: 13px;
    color: #e8e6e3;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    color: #e8e6e3;
    font-weight: 700;
}

/* --- Tooltips --- */
QToolTip {
    background-color: #2a2827;
    color: #e8e6e3;
    border: 1px solid #3d3b39;
    padding: 4px 8px;
    font-size: 12px;
}

/* --- Status bar label --- */
QLabel#StatusLabel {
    color: #8a8784;
    font-size: 12px;
}

/* --- Badge pills --- */
QLabel#BadgeGreen {
    color: #27ae60;
    font-weight: 600;
    font-size: 11px;
    background-color: #1a2e1f;
    border: 1px solid #27ae60;
    padding: 3px 10px;
    border-radius: 10px;
}

QLabel#BadgeAmber {
    color: #e67e22;
    font-weight: 600;
    font-size: 11px;
    background-color: #2e2518;
    border: 1px solid #e67e22;
    padding: 3px 10px;
    border-radius: 10px;
}

QLabel#BadgeBlue {
    color: #2980b9;
    font-weight: 600;
    font-size: 11px;
    background-color: #182530;
    border: 1px solid #2980b9;
    padding: 3px 10px;
    border-radius: 10px;
}

QLabel#BadgeMuted {
    color: #8a8784;
    font-weight: 600;
    font-size: 11px;
    background-color: #242220;
    border: 1px solid #3d3b39;
    padding: 3px 10px;
    border-radius: 10px;
}
"""

LIGHT_THEME_QSS = """
/* ========================================================================
   LIGHT THEME — JunksCleaner
   Base:    #eae8df  (warm parchment)
   Surface: #f5f4ee  (card bg)
   Border:  #d5d1c4  (warm grey)
   Text:    #2c2a26  (near-black warm)
   Muted:   #7a766e  (secondary text)
   Accent:  #c0392b  (crimson — titles, active states only)
   ======================================================================== */

QMainWindow, QWidget#CentralWidget, QStackedWidget {
    background-color: #eae8df;
    color: #2c2a26;
}

QWidget {
    font-family: "Segoe UI", "SF Pro Display", -apple-system, sans-serif;
    font-size: 13px;
    color: #2c2a26;
}

/* --- Scrollbars --- */
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background: transparent;
    background-color: #eae8df;
    border: none;
}

QScrollBar:vertical {
    width: 6px;
    background: transparent;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #c5c1b8;
    min-height: 30px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #9e9a92;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    height: 0px;
    background: transparent;
}

/* --- Sidebar --- */
QFrame#Sidebar {
    background-color: #e0ded4;
    border-right: 1px solid #d0cdc4;
}

QFrame#SidebarSeparator {
    background-color: #d0cdc4;
    border: none;
}

QLabel#AppTitle {
    font-size: 15px;
    font-weight: 700;
    color: #2c2a26;
}

QLabel#SidebarSubtitle {
    font-size: 10px;
    color: #8a8680;
    font-weight: 400;
}

QPushButton#NavButton {
    text-align: left;
    padding: 9px 16px;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    background-color: transparent;
    color: #6b675f;
    font-weight: 500;
    font-size: 13px;
}

QPushButton#NavButton:hover {
    background-color: #d8d5cc;
    color: #2c2a26;
}

QPushButton#NavButton:checked {
    background-color: #d8d5cc;
    color: #c0392b;
    font-weight: 600;
    border-left: 3px solid #c0392b;
}

/* --- Content sections --- */
QFrame#Card {
    background-color: #f5f4ee;
    border: 1px solid #d5d1c4;
    border-radius: 8px;
}

QFrame#HeroCard {
    background-color: #eaf5ee;
    border: 1px solid #b8d8c4;
    border-radius: 8px;
}

QFrame#OptionCard {
    background-color: #f0eee6;
    border: 1px solid #dcd8cc;
    border-radius: 6px;
}

QFrame#OptionCard:hover {
    border-color: #b5b0a2;
    background-color: #f8f7f2;
}

QFrame#SectionGroup {
    background-color: transparent;
    border: 1px solid #d5d1c4;
    border-radius: 8px;
}

QLabel#PageTitle {
    font-size: 20px;
    font-weight: 700;
    color: #2c2a26;
}

QLabel#PageSubtitle {
    font-size: 12px;
    color: #7a766e;
    font-weight: 400;
}

QLabel#SectionTitle {
    font-size: 13px;
    font-weight: 700;
    color: #c0392b;
}

QLabel#CardTitle {
    font-size: 11px;
    font-weight: 600;
    color: #7a766e;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

QLabel#MetricValue {
    font-size: 26px;
    font-weight: 700;
    color: #2c2a26;
}

QLabel#MetricSubtext {
    font-size: 12px;
    color: #7a766e;
}

/* --- Buttons --- */
QPushButton#PrimaryButton {
    background-color: #c0392b;
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 6px;
    padding: 8px 20px;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background-color: #d44637;
}

QPushButton#PrimaryButton:pressed {
    background-color: #a5301f;
}

QPushButton#PrimaryButton:disabled {
    background-color: #dcd8cc;
    color: #a8a29e;
    border: none;
}

QPushButton#SecondaryButton {
    background-color: transparent;
    color: #4a4740;
    border: 1px solid #c5c1b8;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton#SecondaryButton:hover {
    background-color: #f0eee6;
    color: #2c2a26;
    border-color: #9e9a92;
}

QPushButton#DangerButton {
    background-color: #c0392b;
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 6px;
    padding: 8px 20px;
    border: none;
}

QPushButton#DangerButton:hover {
    background-color: #a5301f;
}

/* --- Tables --- */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #f5f4ee;
    border: 1px solid #d5d1c4;
    border-radius: 6px;
    gridline-color: #e8e6de;
    selection-background-color: #e0ded4;
    selection-color: #2c2a26;
    alternate-background-color: #f0eee6;
}

QHeaderView::section {
    background-color: #eae8df;
    color: #7a766e;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: none;
    border-bottom: 1px solid #d5d1c4;
    padding: 8px 12px;
}

/* --- Progress bars --- */
QProgressBar {
    border: none;
    border-radius: 4px;
    text-align: center;
    background-color: #dcd8cc;
    color: #2c2a26;
    font-size: 11px;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: #2980b9;
    border-radius: 4px;
}

/* --- Checkboxes --- */
QCheckBox {
    spacing: 8px;
    color: #2c2a26;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #b5b0a2;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border-color: #c0392b;
}

QCheckBox::indicator:checked {
    background-color: #c0392b;
    border-color: #c0392b;
}

/* --- Inputs --- */
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #c5c1b8;
    border-radius: 4px;
    padding: 6px 10px;
    color: #2c2a26;
    font-weight: 500;
}

QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #9e9a92;
}

QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #c0392b;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d5d1c4;
    selection-background-color: #c0392b;
    selection-color: #ffffff;
    padding: 2px;
}

/* --- Group Boxes --- */
QGroupBox {
    border: 1px solid #d5d1c4;
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px 14px 14px 14px;
    font-weight: 600;
    font-size: 13px;
    color: #2c2a26;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    color: #2c2a26;
    font-weight: 700;
}

/* --- Tooltips --- */
QToolTip {
    background-color: #f5f4ee;
    color: #2c2a26;
    border: 1px solid #d5d1c4;
    padding: 4px 8px;
    font-size: 12px;
}

/* --- Status bar label --- */
QLabel#StatusLabel {
    color: #7a766e;
    font-size: 12px;
}

/* --- Badge pills --- */
QLabel#BadgeGreen {
    color: #27ae60;
    font-weight: 600;
    font-size: 11px;
    background-color: #e8f5ec;
    border: 1px solid #27ae60;
    padding: 3px 10px;
    border-radius: 10px;
}

QLabel#BadgeAmber {
    color: #e67e22;
    font-weight: 600;
    font-size: 11px;
    background-color: #fdf0e0;
    border: 1px solid #e67e22;
    padding: 3px 10px;
    border-radius: 10px;
}

QLabel#BadgeBlue {
    color: #2980b9;
    font-weight: 600;
    font-size: 11px;
    background-color: #e0f0fb;
    border: 1px solid #2980b9;
    padding: 3px 10px;
    border-radius: 10px;
}

QLabel#BadgeMuted {
    color: #7a766e;
    font-weight: 600;
    font-size: 11px;
    background-color: #eae8df;
    border: 1px solid #c5c1b8;
    padding: 3px 10px;
    border-radius: 10px;
}
"""


def get_stylesheet(theme_name: str) -> str:
    """Return the Qt stylesheet matching the requested theme name."""
    if theme_name.lower() == "light":
        return LIGHT_THEME_QSS
    return DARK_THEME_QSS
