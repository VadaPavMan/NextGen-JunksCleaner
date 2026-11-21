"""Tests for GUI foundation, configuration persistence, and navigation."""

import os
from pathlib import Path

from junkscleaner.core.config import ConfigManager
from junkscleaner.native.ffi import NativeCore
from junkscleaner.native.types import (
    JcCleanupItem,
    JcDiskInfo,
    JcRiskLevel,
    JcScanResult,
    JcSnapshotValidityFlags,
    JcSystemSnapshot,
)
from junkscleaner.resources.theme import get_stylesheet
from junkscleaner.services.cleaner import JunkCleanerService
from junkscleaner.services.monitor import SystemMonitorService
from junkscleaner.views.cleaner_page import CleanerPage
from junkscleaner.views.dashboard_page import DashboardPage
from junkscleaner.views.main_window import MainWindow
from PySide6.QtWidgets import QApplication

# Ensure offscreen rendering for headless/test environments
os.environ["QT_QPA_PLATFORM"] = "offscreen"


def test_config_persistence(safe_temp_workspace: Path) -> None:
    """Verify loading, updating, saving, and corrupt recovery of AppConfig."""
    cfg_file = safe_temp_workspace / "test_config.json"
    mgr = ConfigManager(config_path=cfg_file)

    # Defaults
    assert mgr.config.theme == "dark"
    assert mgr.config.monitoring_interval_seconds == 2.0
    assert mgr.config.confirm_before_clean is True

    # Mutate and save
    mgr.config.theme = "light"
    mgr.config.monitoring_interval_seconds = 3.5
    assert mgr.save() is True
    assert cfg_file.exists()

    # Reload from disk
    mgr2 = ConfigManager(config_path=cfg_file)
    assert mgr2.config.theme == "light"
    assert mgr2.config.monitoring_interval_seconds == 3.5

    # Corrupt file fallback
    cfg_file.write_text("{corrupt_json: true,")
    mgr3 = ConfigManager(config_path=cfg_file)
    assert mgr3.config.theme == "dark"  # Defaults returned safely


def test_theme_stylesheets() -> None:
    """Verify theme stylesheets contain required object names."""
    dark_qss = get_stylesheet("dark")
    light_qss = get_stylesheet("light")

    assert "#Sidebar" in dark_qss
    assert "#Card" in dark_qss
    assert "#PrimaryButton" in dark_qss
    assert "#DangerButton" in dark_qss

    assert "#Sidebar" in light_qss
    assert "#Card" in light_qss
    assert "#PrimaryButton" in light_qss


def test_dashboard_page_telemetry_display(qapp: QApplication) -> None:
    """Verify that DashboardPage correctly displays telemetry snapshot data."""
    page = DashboardPage()

    sample_snap = JcSystemSnapshot(
        timestamp_ms=1700000000,
        validity_flags=(
            JcSnapshotValidityFlags.CPU_USAGE
            | JcSnapshotValidityFlags.CPU_CORES
            | JcSnapshotValidityFlags.MEM_TOTAL
            | JcSnapshotValidityFlags.MEM_USED
            | JcSnapshotValidityFlags.MEM_AVAILABLE
            | JcSnapshotValidityFlags.PRIMARY_DISK
        ),
        cpu_usage_percent=42.5,
        logical_cpu_cores=8,
        physical_cpu_cores=4,
        memory_total_bytes=16 * 1024 * 1024 * 1024,
        memory_used_bytes=8 * 1024 * 1024 * 1024,
        memory_available_bytes=8 * 1024 * 1024 * 1024,
        memory_cached_bytes=2 * 1024 * 1024 * 1024,
        memory_committed_bytes=10 * 1024 * 1024 * 1024,
        memory_commit_limit_bytes=20 * 1024 * 1024 * 1024,
        swap_total_bytes=4 * 1024 * 1024 * 1024,
        swap_used_bytes=1 * 1024 * 1024 * 1024,
        process_count=150,
        thread_count=1200,
        disks=[
            JcDiskInfo(
                mount_point="C:\\",
                total_bytes=500 * 1024 * 1024 * 1024,
                free_bytes=250 * 1024 * 1024 * 1024,
                available_bytes=250 * 1024 * 1024 * 1024,
            )
        ],
    )

    page.update_snapshot(sample_snap)
    assert page.cpu_card.value_label.text() == "42.5%"
    assert "8 Logical Cores" in page.cpu_card.subtext_label.text()
    assert page.memory_card.value_label.text() == "50.0%"
    assert page.disk_card.value_label.text() == "50.0%"


def test_cleaner_page_selection_and_preview(qapp: QApplication, native_core: NativeCore) -> None:
    """Verify table population and selection toggling in CleanerPage."""
    service = JunkCleanerService(native_core=native_core)
    page = CleanerPage(service=service)

    fake_items = [
        JcCleanupItem(
            target_id="user_temp",
            relative_path="file1.tmp",
            display_path="file1.tmp",
            size_bytes=1024,
            last_modified_ms=1000,
            risk_level=JcRiskLevel.LOW,
            is_locked=False,
        ),
        JcCleanupItem(
            target_id="user_temp",
            relative_path="file2.tmp",
            display_path="file2.tmp",
            size_bytes=2048,
            last_modified_ms=2000,
            risk_level=JcRiskLevel.LOW,
            is_locked=False,
        ),
    ]
    scan_res = JcScanResult(
        total_candidates_count=2,
        total_estimated_bytes=3072,
        items=fake_items,
    )

    page._on_scan_finished(scan_res)
    assert page.table.rowCount() == 2
    assert "2 items selected" in page.summary_label.text()

    # Deselect all
    page._deselect_all()
    assert "0 items selected" in page.summary_label.text()

    # Select all
    page._select_all()
    assert "2 items selected" in page.summary_label.text()


def test_main_window_navigation(
    qapp: QApplication, native_core: NativeCore, safe_temp_workspace: Path
) -> None:
    """Verify MainWindow sidebar switching and shutdown."""
    cfg_file = safe_temp_workspace / "ui_test_config.json"
    config_mgr = ConfigManager(config_path=cfg_file)
    monitor_service = SystemMonitorService(native_core=native_core, interval_seconds=1.0)
    cleaner_service = JunkCleanerService(native_core=native_core)

    window = MainWindow(
        native_core=native_core,
        config_mgr=config_mgr,
        monitor_service=monitor_service,
        cleaner_service=cleaner_service,
    )

    try:
        assert window.stack.count() == 5
        assert window.stack.currentIndex() == 0  # Dashboard

        # Navigate to Cleaner
        window.btn_cleaner.click()
        assert window.stack.currentIndex() == 1

        # Navigate to Clean Memory
        window.btn_memory.click()
        assert window.stack.currentIndex() == 2

        # Navigate to Activity
        window.btn_activity.click()
        assert window.stack.currentIndex() == 3

        # Navigate to Settings
        window.btn_settings.click()
        assert window.stack.currentIndex() == 4

        # Navigate back to Dashboard
        window.btn_dashboard.click()
        assert window.stack.currentIndex() == 0

    finally:
        window.close()
