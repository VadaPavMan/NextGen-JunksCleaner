"""Memory cleaner orchestration service managing execution, elevation detection, and auditing."""

import ctypes
import logging
import os
import platform
import threading
from dataclasses import dataclass
from datetime import UTC, datetime

from junkscleaner.native.ffi import NativeCore, get_native_core
from junkscleaner.native.types import JcMemoryCleanResult, JcMemoryOperationFlags

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MemoryCleanAuditEntry:
    """Historical audit entry for a memory optimization operation."""

    timestamp_iso: str
    result: JcMemoryCleanResult
    status: str


class MemoryCleanerService:
    """Application service orchestrating memory optimization and cache reclamation."""

    def __init__(self, native_core: NativeCore | None = None) -> None:
        self._native_core = native_core or get_native_core()
        self._lock = threading.Lock()
        self._audit_history: list[MemoryCleanAuditEntry] = []

    def is_elevated(self) -> bool:
        """Check whether the current application process has administrative or root privileges."""
        try:
            if platform.system() == "Windows":
                return bool(ctypes.windll.shell32.IsUserAnAdmin())
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    def clean(self, operations: JcMemoryOperationFlags | int) -> JcMemoryCleanResult:
        """Execute the requested memory operations through native core with audit logging."""
        flags = JcMemoryOperationFlags(operations)
        logger.info(f"Executing memory optimization with operations mask: {flags.name}")

        result = self._native_core.execute_memory_clean(flags)

        status_label = "Success"
        if result.operations_failed:
            if result.operations_succeeded:
                status_label = "Partial Success"
            else:
                status_label = "Failed"

        entry = MemoryCleanAuditEntry(
            timestamp_iso=datetime.now(UTC).isoformat(),
            result=result,
            status=status_label,
        )

        with self._lock:
            self._audit_history.append(entry)

        return result

    def get_audit_history(self) -> list[MemoryCleanAuditEntry]:
        """Return audit history records of all executed memory optimizations."""
        with self._lock:
            return list(self._audit_history)
