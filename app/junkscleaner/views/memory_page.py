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

        # 1. Header with live privilege chip
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        title = QLabel("⚡ Clean Memory")
        title.setStyleSheet("font-size: 22px; font-weight: bold; letter-spacing: -0.4px;")
        subtitle = QLabel(
            "Safe RAM optimization & cache reclamation inspired by Mem Reduct and WinMemoryCleaner"
        )
        subtitle.setStyleSheet("color: #71717a; font-size: 13px;")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addLayout(header_text)
        header_layout.addStretch()

        # Elevation badge
        elev_label = QLabel(
            "● Administrator Mode" if self._is_elevated else "○ Standard User Mode"
        )
        elev_style = (
            "color: #10b981; font-weight: 700; font-size: 12px; "
            "background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); "
            "padding: 6px 14px; border-radius: 12px;"
            if self._is_elevated
            else "color: #94a3b8; font-weight: 600; font-size: 12px; "
            "background: rgba(148, 163, 184, 0.10); border: 1px solid rgba(148, 163, 184, 0.25); "
            "padding: 6px 14px; border-radius: 12px;"
        )
        elev_label.setStyleSheet(elev_style)
        header_layout.addWidget(elev_label)
        layout.addLayout(header_layout)

        # 2. Live Memory Telemetry Card with accent border
        self.telemetry_card = QFrame()
        self.telemetry_card.setObjectName("Card")
        self.telemetry_card.setStyleSheet(
            "QFrame#Card { border-top: 3px solid #10b981; }"
        )
        telemetry_layout = QVBoxLayout(self.telemetry_card)
        telemetry_layout.setContentsMargins(18, 18, 18, 18)
        telemetry_layout.setSpacing(12)

        card_title = QLabel("PHYSICAL RAM UTILIZATION")
        card_title.setObjectName("CardTitle")
        telemetry_layout.addWidget(card_title)

        stats_row = QHBoxLayout()
        self.lbl_used_ram = QLabel("Used: --")
        self.lbl_used_ram.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")
        self.lbl_avail_ram = QLabel("Available: --")
        self.lbl_avail_ram.setStyleSheet("font-size: 15px; font-weight: 600; color: #10b981;")
        self.lbl_cached_ram = QLabel("Cache / Standby: --")
        self.lbl_cached_ram.setStyleSheet("font-size: 15px; font-weight: 600; color: #38bdf8;")
        self.lbl_total_ram = QLabel("Total: --")
        self.lbl_total_ram.setStyleSheet("font-size: 15px; color: #64748b;")

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
        self.memory_progress.setFixedHeight(14)
        telemetry_layout.addWidget(self.memory_progress)

        layout.addWidget(self.telemetry_card)

        # 3. Operations Selection Card
        ops_card = QFrame()
        ops_card.setObjectName("Card")
        ops_layout = QVBoxLayout(ops_card)
        ops_layout.setContentsMargins(18, 18, 18, 18)
        ops_layout.setSpacing(10)

        ops_title = QLabel("OPTIMIZATION TARGETS")
        ops_title.setObjectName("CardTitle")
        ops_layout.addWidget(ops_title)

        # Target 1: Process Working Sets
        card_ws = QFrame()
        card_ws.setObjectName("OptionCard")
        layout_ws = QVBoxLayout(card_ws)
        layout_ws.setContentsMargins(12, 10, 12, 10)
        row_ws = QHBoxLayout()
        self.cb_working_sets = QCheckBox("Process Working Sets")
        self.cb_working_sets.setChecked(True)
        self.cb_working_sets.setStyleSheet("font-weight: 700; font-size: 13px;")
        pill_ws = QLabel("🛡️ Standard User")
        pill_ws.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #38bdf8; "
            "background: rgba(56, 189, 248, 0.12); padding: 3px 8px; border-radius: 6px;"
        )
        row_ws.addWidget(self.cb_working_sets)
        row_ws.addStretch()
        row_ws.addWidget(pill_ws)
        layout_ws.addLayout(row_ws)
        lbl_ws_desc = QLabel(
            "Trims unreferenced working set pages of running processes back to the memory manager."
        )
        lbl_ws_desc.setStyleSheet("color: #64748b; font-size: 12px; margin-left: 26px;")
        layout_ws.addWidget(lbl_ws_desc)
        ops_layout.addWidget(card_ws)

        # Target 2: System File Cache
        card_sc = QFrame()
        card_sc.setObjectName("OptionCard")
        layout_sc = QVBoxLayout(card_sc)
        layout_sc.setContentsMargins(12, 10, 12, 10)
        row_sc = QHBoxLayout()
        self.cb_system_cache = QCheckBox("System File Cache")
        self.cb_system_cache.setChecked(self._is_elevated)
        self.cb_system_cache.setStyleSheet("font-weight: 700; font-size: 13px;")
        pill_sc = QLabel("⚡ Admin Required")
        pill_sc.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #f59e0b; "
            "background: rgba(245, 158, 11, 0.12); padding: 3px 8px; border-radius: 6px;"
        )
        row_sc.addWidget(self.cb_system_cache)
        row_sc.addStretch()
        row_sc.addWidget(pill_sc)
        layout_sc.addLayout(row_sc)
        lbl_sc_desc = QLabel(
            "Flushes the system working set and file system cache using SetSystemFileCacheSize."
        )
        lbl_sc_desc.setStyleSheet("color: #64748b; font-size: 12px; margin-left: 26px;")
        layout_sc.addWidget(lbl_sc_desc)
        ops_layout.addWidget(card_sc)

        # Target 3: Standby Page List
        card_sb = QFrame()
        card_sb.setObjectName("OptionCard")
        layout_sb = QVBoxLayout(card_sb)
        layout_sb.setContentsMargins(12, 10, 12, 10)
        row_sb = QHBoxLayout()
        self.cb_standby_list = QCheckBox("Standby Page List")
        self.cb_standby_list.setChecked(self._is_elevated)
        self.cb_standby_list.setStyleSheet("font-weight: 700; font-size: 13px;")
        pill_sb = QLabel("⚡ Admin Required")
        pill_sb.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #f59e0b; "
            "background: rgba(245, 158, 11, 0.12); padding: 3px 8px; border-radius: 6px;"
        )
        row_sb.addWidget(self.cb_standby_list)
        row_sb.addStretch()
        row_sb.addWidget(pill_sb)
        layout_sb.addLayout(row_sb)
        lbl_sb_desc = QLabel(
            "Purges cached standby pages into free memory. Note: Standby cache is already "
            "available when needed; purging may increase disk I/O on immediate file re-reads."
        )
        lbl_sb_desc.setStyleSheet("color: #64748b; font-size: 12px; margin-left: 26px;")
        layout_sb.addWidget(lbl_sb_desc)
        ops_layout.addWidget(card_sb)

        # Target 4: Modified Page List
        card_mod = QFrame()
        card_mod.setObjectName("OptionCard")
        layout_mod = QVBoxLayout(card_mod)
        layout_mod.setContentsMargins(12, 10, 12, 10)
        row_mod = QHBoxLayout()
        self.cb_modified_list = QCheckBox("Modified Page List")
        self.cb_modified_list.setChecked(False)
        self.cb_modified_list.setStyleSheet("font-weight: 700; font-size: 13px;")
        pill_mod = QLabel("⚡ Admin Required")
        pill_mod.setStyleSheet(
            "font-size: 10px; font-weight: 700; color: #f59e0b; "
            "background: rgba(245, 158, 11, 0.12); padding: 3px 8px; border-radius: 6px;"
        )
        row_mod.addWidget(self.cb_modified_list)
        row_mod.addStretch()
        row_mod.addWidget(pill_mod)
        layout_mod.addLayout(row_mod)
        lbl_mod_desc = QLabel(
            "Flushes modified dirty pages to disk backing store or pagefile."
        )
        lbl_mod_desc.setStyleSheet("color: #64748b; font-size: 12px; margin-left: 26px;")
        layout_mod.addWidget(lbl_mod_desc)
        ops_layout.addWidget(card_mod)

        layout.addWidget(ops_card)

        # 4. Action bar
        action_layout = QHBoxLayout()
        self.btn_clean = QPushButton("⚡  Clean Selected Targets")
        self.btn_clean.setObjectName("PrimaryButton")
        self.btn_clean.setFixedHeight(38)
        self.btn_clean.clicked.connect(self._on_clean_clicked)

        self.status_label = QLabel("Select targets above and click Clean Selected Targets")
        self.status_label.setStyleSheet("color: #71717a; font-size: 13px;")

        action_layout.addWidget(self.btn_clean)
        action_layout.addWidget(self.status_label)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        # 5. Results Card (initially hidden)
        self.result_card = QFrame()
        self.result_card.setObjectName("HeroCard")
        self.result_card.setStyleSheet(
            "QFrame#HeroCard { border: 1px solid #059669; "
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #064e3b, stop:1 #065f46); }"
        )
        self.result_card.setVisible(False)
        result_layout = QVBoxLayout(self.result_card)

        res_title = QLabel("OPTIMIZATION REPORT")
        res_title.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #a7f3d0; letter-spacing: 0.6px;"
        )
        result_layout.addWidget(res_title)

        res_metrics_row = QHBoxLayout()
        self.res_reclaimed_label = QLabel("Reclaimed: --")
        self.res_reclaimed_label.setStyleSheet(
            "font-size: 17px; font-weight: 800; color: #ffffff;"
        )
        self.res_before_after = QLabel("Before: -- | After: --")
        self.res_before_after.setStyleSheet("font-size: 13px; color: #d1fae5; font-weight: 500;")
        self.res_processes = QLabel("Processes Trimmed: --")
        self.res_processes.setStyleSheet("font-size: 13px; color: #d1fae5; font-weight: 500;")

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
