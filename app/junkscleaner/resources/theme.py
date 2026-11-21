"""Themes and styling for JunksCleaner."""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #0b0f19;
    color: #f1f5f9;
}

QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Inter", "Ubuntu", sans-serif;
    font-size: 13px;
    color: #f1f5f9;
}

/* Sidebar navigation */
QFrame#Sidebar {
    background-color: #0f1423;
    border-right: 1px solid #1a2236;
}

QLabel#AppTitle {
    font-size: 17px;
    font-weight: 700;
    color: #ffffff;
    padding: 8px 4px;
    letter-spacing: -0.3px;
}

QLabel#SidebarSubtitle {
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
    padding-left: 4px;
    margin-bottom: 8px;
}

QPushButton#NavButton {
    text-align: left;
    padding: 10px 14px;
    border: 1px solid transparent;
    border-radius: 8px;
    background-color: transparent;
    color: #94a3b8;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#NavButton:hover {
    background-color: #161e31;
    color: #f8fafc;
    border: 1px solid #23304d;
}

QPushButton#NavButton:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #2563eb);
    color: #ffffff;
    font-weight: 700;
    border: 1px solid #60a5fa;
}

/* Content cards */
QFrame#Card {
    background-color: #131929;
    border: 1px solid #1f2942;
    border-radius: 10px;
    padding: 18px;
}

QFrame#HeroCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #131929, stop:1 #162035);
    border: 1px solid #283759;
    border-radius: 10px;
    padding: 18px;
}

QFrame#OptionCard {
    background-color: #101524;
    border: 1px solid #1c253b;
    border-radius: 8px;
    padding: 12px 14px;
}

QFrame#OptionCard:hover {
    border: 1px solid #2b395b;
    background-color: #13192c;
}

QLabel#CardTitle {
    font-size: 11px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

QLabel#MetricValue {
    font-size: 28px;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: -0.5px;
}

QLabel#MetricSubtext {
    font-size: 12px;
    color: #64748b;
}

/* Primary / Secondary / Danger Buttons */
QPushButton#PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #3b82f6);
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 8px;
    padding: 9px 20px;
    border: 1px solid #60a5fa;
}

QPushButton#PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #2563eb);
    border: 1px solid #93c5fd;
}

QPushButton#PrimaryButton:disabled {
    background-color: #171e30;
    color: #475569;
    border: 1px solid #24304c;
}

QPushButton#SecondaryButton {
    background-color: #161c2e;
    color: #cbd5e1;
    border: 1px solid #24304c;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton#SecondaryButton:hover {
    background-color: #1d253d;
    color: #ffffff;
    border: 1px solid #3b82f6;
}

QPushButton#DangerButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #ef4444);
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 8px;
    padding: 9px 20px;
    border: 1px solid #f87171;
}

QPushButton#DangerButton:hover {
    background: #b91c1c;
    border: 1px solid #fca5a5;
}

/* Tables and Lists */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #0f1424;
    border: 1px solid #1c253b;
    border-radius: 8px;
    gridline-color: #182033;
    selection-background-color: #1e293b;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #13192b;
    color: #94a3b8;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: none;
    padding: 8px 12px;
}

QProgressBar {
    border: 1px solid #1c253b;
    border-radius: 6px;
    text-align: center;
    background-color: #0c101c;
    color: #cbd5e1;
    font-size: 11px;
    font-weight: 600;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #06b6d4);
    border-radius: 5px;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #f1f5f9;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #28334f;
    border-radius: 4px;
    background-color: #0f1424;
}

QCheckBox::indicator:hover {
    border: 1px solid #3b82f6;
    background-color: #161e31;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border: 1px solid #60a5fa;
}
"""

LIGHT_THEME_QSS = """
QMainWindow {
    background-color: #f8fafc;
    color: #0f172a;
}

QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Inter", "Ubuntu", sans-serif;
    font-size: 13px;
    color: #0f172a;
}

/* Sidebar navigation */
QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

QLabel#AppTitle {
    font-size: 17px;
    font-weight: 700;
    color: #0f172a;
    padding: 8px 4px;
    letter-spacing: -0.3px;
}

QLabel#SidebarSubtitle {
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
    padding-left: 4px;
    margin-bottom: 8px;
}

QPushButton#NavButton {
    text-align: left;
    padding: 10px 14px;
    border: 1px solid transparent;
    border-radius: 8px;
    background-color: transparent;
    color: #64748b;
    font-weight: 600;
    font-size: 13px;
}

QPushButton#NavButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
    border: 1px solid #e2e8f0;
}

QPushButton#NavButton:checked {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 700;
    border: 1px solid #1d4ed8;
}

/* Content cards */
QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px;
}

QFrame#HeroCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f8fafc);
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 18px;
}

QFrame#OptionCard {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 14px;
}

QFrame#OptionCard:hover {
    border: 1px solid #cbd5e1;
    background-color: #ffffff;
}

QLabel#CardTitle {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

QLabel#MetricValue {
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.5px;
}

QLabel#MetricSubtext {
    font-size: 12px;
    color: #64748b;
}

/* Primary / Secondary / Danger Buttons */
QPushButton#PrimaryButton {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 8px;
    padding: 9px 20px;
    border: 1px solid #1d4ed8;
}

QPushButton#PrimaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#PrimaryButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
    border: 1px solid #cbd5e1;
}

QPushButton#SecondaryButton {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton#SecondaryButton:hover {
    background-color: #f1f5f9;
    border: 1px solid #94a3b8;
}

QPushButton#DangerButton {
    background-color: #dc2626;
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    border-radius: 8px;
    padding: 9px 20px;
    border: 1px solid #b91c1c;
}

QPushButton#DangerButton:hover {
    background-color: #b91c1c;
}

/* Tables and Lists */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    selection-background-color: #e2e8f0;
    selection-color: #0f172a;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #64748b;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: none;
    padding: 8px 12px;
}

QProgressBar {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    text-align: center;
    background-color: #f1f5f9;
    color: #475569;
    font-size: 11px;
    font-weight: 600;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #06b6d4);
    border-radius: 5px;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #0f172a;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border: 1px solid #2563eb;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border: 1px solid #1d4ed8;
}
"""


def get_stylesheet(theme_name: str) -> str:
    """Return the Qt stylesheet matching the requested theme name."""
    if theme_name.lower() == "light":
        return LIGHT_THEME_QSS
    return DARK_THEME_QSS
