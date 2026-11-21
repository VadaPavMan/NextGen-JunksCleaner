"""Tests for MemoryCleanerService, FFI execution, and MemoryPage UI."""

import os
from unittest.mock import MagicMock

from junkscleaner.native.ffi import NativeCore
from junkscleaner.native.types import (
    JcMemoryCleanResult,
    JcMemoryOperationFlags,
    JcSnapshotValidityFlags,
    JcSystemSnapshot,
)
from junkscleaner.services.memory import MemoryCleanerService
from junkscleaner.views.memory_page import MemoryPage
from PySide6.QtWidgets import QApplication

os.environ["QT_QPA_PLATFORM"] = "offscreen"


def test_memory_cleaner_service_elevation(native_core: NativeCore) -> None:
    """Verify that elevation check returns a boolean without throwing."""
    service = MemoryCleanerService(native_core=native_core)
    is_elev = service.is_elevated()
    assert isinstance(is_elev, bool)


def test_memory_cleaner_service_execution(native_core: NativeCore) -> None:
    """Verify end-to-end memory cleaning with appropriate platform target."""
    import platform

    service = MemoryCleanerService(native_core=native_core)
    assert len(service.get_audit_history()) == 0

    op = (
        JcMemoryOperationFlags.WORKING_SETS
        if platform.system() == "Windows"
        else JcMemoryOperationFlags.MODIFIED_LIST
    )
    result = service.clean(op)

    assert isinstance(result, JcMemoryCleanResult)
    assert (result.operations_attempted & op) != 0
    assert result.before_used_bytes > 0
    assert result.after_used_bytes > 0
    assert result.bytes_reclaimed >= 0
    assert isinstance(result.bytes_reclaimed_display, str)

    # Verify audit entry
    history = service.get_audit_history()
    assert len(history) == 1
    assert history[0].result == result
    assert history[0].status in ("Success", "Partial Success", "Failed")


def test_memory_cleaner_mock_service() -> None:
    """Verify service behavior when native core returns partial success."""
    mock_core = MagicMock()
    ops = (
        JcMemoryOperationFlags.WORKING_SETS
        | JcMemoryOperationFlags.STANDBY_LIST
    )
    mock_core.execute_memory_clean.return_value = JcMemoryCleanResult(
        before_used_bytes=8000000000,
        after_used_bytes=7500000000,
        bytes_reclaimed=500000000,
        operations_attempted=ops,
        operations_succeeded=JcMemoryOperationFlags.WORKING_SETS,
        operations_failed=JcMemoryOperationFlags.STANDBY_LIST,
        processes_trimmed=15,
        processes_failed=2,
    )

    service = MemoryCleanerService(native_core=mock_core)
    result = service.clean(
        JcMemoryOperationFlags.WORKING_SETS | JcMemoryOperationFlags.STANDBY_LIST
    )

    assert result.bytes_reclaimed == 500000000
    assert result.operations_succeeded == JcMemoryOperationFlags.WORKING_SETS
    assert result.operations_failed == JcMemoryOperationFlags.STANDBY_LIST

    history = service.get_audit_history()
    assert len(history) == 1
    assert history[0].status == "Partial Success"


def test_memory_page_ui(qapp: QApplication, native_core: NativeCore) -> None:
    """Verify MemoryPage controls, mask calculation, and telemetry updates."""
    service = MemoryCleanerService(native_core=native_core)
    page = MemoryPage(service=service)

    try:
        # Default states
        assert page.cb_working_sets.isChecked() is True
        assert page.btn_clean.isEnabled() is True
        assert page.result_card.isHidden() is True

        # Selected mask
        mask = page._get_selected_mask()
        assert (mask & JcMemoryOperationFlags.WORKING_SETS) != 0

        # Snapshot update
        snap = JcSystemSnapshot(
            timestamp_ms=1000,
            validity_flags=int(
                JcSnapshotValidityFlags.MEM_TOTAL
                | JcSnapshotValidityFlags.MEM_USED
                | JcSnapshotValidityFlags.MEM_AVAILABLE
                | JcSnapshotValidityFlags.MEM_CACHED
            ),
            cpu_usage_percent=12.5,
            logical_cpu_cores=8,
            physical_cpu_cores=4,
            memory_total_bytes=16 * 1024 * 1024 * 1024,
            memory_used_bytes=8 * 1024 * 1024 * 1024,
            memory_available_bytes=8 * 1024 * 1024 * 1024,
            memory_cached_bytes=4 * 1024 * 1024 * 1024,
            memory_committed_bytes=0,
            memory_commit_limit_bytes=0,
            swap_total_bytes=0,
            swap_used_bytes=0,
            process_count=100,
            thread_count=1000,
            disks=[],
        )

        page.update_snapshot(snap)
        assert page.memory_progress.value() == 50
        assert "Used:" in page.lbl_used_ram.text()
        assert "Available:" in page.lbl_avail_ram.text()
        assert "Cached:" in page.lbl_cached_ram.text()

        # Finished result handler
        fake_res = JcMemoryCleanResult(
            before_used_bytes=8 * 1024 * 1024 * 1024,
            after_used_bytes=7 * 1024 * 1024 * 1024,
            bytes_reclaimed=1024 * 1024 * 1024,
            operations_attempted=JcMemoryOperationFlags.WORKING_SETS,
            operations_succeeded=JcMemoryOperationFlags.WORKING_SETS,
            operations_failed=JcMemoryOperationFlags.NONE,
            processes_trimmed=10,
            processes_failed=0,
        )
        page._on_clean_finished(fake_res)
        assert page.result_card.isHidden() is False
        assert "1.00 GiB" in page.res_reclaimed_label.text()
        assert "Trimmed: 10" in page.res_processes.text()

    finally:
        page.close()
