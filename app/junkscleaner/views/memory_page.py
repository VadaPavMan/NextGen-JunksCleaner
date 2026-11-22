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
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class MemoryPage(QWidget):
    """Interactive Clean Memory page for RAM optimization inspired by WinMemoryCleaner."""

    memory_cleaned = Signal(object)  # Emits JcMemoryCleanResult

    def __init__(self, service: MemoryCleanerService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.service = service
        self._worker: MemoryCleanWorker | None = None
        self._is_elevated = self.service.is_elevated()

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # ── Header ───────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(4)

        title = QLabel("Clean Memory")
        title.setObjectName("PageTitle")
        header_text.addWidget(title)

        subtitle = QLabel("Safe RAM optimization & cache reclamation via native NT engine")
        subtitle.setObjectName("PageSubtitle")
        header_text.addWidget(subtitle)

        header_row.addLayout(header_text)
        header_row.addStretch()

        # Privilege badge
        if self._is_elevated:
            elev_label = QLabel("Administrator Mode")
            elev_label.setObjectName("BadgeGreen")
        else:
            elev_label = QLabel("Standard User Mode")
            elev_label.setObjectName("BadgeAmber")
        header_row.addWidget(elev_label)
        layout.addLayout(header_row)

        # Non-elevated tip banner
        if not self._is_elevated:
            tip_frame = QFrame()
            tip_frame.setObjectName("OptionCard")
            tip_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            tl_tip = QHBoxLayout(tip_frame)
            tl_tip.setContentsMargins(14, 10, 14, 10)
            tip_icon = QLabel("\u2139")
            tip_icon.setStyleSheet("font-size: 16px; font-weight: 700; color: #f39c12;")
            tip_label = QLabel(
                "Tip: To reclaim maximum memory (purging cached standby pages & file cache), "
                "run JunksCleaner as Administrator."
            )
            tip_label.setStyleSheet("font-size: 12px; color: #a09d98;")
            tip_label.setWordWrap(True)
            tl_tip.addWidget(tip_icon)
            tl_tip.addWidget(tip_label, 1)
            layout.addWidget(tip_frame)

        # ── Live RAM telemetry ───────────────────────────────────────
        self.telemetry_card = QFrame()
        self.telemetry_card.setObjectName("Card")
        self.telemetry_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tl = QVBoxLayout(self.telemetry_card)
        tl.setContentsMargins(16, 14, 16, 14)
        tl.setSpacing(10)

        tl_title = QLabel("PHYSICAL RAM UTILIZATION")
        tl_title.setObjectName("CardTitle")
        tl.addWidget(tl_title)

        # Stats row
        stats = QHBoxLayout()
        stats.setSpacing(20)
        self.lbl_used_ram = QLabel("Used: --")
        self.lbl_used_ram.setStyleSheet("font-size: 14px; font-weight: 700;")
        self.lbl_avail_ram = QLabel("Available: --")
        self.lbl_avail_ram.setStyleSheet("font-size: 14px; font-weight: 600;")
        self.lbl_cached_ram = QLabel("Cached: --")
        self.lbl_cached_ram.setStyleSheet("font-size: 14px; font-weight: 600; color: #3498db;")
        self.lbl_total_ram = QLabel("Total: --")
        self.lbl_total_ram.setStyleSheet("font-size: 14px; font-weight: 500;")

        stats.addWidget(self.lbl_used_ram)
        stats.addWidget(self.lbl_avail_ram)
        stats.addWidget(self.lbl_cached_ram)
        stats.addWidget(self.lbl_total_ram)
        stats.addStretch()
        tl.addLayout(stats)

        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setValue(0)
        self.memory_progress.setTextVisible(True)
        self.memory_progress.setFixedHeight(18)
        tl.addWidget(self.memory_progress)

        layout.addWidget(self.telemetry_card)

        # ── Optimization targets ─────────────────────────────────────
        targets_card = QFrame()
        targets_card.setObjectName("Card")
        targets_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tc = QVBoxLayout(targets_card)
        tc.setContentsMargins(16, 14, 16, 14)
        tc.setSpacing(8)

        # Targets card header with selection actions
        th_row = QHBoxLayout()
        tc_title = QLabel("OPTIMIZATION TARGETS")
        tc_title.setObjectName("CardTitle")
        th_row.addWidget(tc_title)
        th_row.addStretch()

        btn_select_all = QPushButton("Select All")
        btn_select_all.setObjectName("SecondaryButton")
        btn_select_all.setFixedHeight(26)
        btn_select_all.clicked.connect(self._select_all_targets)
        th_row.addWidget(btn_select_all)

        btn_clear_all = QPushButton("Clear All")
        btn_clear_all.setObjectName("SecondaryButton")
        btn_clear_all.setFixedHeight(26)
        btn_clear_all.clicked.connect(self._clear_all_targets)
        th_row.addWidget(btn_clear_all)

        tc.addLayout(th_row)

        # 1. Process Working Sets
        self.cb_working_sets = QCheckBox("Process Working Sets")
        self.cb_working_sets.setChecked(True)
        tc.addWidget(self._make_target_row(
            self.cb_working_sets,
            "Trims unreferenced working set pages across running processes back to memory manager.",
            "Standard",
        ))

        # 2. System File Cache
        self.cb_system_cache = QCheckBox("System File Cache")
        self.cb_system_cache.setChecked(True)
        tc.addWidget(self._make_target_row(
            self.cb_system_cache,
            "Flushes system working set and file system cache via NT kernel and Win32 interfaces.",
            "Admin",
        ))

        # 3. Standby Page List
        self.cb_standby_list = QCheckBox("Standby Page List")
        self.cb_standby_list.setChecked(True)
        tc.addWidget(self._make_target_row(
            self.cb_standby_list,
            "Purges cached standby pages into free RAM (reclaims gigabytes of cached memory).",
            "Admin",
        ))

        # 4. Modified Page List
        self.cb_modified_list = QCheckBox("Modified Page List")
        self.cb_modified_list.setChecked(True)
        tc.addWidget(self._make_target_row(
            self.cb_modified_list,
            "Flushes dirty modified memory pages to the disk backing store / pagefile.",
            "Admin",
        ))

        # 5. Combined Page List
        self.cb_combined_list = QCheckBox("Combined Page List")
        self.cb_combined_list.setChecked(True)
        tc.addWidget(self._make_target_row(
            self.cb_combined_list,
            "Combines and deduplicates identical physical memory pages (Windows 8.1 / 10+).",
            "Admin",
        ))

        # 6. Registry Cache
        self.cb_registry_cache = QCheckBox("Registry Cache")
        self.cb_registry_cache.setChecked(True)
        tc.addWidget(self._make_target_row(
            self.cb_registry_cache,
            "Flushes registry reconciliation buffers and hive working memory.",
            "Admin",
        ))

        # 7. Modified File Cache
        self.cb_modified_file_cache = QCheckBox("Modified File Cache")
        self.cb_modified_file_cache.setChecked(True)
        tc.addWidget(self._make_target_row(
            self.cb_modified_file_cache,
            "Flushes volume write order & file buffers across fixed drives via disk IOCTLs.",
            "Admin",
        ))

        layout.addWidget(targets_card)

        # ── Action row ───────────────────────────────────────────────
        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.btn_clean = QPushButton("Clean Selected Targets")
        self.btn_clean.setObjectName("PrimaryButton")
        self.btn_clean.setFixedHeight(38)
        self.btn_clean.clicked.connect(self._on_clean_clicked)
        action_row.addWidget(self.btn_clean)

        self.status_label = QLabel("Select targets and click Clean Selected Targets")
        self.status_label.setObjectName("StatusLabel")
        action_row.addWidget(self.status_label)
        action_row.addStretch()

        layout.addLayout(action_row)

        # ── Results card (hidden until a clean completes) ────────────
        self.result_card = QFrame()
        self.result_card.setObjectName("HeroCard")
        self.result_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.result_card.setVisible(False)
        rl = QVBoxLayout(self.result_card)
        rl.setContentsMargins(16, 12, 16, 12)
        rl.setSpacing(6)

        res_title = QLabel("OPTIMIZATION REPORT")
        res_title.setObjectName("CardTitle")
        res_title.setStyleSheet(
            "font-size: 12px; font-weight: 700; color: #27ae60; "
            "text-transform: uppercase; letter-spacing: 0.8px;"
        )
        rl.addWidget(res_title)

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(16)
        self.res_reclaimed_label = QLabel("Reclaimed: --")
        self.res_reclaimed_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #2ecc71;")
        self.res_before_after = QLabel("Before: -- | After: --")
        self.res_before_after.setStyleSheet("font-size: 13px; font-weight: 500;")
        self.res_processes = QLabel("Processes Trimmed: --")
        self.res_processes.setStyleSheet("font-size: 13px; font-weight: 500;")

        metrics_row.addWidget(self.res_reclaimed_label)
        metrics_row.addWidget(self.res_before_after)
        metrics_row.addWidget(self.res_processes)
        metrics_row.addStretch()
        rl.addLayout(metrics_row)

        layout.addWidget(self.result_card)
        layout.addStretch()

    @staticmethod
    def _make_target_row(checkbox: QCheckBox, description: str, level: str) -> QFrame:
        """Build a single optimization target row card."""
        card = QFrame()
        card.setObjectName("OptionCard")
        card.setMinimumHeight(60)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(12, 6, 12, 6)
        outer.setSpacing(2)

        top_row = QHBoxLayout()
        checkbox.setStyleSheet("font-weight: 600; font-size: 14px;")
        top_row.addWidget(checkbox)
        top_row.addStretch()

        if level == "Admin":
            badge = QLabel("Admin Recommended")
            badge.setObjectName("BadgeAmber")
        else:
            badge = QLabel("Standard User")
            badge.setObjectName("BadgeBlue")
        top_row.addWidget(badge)
        outer.addLayout(top_row)

        desc_label = QLabel(description)
        desc_label.setObjectName("MetricSubtext")
        desc_label.setStyleSheet("margin-left: 24px; font-size: 12px; color: #a09d98;")
        desc_label.setWordWrap(True)
        outer.addWidget(desc_label)

        return card

    def _select_all_targets(self) -> None:
        """Select all optimization target checkboxes."""
        self.cb_working_sets.setChecked(True)
        self.cb_system_cache.setChecked(True)
        self.cb_standby_list.setChecked(True)
        self.cb_modified_list.setChecked(True)
        self.cb_combined_list.setChecked(True)
        self.cb_registry_cache.setChecked(True)
        self.cb_modified_file_cache.setChecked(True)

    def _clear_all_targets(self) -> None:
        """Deselect all optimization target checkboxes."""
        self.cb_working_sets.setChecked(False)
        self.cb_system_cache.setChecked(False)
        self.cb_standby_list.setChecked(False)
        self.cb_modified_list.setChecked(False)
        self.cb_combined_list.setChecked(False)
        self.cb_registry_cache.setChecked(False)
        self.cb_modified_file_cache.setChecked(False)

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
            self.lbl_cached_ram.setText(f"Cached: {format_bytes(cached)}")

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
        if self.cb_combined_list.isChecked():
            mask |= JcMemoryOperationFlags.COMBINED_LIST
        if self.cb_registry_cache.isChecked():
            mask |= JcMemoryOperationFlags.REGISTRY_CACHE
        if self.cb_modified_file_cache.isChecked():
            mask |= JcMemoryOperationFlags.MODIFIED_FILE_CACHE
        return int(mask)

    @Slot()
    def _on_clean_clicked(self) -> None:
        mask = self._get_selected_mask()
        if mask == 0:
            QMessageBox.warning(
                self,
                "No Targets Selected",
                "Please select at least one optimization target.",
            )
            return

        self.btn_clean.setEnabled(False)
        self.status_label.setText("Optimizing system memory\u2026")

        self._worker = MemoryCleanWorker(service=self.service, operations=mask, parent=self)
        self._worker.clean_finished.connect(self._on_clean_finished)
        self._worker.clean_failed.connect(self._on_clean_failed)
        self._worker.start()

    @Slot(object)
    def _on_clean_finished(self, result: JcMemoryCleanResult) -> None:
        self.btn_clean.setEnabled(True)
        self.status_label.setText(f"Completed \u2014 reclaimed {result.bytes_reclaimed_display}.")

        self.result_card.setVisible(True)
        self.res_reclaimed_label.setText(f"Reclaimed: {result.bytes_reclaimed_display}")
        self.res_before_after.setText(
            f"Before: {result.before_used_display} | After: {result.after_used_display}"
        )
        self.res_processes.setText(
            f"Processes Trimmed: {result.processes_trimmed} (Skipped: {result.processes_failed})"
        )

        self.memory_cleaned.emit(result)

    @Slot(str)
    def _on_clean_failed(self, error_msg: str) -> None:
        self.btn_clean.setEnabled(True)
        self.status_label.setText("Optimization failed")
        QMessageBox.critical(
            self,
            "Memory Optimization Error",
            f"Failed to execute memory cleaning:\n\n{error_msg}",
        )
