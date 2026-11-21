"""Junk cleaner page providing interactive scan, preview, confirmation, and safe deletion."""

from junkscleaner.native.types import (
    JcCleanupItem,
    JcCleanupReport,
    JcScanResult,
    format_bytes,
)
from junkscleaner.services.cleaner import JunkCleanerService
from junkscleaner.workers.cleaner_worker import CleanWorker, ScanWorker
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CleanerPage(QWidget):
    """Interactive Junk Cleaner page."""

    cleanup_completed = Signal(object)  # Emits JcCleanupReport

    def __init__(self, service: JunkCleanerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._scan_result: JcScanResult | None = None
        self._scan_worker: ScanWorker | None = None
        self._clean_worker: CleanWorker | None = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # ── Header ───────────────────────────────────────────────────
        header = QVBoxLayout()
        header.setSpacing(4)
        title = QLabel("Junk Cleaner")
        title.setObjectName("PageTitle")
        header.addWidget(title)

        subtitle = QLabel("Preview and safely remove disposable temporary files")
        subtitle.setObjectName("PageSubtitle")
        header.addWidget(subtitle)
        layout.addLayout(header)

        # ── Toolbar row ──────────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.scan_button = QPushButton("Scan for Junk")
        self.scan_button.setObjectName("PrimaryButton")
        self.scan_button.clicked.connect(self._start_scan)
        toolbar.addWidget(self.scan_button)

        self.status_label = QLabel("Ready. Click Scan to search temporary folders.")
        self.status_label.setObjectName("StatusLabel")
        toolbar.addWidget(self.status_label)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Progress bar (indeterminate)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # ── Preview table ────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Item", "Path", "Size", "Risk", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemChanged.connect(self._on_table_item_changed)
        layout.addWidget(self.table)

        # ── Action bar ───────────────────────────────────────────────
        self.action_frame = QFrame()
        self.action_frame.setObjectName("Card")
        action_layout = QHBoxLayout(self.action_frame)
        action_layout.setContentsMargins(14, 10, 14, 10)
        action_layout.setSpacing(8)

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setObjectName("SecondaryButton")
        self.select_all_btn.clicked.connect(self._select_all)
        action_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.setObjectName("SecondaryButton")
        self.deselect_all_btn.clicked.connect(self._deselect_all)
        action_layout.addWidget(self.deselect_all_btn)

        action_layout.addStretch()

        self.summary_label = QLabel("0 items selected (0 B)")
        self.summary_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        action_layout.addWidget(self.summary_label)

        self.dry_run_btn = QPushButton("Dry Run")
        self.dry_run_btn.setObjectName("SecondaryButton")
        self.dry_run_btn.clicked.connect(lambda: self._confirm_and_clean(is_dry_run=True))
        action_layout.addWidget(self.dry_run_btn)

        self.clean_button = QPushButton("Delete Selected")
        self.clean_button.setObjectName("DangerButton")
        self.clean_button.clicked.connect(lambda: self._confirm_and_clean(is_dry_run=False))
        action_layout.addWidget(self.clean_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("SecondaryButton")
        self.cancel_button.clicked.connect(self._cancel_active_operation)
        self.cancel_button.hide()
        action_layout.addWidget(self.cancel_button)

        self.action_frame.setEnabled(False)
        layout.addWidget(self.action_frame)

    @Slot()
    def _start_scan(self) -> None:
        """Trigger background scanning."""
        self.scan_button.setEnabled(False)
        self.action_frame.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText("Scanning temporary folders\u2026")

        self._scan_worker = ScanWorker(self.service, parent=self)
        self._scan_worker.scan_finished.connect(self._on_scan_finished)
        self._scan_worker.scan_failed.connect(self._on_scan_failed)
        self._scan_worker.start()

    @Slot(object)
    def _on_scan_finished(self, result: JcScanResult) -> None:
        self.progress_bar.hide()
        self.scan_button.setEnabled(True)
        self._scan_result = result

        self.table.blockSignals(True)
        self.table.setRowCount(len(result.items))

        for row, item in enumerate(result.items):
            check_item = QTableWidgetItem(item.display_path)
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            check_item.setCheckState(Qt.Checked if not item.is_locked else Qt.Unchecked)
            self.table.setItem(row, 0, check_item)

            self.table.setItem(row, 1, QTableWidgetItem(item.relative_path))
            self.table.setItem(row, 2, QTableWidgetItem(item.size_display))
            self.table.setItem(row, 3, QTableWidgetItem(item.risk_level.name))

            status_txt = "Locked" if item.is_locked else "Ready"
            self.table.setItem(row, 4, QTableWidgetItem(status_txt))

        self.table.blockSignals(False)

        count = len(result.items)
        size_txt = result.total_estimated_display
        self.status_label.setText(f"Found {count} candidates ({size_txt})")
        self.action_frame.setEnabled(count > 0)
        self._update_selection_summary()

    @Slot(str)
    def _on_scan_failed(self, error_msg: str) -> None:
        self.progress_bar.hide()
        self.scan_button.setEnabled(True)
        self.status_label.setText(f"Scan failed: {error_msg}")
        QMessageBox.critical(self, "Scan Error", f"Failed to complete scan:\n{error_msg}")

    def _get_selected_items(self) -> list[JcCleanupItem]:
        if not self._scan_result:
            return []
        selected: list[JcCleanupItem] = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                selected.append(self._scan_result.items[row])
        return selected

    def _update_selection_summary(self) -> None:
        selected = self._get_selected_items()
        total_bytes = sum(it.size_bytes for it in selected)
        self.summary_label.setText(f"{len(selected)} items selected ({format_bytes(total_bytes)})")
        self.clean_button.setEnabled(len(selected) > 0)
        self.dry_run_btn.setEnabled(len(selected) > 0)

    @Slot(QTableWidgetItem)
    def _on_table_item_changed(self, item: QTableWidgetItem) -> None:
        if item.column() == 0:
            self._update_selection_summary()

    @Slot()
    def _select_all(self) -> None:
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Checked)
        self.table.blockSignals(False)
        self._update_selection_summary()

    @Slot()
    def _deselect_all(self) -> None:
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Unchecked)
        self.table.blockSignals(False)
        self._update_selection_summary()

    def _confirm_and_clean(self, is_dry_run: bool) -> None:
        selected = self._get_selected_items()
        if not selected:
            return

        total_bytes = sum(it.size_bytes for it in selected)
        size_txt = format_bytes(total_bytes)

        if not is_dry_run:
            res = QMessageBox.warning(
                self,
                "Confirm Deletion",
                f"Are you sure you want to permanently delete {len(selected)} temporary files "
                f"({size_txt})?\n\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.Cancel,
                QMessageBox.Cancel,
            )
            if res != QMessageBox.Yes:
                return

        self.scan_button.setEnabled(False)
        self.clean_button.setEnabled(False)
        self.dry_run_btn.setEnabled(False)
        self.cancel_button.show()
        self.progress_bar.show()

        action_name = "Simulating cleanup" if is_dry_run else "Deleting selected files"
        self.status_label.setText(f"{action_name}\u2026")

        self._clean_worker = CleanWorker(
            self.service,
            items=selected,
            confirmed=True,
            is_dry_run=is_dry_run,
            parent=self,
        )
        self._clean_worker.clean_finished.connect(self._on_clean_finished)
        self._clean_worker.clean_failed.connect(self._on_clean_failed)
        self._clean_worker.start()

    @Slot(object)
    def _on_clean_finished(self, report: JcCleanupReport) -> None:
        self.progress_bar.hide()
        self.cancel_button.hide()
        self.scan_button.setEnabled(True)
        self.clean_button.setEnabled(True)
        self.dry_run_btn.setEnabled(True)

        status_prefix = (
            "Dry Run Complete"
            if self._clean_worker and self._clean_worker.is_dry_run
            else "Cleanup Complete"
        )
        msg = (
            f"Removed: {report.deleted_count} files "
            f"({report.actual_deleted_display})\n"
            f"Skipped: {report.skipped_count}\n"
            f"Failed: {report.failed_count}\n"
            f"Duration: {report.duration_ms} ms"
        )
        if report.was_cancelled:
            msg += "\n\nOperation was cancelled."

        QMessageBox.information(self, status_prefix, msg)
        self.status_label.setText(f"Done \u2014 {report.actual_deleted_display} freed")
        self.cleanup_completed.emit(report)
        self._start_scan()

    @Slot(str)
    def _on_clean_failed(self, error_msg: str) -> None:
        self.progress_bar.hide()
        self.cancel_button.hide()
        self.scan_button.setEnabled(True)
        self.clean_button.setEnabled(True)
        self.dry_run_btn.setEnabled(True)
        self.status_label.setText(f"Error: {error_msg}")
        QMessageBox.critical(
            self, "Cleanup Failed", f"Error during cleanup:\n{error_msg}"
        )

    @Slot()
    def _cancel_active_operation(self) -> None:
        if self._clean_worker:
            self._clean_worker.cancel()
            self.status_label.setText("Cancelling\u2026")
