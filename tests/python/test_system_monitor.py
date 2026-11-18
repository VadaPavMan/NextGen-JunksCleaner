"""Integration tests for native system snapshot and SystemMonitorService."""

import time

from junkscleaner.native.ffi import NativeCore
from junkscleaner.native.types import JcSnapshotValidityFlags, JcSystemSnapshot
from junkscleaner.services.monitor import SystemMonitorService


def test_native_get_system_snapshot(native_core: NativeCore) -> None:
    """Verify that native_core.get_system_snapshot() captures real metrics."""
    snap = native_core.get_system_snapshot()

    assert snap.timestamp_ms > 0
    assert snap.validity_flags != JcSnapshotValidityFlags.NONE

    # CPU assertions
    assert snap.is_valid(JcSnapshotValidityFlags.CPU_CORES)
    assert snap.logical_cpu_cores >= 1
    if snap.is_valid(JcSnapshotValidityFlags.CPU_USAGE):
        assert 0.0 <= snap.cpu_usage_percent <= 100.0
        assert "%" in snap.cpu_usage_display

    # RAM assertions
    assert snap.is_valid(JcSnapshotValidityFlags.MEM_TOTAL)
    assert snap.is_valid(JcSnapshotValidityFlags.MEM_USED)
    assert snap.is_valid(JcSnapshotValidityFlags.MEM_AVAILABLE)
    assert snap.memory_total_bytes > 0
    assert snap.memory_used_bytes > 0
    assert snap.memory_available_bytes > 0
    assert snap.memory_used_percent is not None
    assert 0.0 <= snap.memory_used_percent <= 100.0
    assert "B" in snap.memory_total_display
    assert "B" in snap.memory_used_display

    # Disk assertions
    assert snap.is_valid(JcSnapshotValidityFlags.PRIMARY_DISK)
    assert len(snap.disks) >= 1
    primary_disk = snap.disks[0]
    assert len(primary_disk.mount_point) > 0
    assert primary_disk.total_bytes > 0
    assert primary_disk.free_bytes <= primary_disk.total_bytes
    assert 0.0 <= primary_disk.used_percent <= 100.0
    assert "B" in primary_disk.total_display


def test_snapshot_unavailable_fallback() -> None:
    """Verify that unavailable metrics correctly report 'N/A' without crashing."""
    mock_snap = JcSystemSnapshot(
        timestamp_ms=12345678,
        validity_flags=JcSnapshotValidityFlags.NONE,
        cpu_usage_percent=0.0,
        logical_cpu_cores=0,
        physical_cpu_cores=0,
        memory_total_bytes=0,
        memory_used_bytes=0,
        memory_available_bytes=0,
        memory_cached_bytes=0,
        memory_committed_bytes=0,
        memory_commit_limit_bytes=0,
        swap_total_bytes=0,
        swap_used_bytes=0,
        process_count=0,
        thread_count=0,
        disks=[],
    )

    assert not mock_snap.is_valid(JcSnapshotValidityFlags.CPU_USAGE)
    assert mock_snap.cpu_usage_display == "N/A"
    assert mock_snap.memory_used_percent is None
    assert mock_snap.memory_used_display == "N/A"
    assert mock_snap.memory_total_display == "N/A"
    assert mock_snap.memory_available_display == "N/A"
    assert mock_snap.memory_cached_display == "N/A"


def test_system_monitor_service_sample_now(native_core: NativeCore) -> None:
    """Verify synchronous sampling and subscriber dispatching in SystemMonitorService."""
    service = SystemMonitorService(native_core=native_core, interval_seconds=1.0)
    received_snapshots: list[JcSystemSnapshot] = []

    def on_snapshot(s: JcSystemSnapshot) -> None:
        received_snapshots.append(s)

    service.subscribe(on_snapshot)
    sample = service.sample_now()

    assert len(received_snapshots) == 1
    assert received_snapshots[0] is sample
    assert service.get_latest_snapshot() is sample
    assert len(service.get_history()) == 1

    service.unsubscribe(on_snapshot)
    service.sample_now()
    assert len(received_snapshots) == 1  # Unsubscribed, count unchanged


def test_system_monitor_bounded_history(native_core: NativeCore) -> None:
    """Verify that the history buffer does not exceed max_history_size."""
    service = SystemMonitorService(native_core=native_core, max_history_size=10)

    for _ in range(15):
        service.sample_now()

    history = service.get_history()
    assert len(history) == 10
    service.clear_history()
    assert len(service.get_history()) == 0


def test_system_monitor_background_thread_lifecycle(native_core: NativeCore) -> None:
    """Verify start, pause, resume, and stop semantics of the background polling thread."""
    service = SystemMonitorService(native_core=native_core, interval_seconds=0.2)

    assert not service.is_running
    service.start()
    assert service.is_running
    assert not service.is_paused

    # Wait for at least 2 samples to be captured in background
    time.sleep(0.55)
    history_count = len(service.get_history())
    assert history_count >= 2

    # Pause and ensure no new samples are added
    service.pause()
    assert service.is_paused
    time.sleep(0.35)
    paused_count = len(service.get_history())
    assert paused_count == history_count

    # Resume and verify polling continues
    service.resume()
    assert not service.is_paused
    time.sleep(0.45)
    assert len(service.get_history()) > paused_count

    # Stop service
    service.stop()
    assert not service.is_running
