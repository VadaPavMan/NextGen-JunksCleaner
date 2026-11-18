"""Junk cleaner orchestration service providing scan, preview, confirmation, and audit tracking."""

import ctypes
import logging
import threading

from junkscleaner.native.ffi import NativeCore, get_native_core
from junkscleaner.native.types import (
    JcCleanupItem,
    JcCleanupReport,
    JcScanResult,
)

logger = logging.getLogger(__name__)


class ConfirmationRequiredError(Exception):
    """Raised when cleanup execution is attempted without explicit user confirmation."""


class JunkCleanerService:
    """Application service orchestrating safe preview-first junk cleanup.

    Pipeline:
    Target discovery -> Preview aggregation -> User confirmation ->
    Revalidation & Deletion -> Audit Report
    """

    def __init__(self, native_core: NativeCore | None = None) -> None:
        self._native_core = native_core or get_native_core()
        self._lock = threading.Lock()
        self._audit_history: list[JcCleanupReport] = []
        self._current_cancel_token: ctypes.c_int32 | None = None

    def scan(
        self,
        custom_root_override: str | None = None,
        min_age_seconds: int = 0,
        max_depth: int = 5,
    ) -> JcScanResult:
        """Scan allow-listed cleanup targets and return candidate items."""
        logger.info("Starting cleanup target scan...")
        return self._native_core.scan_cleanup_targets(
            custom_root_override=custom_root_override,
            min_age_seconds=min_age_seconds,
            max_depth=max_depth,
        )

    def create_preview(
        self,
        scan_result: JcScanResult,
        deselected_relative_paths: set[str] | None = None,
    ) -> list[JcCleanupItem]:
        """Filter scan result candidate items based on user selection in the preview."""
        deselected = deselected_relative_paths or set()
        return [item for item in scan_result.items if item.relative_path not in deselected]

    def cancel(self) -> None:
        """Signal cooperative cancellation to any currently running cleanup operation."""
        with self._lock:
            if self._current_cancel_token is not None:
                self._current_cancel_token.value = 1
                logger.info("Cancellation requested for running cleanup operation.")

    def execute(
        self,
        items: list[JcCleanupItem],
        confirmed: bool,
        custom_root_override: str | None = None,
        is_dry_run: bool = False,
    ) -> JcCleanupReport:
        """Execute cleanup on user-approved candidate items.

        Requires confirmed=True for destructive deletion.
        """
        if not is_dry_run and not confirmed:
            raise ConfirmationRequiredError(
                "Destructive cleanup requires explicit user confirmation."
            )

        cancel_token = ctypes.c_int32(0)
        with self._lock:
            self._current_cancel_token = cancel_token

        try:
            report = self._native_core.execute_cleanup(
                items=items,
                custom_root_override=custom_root_override,
                is_dry_run=is_dry_run,
                cancel_token=cancel_token,
            )
            with self._lock:
                self._audit_history.append(report)
            return report
        finally:
            with self._lock:
                self._current_cancel_token = None

    def get_audit_history(self) -> list[JcCleanupReport]:
        """Return audit history records of all executed cleanup runs."""
        with self._lock:
            return list(self._audit_history)

    def clear_audit_history(self) -> None:
        """Clear audit history records."""
        with self._lock:
            self._audit_history.clear()
