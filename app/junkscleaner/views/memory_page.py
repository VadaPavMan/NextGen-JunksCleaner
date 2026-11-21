"""Memory cleaning page providing granular RAM optimization and transparent privilege handling."""

from junkscleaner.native.types import (
    JcMemoryCleanResult,
    JcMemoryOperationFlags,
    JcSnapshotValidityFlags,
    JcSystemSnapshot,
    format_bytes,
)
from junkscleaner.services.memory import MemoryCleanerService
from junkscleaner.workers.memory_worker import MemoryCleanWorker
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MemoryPage(QWidget):
    """Interactive Clean Memory page for RAM optimization."""

    memory_cleaned = Signal(object)  # Emits JcMemoryCleanResult

    def __init__(self, service: MemoryCleanerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._worker: MemoryCleanWorker | None = None
        self._is_elevated = self.service.is_elevated()

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 1. Header
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        title = QLabel("Clean Memory")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        subtitle = QLabel(
            "Safe RAM optimization and cache reclamation with transparent privilege disclosure"
        )
        subtitle.setStyleSheet("color: #71717a; font-size: 13px;")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addLayout(header_text)
        header_layout.addStretch()

        # Elevation badge
        elev_label = QLabel(
            "● Running as Administrator" if self._is_elevated else "○ Running as Standard User"
        )
        elev_style = (
            "color: #10b981; font-weight: bold; background: #064e3b; "
            "padding: 6px 12px; border-radius: 6px;"
            if self._is_elevated
            else "color: #94a3b8; font-weight: 500; background: #1e293b; "
            "padding: 6px 12px; border-radius: 6px;"
        )
        elev_label.setStyleSheet(elev_style)
        header_layout.addWidget(elev_label)
        layout.addLayout(header_layout)

        # 2. Live Memory Telemetry Card
        self.telemetry_card = QFrame()
        self.telemetry_card.setObjectName("Card")
        telemetry_layout = QVBoxLayout(self.telemetry_card)

        card_title = QLabel("System Memory Overview")
        card_title.setObjectName("CardTitle")
        telemetry_layout.addWidget(card_title)

        stats_row = QHBoxLayout()
        self.lbl_used_ram = QLabel("Used: --")
        self.lbl_used_ram.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.lbl_avail_ram = QLabel("Available: --")
        self.lbl_avail_ram.setStyleSheet("font-size: 14px; color: #10b981;")
        self.lbl_cached_ram = QLabel("Cache / Standby: --")
        self.lbl_cached_ram.setStyleSheet("font-size: 14px; color: #a1a1aa;")
        self.lbl_total_ram = QLabel("Total: --")
        self.lbl_total_ram.setStyleSheet("font-size: 14px; color: #71717a;")

        stats_row.addWidget(self.lbl_used_ram)
        stats_row.addWidget(self.lbl_avail_ram)
        stats_row.addWidget(self.lbl_cached_ram)
        stats_row.addWidget(self.lbl_total_ram)
        stats_row.addStretch()
        telemetry_layout.addLayout(stats_row)

        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setValue(0)
        self.memory_progress.setTextVisible(True)
        self.memory_progress.setFixedHeight(12)
        telemetry_layout.addWidget(self.memory_progress)

        layout.addWidget(self.telemetry_card)

        # 3. Operations Selection Card
        ops_card = QFrame()
        ops_card.setObjectName("Card")
        ops_layout = QVBoxLayout(ops_card)

        ops_title = QLabel("Optimization Targets")
        ops_title.setObjectName("CardTitle")
        ops_layout.addWidget(ops_title)

        # Checkboxes with descriptions
        self.cb_working_sets = QCheckBox("Process Working Sets")
        self.cb_working_sets.setChecked(True)
        self.cb_working_sets.setStyleSheet("font-weight: bold;")
        lbl_ws_desc = QLabel(
            "Trims working sets of running processes to release inactive memory pages. "
            "(Unprivileged / Standard User)"
        )
        desc_style = "color: #71717a; font-size: 12px; margin-left: 20px; margin-bottom: 8px;"
        lbl_ws_desc.setStyleSheet(desc_style)
        ops_layout.addWidget(self.cb_working_sets)
        ops_layout.addWidget(lbl_ws_desc)

        self.cb_system_cache = QCheckBox("System File Cache")
        self.cb_system_cache.setChecked(self._is_elevated)
        self.cb_system_cache.setStyleSheet("font-weight: bold;")
        lbl_sc_desc = QLabel(
            "Flushes the system working set and file system cache. (Requires Administrator)"
        )
        lbl_sc_desc.setStyleSheet(desc_style)
        ops_layout.addWidget(self.cb_system_cache)
        ops_layout.addWidget(lbl_sc_desc)

        self.cb_standby_list = QCheckBox("Standby Page List")
        self.cb_standby_list.setChecked(self._is_elevated)
        self.cb_standby_list.setStyleSheet("font-weight: bold;")
        lbl_sb_desc = QLabel(
            "Purges cached standby pages into free memory. Note: Standby memory is already "
            "available when needed; purging may cause subsequent reads to hit disk. (Admin)"
        )
        lbl_sb_desc.setStyleSheet(desc_style)
        ops_layout.addWidget(self.cb_standby_list)
        ops_layout.addWidget(lbl_sb_desc)

        self.cb_modified_list = QCheckBox("Modified Page List")
        self.cb_modified_list.setChecked(False)
        self.cb_modified_list.setStyleSheet("font-weight: bold;")
        lbl_mod_desc = QLabel(
            "Forces memory manager to flush modified pages to disk or pagefile. (Requires Admin)"
        )
        lbl_mod_desc.setStyleSheet("color: #71717a; font-size: 12px; margin-left: 20px;")
        ops_layout.addWidget(self.cb_modified_list)
        ops_layout.addWidget(lbl_mod_desc)

        layout.addWidget(ops_card)

        # 4. Action bar & Warning Disclosure
        action_layout = QHBoxLayout()
        self.btn_clean = QPushButton("Clean Memory")
        self.btn_clean.setObjectName("PrimaryButton")
        self.btn_clean.setFixedHeight(36)
        self.btn_clean.clicked.connect(self._on_clean_clicked)

        self.status_label = QLabel("Select targets above and click Clean Memory")
        self.status_label.setStyleSheet("color: #71717a;")

        action_layout.addWidget(self.btn_clean)
        action_layout.addWidget(self.status_label)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        # 5. Results Card (initially hidden)
        self.result_card = QFrame()
        self.result_card.setObjectName("Card")
        self.result_card.setVisible(False)
        result_layout = QVBoxLayout(self.result_card)

        res_title = QLabel("Last Optimization Result")
        res_title.setObjectName("CardTitle")
        result_layout.addWidget(res_title)

        res_metrics_row = QHBoxLayout()
        self.res_reclaimed_label = QLabel("Reclaimed: --")
        self.res_reclaimed_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #10b981;"
        )
        self.res_before_after = QLabel("Before: -- | After: --")
        self.res_before_after.setStyleSheet("font-size: 13px; color: #a1a1aa;")
        self.res_processes = QLabel("Processes Trimmed: --")
        self.res_processes.setStyleSheet("font-size: 13px; color: #a1a1aa;")

        res_metrics_row.addWidget(self.res_reclaimed_label)
        res_metrics_row.addWidget(self.res_before_after)
        res_metrics_row.addWidget(self.res_processes)
        res_metrics_row.addStretch()
        result_layout.addLayout(res_metrics_row)

        layout.addWidget(self.result_card)
        layout.addStretch()

    @Slot(object)
    def update_snapshot(self, snap: JcSystemSnapshot) -> None:
        """Update live telemetry header from background monitor snapshot."""
        if not snap:
            return

        total = snap.memory_total_bytes
        used = snap.memory_used_bytes
        avail = snap.memory_available_bytes
        cached = snap.memory_cached_bytes

        if snap.is_valid(JcSnapshotValidityFlags.MEM_USED) and total > 0:
            pct = int((used / total) * 100)
            self.memory_progress.setValue(pct)
            self.memory_progress.setFormat(
                f"{pct}% Used ({format_bytes(used)} / {format_bytes(total)})"
            )
            self.lbl_used_ram.setText(f"Used: {format_bytes(used)}")
            self.lbl_total_ram.setText(f"Total: {format_bytes(total)}")

        if snap.is_valid(JcSnapshotValidityFlags.MEM_AVAILABLE):
            self.lbl_avail_ram.setText(f"Available: {format_bytes(avail)}")

        if snap.is_valid(JcSnapshotValidityFlags.MEM_CACHED):
            self.lbl_cached_ram.setText(f"Cache / Standby: {format_bytes(cached)}")

    def _get_selected_mask(self) -> int:
        mask = JcMemoryOperationFlags.NONE
        if self.cb_working_sets.isChecked():
            mask |= JcMemoryOperationFlags.WORKING_SETS
        if self.cb_system_cache.isChecked():
            mask |= JcMemoryOperationFlags.SYSTEM_CACHE
        if self.cb_standby_list.isChecked():
            mask |= JcMemoryOperationFlags.STANDBY_LIST
        if self.cb_modified_list.isChecked():
            mask |= JcMemoryOperationFlags.MODIFIED_LIST
        return int(mask)

    @Slot()
    def _on_clean_clicked(self) -> None:
        mask = self._get_selected_mask()
        if mask == 0:
            QMessageBox.warning(
                self,
                "No Targets Selected",
                "Please select at least one memory optimization target.",
            )
            return

        # Check for admin-only options if unprivileged
        needs_admin = (
            (mask & JcMemoryOperationFlags.SYSTEM_CACHE)
            or (mask & JcMemoryOperationFlags.STANDBY_LIST)
            or (mask & JcMemoryOperationFlags.MODIFIED_LIST)
        )
        if needs_admin and not self._is_elevated:
            ret = QMessageBox.question(
                self,
                "Administrator Rights Recommended",
                "You selected operations that require Administrator privileges "
                "(System Cache, Standby List, or Modified List).\n\n"
                "In standard user mode, these operations may be skipped or denied.\n\n"
                "Do you want to proceed anyway with available permissions?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if ret != QMessageBox.Yes:
                return

        self.btn_clean.setEnabled(False)
        self.status_label.setText("Optimizing memory targets...")

        self._worker = MemoryCleanWorker(service=self.service, operations=mask, parent=self)
        self._worker.clean_finished.connect(self._on_clean_finished)
        self._worker.clean_failed.connect(self._on_clean_failed)
        self._worker.start()

    @Slot(object)
    def _on_clean_finished(self, result: JcMemoryCleanResult) -> None:
        self.btn_clean.setEnabled(True)
        reclaimed_text = f"Optimization completed. Reclaimed {result.bytes_reclaimed_display}."
        self.status_label.setText(reclaimed_text)

        # Display result card
        self.result_card.setVisible(True)
        self.res_reclaimed_label.setText(f"Reclaimed: {result.bytes_reclaimed_display}")
        self.res_before_after.setText(
            f"Before: {result.before_used_display}  |  After: {result.after_used_display}"
        )
        self.res_processes.setText(
            f"Processes Trimmed: {result.processes_trimmed} (Skipped: {result.processes_failed})"
        )

        self.memory_cleaned.emit(result)

    @Slot(str)
    def _on_clean_failed(self, error_msg: str) -> None:
        self.btn_clean.setEnabled(True)
        self.status_label.setText("Optimization failed.")
        QMessageBox.critical(
            self,
            "Memory Optimization Error",
            f"Failed to execute memory cleaning:\n\n{error_msg}",
        )
