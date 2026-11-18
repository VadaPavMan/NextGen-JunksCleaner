"""Safety and integration tests for JunksCleaner safe cleanup pipeline."""

from pathlib import Path

import pytest
from junkscleaner.native.ffi import NativeCore
from junkscleaner.native.types import JcCleanupItem, JcRiskLevel
from junkscleaner.services.cleaner import ConfirmationRequiredError, JunkCleanerService


def test_safe_cleanup_workflow_end_to_end(
    native_core: NativeCore, safe_temp_workspace: Path
) -> None:
    """Verify complete scan -> preview -> confirmation -> deletion -> audit history pipeline."""
    # 1. Setup isolated test files inside safe_temp_workspace
    sub_dir = safe_temp_workspace / "sub_cache"
    sub_dir.mkdir(parents=True, exist_ok=True)

    file_a = safe_temp_workspace / "cache_1.tmp"
    file_b = sub_dir / "cache_2.log"
    file_db = safe_temp_workspace / "settings.db"  # Excluded by policy

    file_a.write_text("AAAAA")  # 5 bytes
    file_b.write_text("BBBBBBBBBB")  # 10 bytes
    file_db.write_text("SQLITE_DATABASE_HEADER")

    # Setup external canary file outside test root
    canary_dir = safe_temp_workspace.parent / f"canary_ext_{safe_temp_workspace.name}"
    canary_dir.mkdir(parents=True, exist_ok=True)
    canary_file = canary_dir / "critical_user_file.txt"
    canary_file.write_text("CRITICAL_USER_DATA_DO_NOT_DELETE")

    try:
        service = JunkCleanerService(native_core=native_core)

        # 2. Scan
        scan_res = service.scan(custom_root_override=str(safe_temp_workspace))
        assert scan_res.total_candidates_count == 2
        assert scan_res.total_estimated_bytes == 15
        assert len(scan_res.items) == 2

        # 3. Preview & Deselection
        # Deselect file_b in preview
        preview_items = service.create_preview(
            scan_res,
            deselected_relative_paths={"sub_cache/cache_2.log", "sub_cache\\cache_2.log"},
        )
        assert len(preview_items) == 1
        assert preview_items[0].display_path == "cache_1.tmp"

        # 4. Confirmation requirement gate
        with pytest.raises(ConfirmationRequiredError):
            service.execute(
                items=preview_items,
                confirmed=False,
                custom_root_override=str(safe_temp_workspace),
                is_dry_run=False,
            )

        # 5. Dry run
        dry_report = service.execute(
            items=preview_items,
            confirmed=True,
            custom_root_override=str(safe_temp_workspace),
            is_dry_run=True,
        )
        assert dry_report.selected_count == 1
        assert dry_report.deleted_count == 1
        assert dry_report.actual_bytes_deleted == 5
        assert file_a.exists(), "File A must still exist after dry run"

        # 6. Real Confirmed Deletion
        real_report = service.execute(
            items=preview_items,
            confirmed=True,
            custom_root_override=str(safe_temp_workspace),
            is_dry_run=False,
        )
        assert real_report.selected_count == 1
        assert real_report.deleted_count == 1
        assert real_report.actual_bytes_deleted == 5
        assert not file_a.exists(), "File A must be deleted from disk"
        assert file_b.exists(), "Deselected File B must remain on disk"
        assert file_db.exists(), "Excluded database file must remain on disk"
        assert canary_file.exists(), "External canary file must remain untouched"

        # 7. Audit History
        history = service.get_audit_history()
        assert len(history) == 2
        assert history[0] == dry_report
        assert history[1] == real_report

    finally:
        # Cleanup external canary
        if canary_dir.exists():
            import shutil

            shutil.rmtree(canary_dir, ignore_errors=True)


def test_path_traversal_attack_blocked(native_core: NativeCore, safe_temp_workspace: Path) -> None:
    """Verify that candidate items attempting path traversal are rejected and skipped."""
    canary_dir = safe_temp_workspace.parent / f"canary_attack_{safe_temp_workspace.name}"
    canary_dir.mkdir(parents=True, exist_ok=True)
    canary_file = canary_dir / "target_of_attack.txt"
    canary_file.write_text("MUST_NOT_BE_DELETED")

    try:
        service = JunkCleanerService(native_core=native_core)

        # Craft malicious item with path traversal relative_path
        malicious_item = JcCleanupItem(
            target_id="user_temp",
            relative_path=f"../canary_attack_{safe_temp_workspace.name}/target_of_attack.txt",
            display_path="target_of_attack.txt",
            size_bytes=100,
            last_modified_ms=1000,
            risk_level=JcRiskLevel.LOW,
            is_locked=False,
        )

        report = service.execute(
            items=[malicious_item],
            confirmed=True,
            custom_root_override=str(safe_temp_workspace),
            is_dry_run=False,
        )

        assert report.deleted_count == 0
        assert report.skipped_count == 1
        assert canary_file.exists(), "External attack target must remain intact!"

    finally:
        if canary_dir.exists():
            import shutil

            shutil.rmtree(canary_dir, ignore_errors=True)
