"""Activity and audit report page displaying historical cleanup records."""

import time

from junkscleaner.services.cleaner import JunkCleanerService
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ActivityPage(QWidget):
    """View displaying historical audit logs of cleanup operations."""

    def __init__(self, service: JunkCleanerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        title = QLabel("Activity & Reports")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Local audit trail of all previous preview, deletion, and memory runs")
        subtitle.setStyleSheet("color: #888888; font-size: 13px;")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addLayout(header_text)
        header_layout.addStretch()

        self.clear_btn = QPushButton("Clear History")
        self.clear_btn.setObjectName("SecondaryButton")
        self.clear_btn.clicked.connect(self._clear_history)
        header_layout.addWidget(self.clear_btn)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                "Timestamp",
                "Duration",
                "Selected",
                "Deleted",
                "Actual Freed",
                "Status",
            ]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        """Refresh table from service audit history."""
        history = self.service.get_audit_history()
        self.table.setRowCount(len(history))

        for row, rep in enumerate(reversed(history)):
            ts_str = time.strftime("%Y-%m-%d %H:%M:%S")
            self.table.setItem(row, 0, QTableWidgetItem(ts_str))
            self.table.setItem(row, 1, QTableWidgetItem(f"{rep.duration_ms} ms"))
            self.table.setItem(row, 2, QTableWidgetItem(str(rep.selected_count)))
            self.table.setItem(row, 3, QTableWidgetItem(str(rep.deleted_count)))
            self.table.setItem(row, 4, QTableWidgetItem(rep.actual_deleted_display))

            status_txt = (
                "Cancelled"
                if rep.was_cancelled
                else ("Partial" if rep.failed_count > 0 or rep.skipped_count > 0 else "Success")
            )
            self.table.setItem(row, 5, QTableWidgetItem(status_txt))

    def _clear_history(self) -> None:
        self.service.clear_audit_history()
        self.refresh()
