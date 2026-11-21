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
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # ── Header ───────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(4)

        title = QLabel("Clean Memory")
        title.setObjectName("PageTitle")
        header_text.addWidget(title)

        subtitle = QLabel("RAM optimization and cache reclamation")
        subtitle.setObjectName("PageSubtitle")
        header_text.addWidget(subtitle)

        header_row.addLayout(header_text)
        header_row.addStretch()

        # Privilege badge
        if self._is_elevated:
            elev_label = QLabel("Administrator")
            elev_label.setObjectName("BadgeGreen")
        else:
            elev_label = QLabel("Standard User")
            elev_label.setObjectName("BadgeMuted")
        header_row.addWidget(elev_label)
        layout.addLayout(header_row)

        # ── Live RAM telemetry ───────────────────────────────────────
        self.telemetry_card = QFrame()
        self.telemetry_card.setObjectName("Card")
        self.telemetry_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tl = QVBoxLayout(self.telemetry_card)
        tl.setContentsMargins(16, 14, 16, 14)
        tl.setSpacing(10)

        tl_title = QLabel("PHYSICAL RAM")
        tl_title.setObjectName("CardTitle")
        tl.addWidget(tl_title)

        # Stats row
        stats = QHBoxLayout()
        stats.setSpacing(20)
        self.lbl_used_ram = QLabel("Used: --")
        self.lbl_used_ram.setStyleSheet("font-weight: 600;")
        self.lbl_avail_ram = QLabel("Available: --")
        self.lbl_avail_ram.setStyleSheet("font-weight: 500;")
        self.lbl_cached_ram = QLabel("Cached: --")
        self.lbl_cached_ram.setStyleSheet("font-weight: 500;")
        self.lbl_total_ram = QLabel("Total: --")
        self.lbl_total_ram.setObjectName("MetricSubtext")

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
        self.memory_progress.setFixedHeight(14)
        tl.addWidget(self.memory_progress)

        layout.addWidget(self.telemetry_card)

        # ── Optimization targets ─────────────────────────────────────
        targets_card = QFrame()
        targets_card.setObjectName("Card")
        targets_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tc = QVBoxLayout(targets_card)
        tc.setContentsMargins(16, 14, 16, 14)
        tc.setSpacing(8)

        tc_title = QLabel("OPTIMIZATION TARGETS")
        tc_title.setObjectName("CardTitle")
        tc.addWidget(tc_title)

        # -- Target: Working Sets
        self.cb_working_sets = QCheckBox("Process Working Sets")
        self.cb_working_sets.setChecked(True)
        tc.addWidget(self._make_target_row(
            self.cb_working_sets,
            "Trims unreferenced pages back to the memory manager.",
            "Standard",
        ))

        # -- Target: System File Cache
        self.cb_system_cache = QCheckBox("System File Cache")
        self.cb_system_cache.setChecked(self._is_elevated)
        tc.addWidget(self._make_target_row(
            self.cb_system_cache,
            "Flushes system working set and file cache via SetSystemFileCacheSize.",
            "Admin",
        ))

        # -- Target: Standby Page List
        self.cb_standby_list = QCheckBox("Standby Page List")
        self.cb_standby_list.setChecked(self._is_elevated)
        tc.addWidget(self._make_target_row(
            self.cb_standby_list,
            "Purges standby pages into free memory. May increase disk I/O.",
            "Admin",
        ))

        # -- Target: Modified Page List
        self.cb_modified_list = QCheckBox("Modified Page List")
        self.cb_modified_list.setChecked(False)
        tc.addWidget(self._make_target_row(
            self.cb_modified_list,
            "Flushes dirty pages to disk backing store.",
            "Admin",
        ))

        layout.addWidget(targets_card)

        # ── Action row ───────────────────────────────────────────────
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_clean = QPushButton("Clean Selected Targets")
        self.btn_clean.setObjectName("PrimaryButton")
        self.btn_clean.setFixedHeight(36)
        self.btn_clean.clicked.connect(self._on_clean_clicked)
        action_row.addWidget(self.btn_clean)

        self.status_label = QLabel("Select targets and click Clean")
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
        rl.setSpacing(4)

        res_title = QLabel("OPTIMIZATION REPORT")
        res_title.setObjectName("CardTitle")
        res_title.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #27ae60; "
            "text-transform: uppercase; letter-spacing: 0.8px;"
        )
        rl.addWidget(res_title)

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(16)
        self.res_reclaimed_label = QLabel("Reclaimed: --")
        self.res_reclaimed_label.setStyleSheet("font-size: 16px; font-weight: 700;")
        self.res_before_after = QLabel("Before: -- | After: --")
        self.res_before_after.setObjectName("MetricSubtext")
        self.res_processes = QLabel("Trimmed: --")
        self.res_processes.setObjectName("MetricSubtext")

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
        card.setMinimumHeight(64)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(12, 8, 12, 8)
        outer.setSpacing(4)

        top_row = QHBoxLayout()
        checkbox.setStyleSheet("font-weight: 600;")
        top_row.addWidget(checkbox)
        top_row.addStretch()

        if level == "Admin":
            badge = QLabel("Admin Required")
            badge.setObjectName("BadgeAmber")
        else:
            badge = QLabel("Standard User")
            badge.setObjectName("BadgeBlue")
        top_row.addWidget(badge)
        outer.addLayout(top_row)

        desc_label = QLabel(description)
        desc_label.setObjectName("MetricSubtext")
        desc_label.setStyleSheet("margin-left: 24px;")
        desc_label.setWordWrap(True)
        outer.addWidget(desc_label)

        return card

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

        needs_admin = (
            (mask & JcMemoryOperationFlags.SYSTEM_CACHE)
            or (mask & JcMemoryOperationFlags.STANDBY_LIST)
            or (mask & JcMemoryOperationFlags.MODIFIED_LIST)
        )
        if needs_admin and not self._is_elevated:
            ret = QMessageBox.question(
                self,
                "Administrator Rights Recommended",
                "Some selected operations require Administrator privileges "
                "(System Cache, Standby List, Modified List).\n\n"
                "In standard mode these may be skipped or denied.\n\n"
                "Proceed anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if ret != QMessageBox.Yes:
                return

        self.btn_clean.setEnabled(False)
        self.status_label.setText("Optimizing\u2026")

        self._worker = MemoryCleanWorker(service=self.service, operations=mask, parent=self)
        self._worker.clean_finished.connect(self._on_clean_finished)
        self._worker.clean_failed.connect(self._on_clean_failed)
        self._worker.start()

    @Slot(object)
    def _on_clean_finished(self, result: JcMemoryCleanResult) -> None:
        self.btn_clean.setEnabled(True)
        self.status_label.setText(f"Done \u2014 reclaimed {result.bytes_reclaimed_display}")

        self.result_card.setVisible(True)
        self.res_reclaimed_label.setText(f"Reclaimed: {result.bytes_reclaimed_display}")
        self.res_before_after.setText(
            f"Before: {result.before_used_display}  |  After: {result.after_used_display}"
        )
        self.res_processes.setText(
            f"Trimmed: {result.processes_trimmed}  (Skipped: {result.processes_failed})"
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
