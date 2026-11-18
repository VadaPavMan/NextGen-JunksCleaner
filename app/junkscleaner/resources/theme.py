"""Themes and styling for JunksCleaner."""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #121214;
    color: #f3f4f6;
}

QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Ubuntu", sans-serif;
    font-size: 13px;
    color: #f3f4f6;
}

/* Sidebar navigation */
QFrame#Sidebar {
    background-color: #1a1a1e;
    border-right: 1px solid #27272a;
}

QLabel#AppTitle {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
    padding: 16px 12px;
}

QPushButton#NavButton {
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    background-color: transparent;
    color: #a1a1aa;
    font-weight: 500;
}

QPushButton#NavButton:hover {
    background-color: #27272a;
    color: #ffffff;
}

QPushButton#NavButton:checked {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: bold;
}

/* Content cards */
QFrame#Card {
    background-color: #1e1e24;
    border: 1px solid #2e2e38;
    border-radius: 8px;
    padding: 16px;
}

QLabel#CardTitle {
    font-size: 14px;
    font-weight: bold;
    color: #d4d4d8;
}

QLabel#MetricValue {
    font-size: 28px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#MetricSubtext {
    font-size: 12px;
    color: #a1a1aa;
}

/* Primary / Secondary Buttons */
QPushButton#PrimaryButton {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#PrimaryButton:disabled {
    background-color: #3f3f46;
    color: #71717a;
}

QPushButton#DangerButton {
    background-color: #dc2626;
    color: #ffffff;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}

QPushButton#DangerButton:hover {
    background-color: #b91c1c;
}

QPushButton#SecondaryButton {
    background-color: #27272a;
    color: #f3f4f6;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 8px 16px;
}

QPushButton#SecondaryButton:hover {
    background-color: #3f3f46;
}

/* Tables and Lists */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 6px;
    gridline-color: #27272a;
}

QHeaderView::section {
    background-color: #27272a;
    color: #d4d4d8;
    font-weight: bold;
    border: none;
    padding: 6px 8px;
}

QProgressBar {
    border: 1px solid #27272a;
    border-radius: 4px;
    text-align: center;
    background-color: #18181b;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 3px;
}
"""

LIGHT_THEME_QSS = """
QMainWindow {
    background-color: #f8fafc;
    color: #0f172a;
}

QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Ubuntu", sans-serif;
    font-size: 13px;
    color: #0f172a;
}

/* Sidebar navigation */
QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

QLabel#AppTitle {
    font-size: 16px;
    font-weight: bold;
    color: #0f172a;
    padding: 16px 12px;
}

QPushButton#NavButton {
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    background-color: transparent;
    color: #64748b;
    font-weight: 500;
}

QPushButton#NavButton:hover {
    background-color: #f1f5f9;
    color: #0f172a;
}

QPushButton#NavButton:checked {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: bold;
}

/* Content cards */
QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
}

QLabel#CardTitle {
    font-size: 14px;
    font-weight: bold;
    color: #334155;
}

QLabel#MetricValue {
    font-size: 28px;
    font-weight: bold;
    color: #0f172a;
}

QLabel#MetricSubtext {
    font-size: 12px;
    color: #64748b;
}

/* Primary / Secondary Buttons */
QPushButton#PrimaryButton {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#PrimaryButton:disabled {
    background-color: #cbd5e1;
    color: #94a3b8;
}

QPushButton#DangerButton {
    background-color: #dc2626;
    color: #ffffff;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}

QPushButton#DangerButton:hover {
    background-color: #b91c1c;
}

QPushButton#SecondaryButton {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 16px;
}

QPushButton#SecondaryButton:hover {
    background-color: #f1f5f9;
}

/* Tables and Lists */
QTableWidget, QTreeWidget, QListWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    gridline-color: #f1f5f9;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #334155;
    font-weight: bold;
    border: none;
    padding: 6px 8px;
}

QProgressBar {
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    text-align: center;
    background-color: #ffffff;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 3px;
}
"""


def get_stylesheet(theme_name: str) -> str:
    """Return the Qt stylesheet matching the requested theme name."""
    if theme_name.lower() == "light":
        return LIGHT_THEME_QSS
    return DARK_THEME_QSS
