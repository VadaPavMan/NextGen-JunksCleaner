"""ctypes FFI wrapper for JunksCleaner native C ABI."""

import ctypes
import os
import platform
import sys
from pathlib import Path

from .types import (
    JC_CURRENT_ABI_VERSION,
    CTypesCapabilities,
    CTypesCleanupItem,
    CTypesCleanupOptions,
    CTypesCleanupReport,
    CTypesScanOptions,
    CTypesScanResult,
    CTypesSystemSnapshot,
    CTypesVersionInfo,
    JcArchitecture,
    JcCapabilities,
    JcCapabilityFlags,
    JcCleanupItem,
    JcCleanupReport,
    JcDiskInfo,
    JcOsFamily,
    JcRiskLevel,
    JcScanResult,
    JcSnapshotValidityFlags,
    JcStatus,
    JcSystemSnapshot,
    JcVersionInfo,
)


class JcNativeError(Exception):
    """Raised when a native operation returns a non-OK status."""

    def __init__(self, status: JcStatus, message: str) -> None:
        super().__init__(f"Native error {status.name} ({status.value}): {message}")
        self.status = status
        self.message = message


class JcAbiMismatchError(JcNativeError):
    """Raised when the loaded native library ABI version does not match the Python client."""


def find_native_library() -> Path:
    """Locate the native shared library on the local filesystem."""
    system = platform.system()
    if system == "Windows":
        names = ["libjunkscleaner_native.dll", "junkscleaner_native.dll"]
    elif system == "Darwin":
        names = ["libjunkscleaner_native.dylib"]
    else:
        names = ["libjunkscleaner_native.so"]

    # Search paths in order of preference
    search_dirs = [
        # Explicit env override
        os.environ.get("JC_NATIVE_LIB_DIR"),
        # Package native lib directory
        Path(__file__).parent / "bin",
        # Typical CMake build outputs
        Path(__file__).parents[2] / "build" / "bin",
        Path(__file__).parents[2] / "build" / "bin" / "Release",
        Path(__file__).parents[2] / "build" / "bin" / "Debug",
        Path(__file__).parents[2] / "build" / "src" / "native",
        Path(__file__).parents[2] / "build" / "windows-ninja" / "bin",
        Path(__file__).parents[2] / "build" / "linux-ninja" / "bin",
        Path.cwd() / "build" / "bin",
        Path.cwd() / "build" / "bin" / "Release",
        Path.cwd() / "build" / "bin" / "Debug",
    ]

    for d in search_dirs:
        if not d:
            continue
        directory = Path(d)
        if not directory.is_dir():
            continue
        for name in names:
            candidate = directory / name
            if candidate.is_file():
                return candidate.resolve()

    raise FileNotFoundError(
        f"Could not find JunksCleaner native library ({', '.join(names)}) in search paths."
    )


class NativeCore:
    """Thread-safe facade over the JunksCleaner C ABI."""

    def __init__(self, lib_path: Path | None = None) -> None:
        self.lib_path = (lib_path or find_native_library()).resolve()
        if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(str(self.lib_path.parent))
            except (OSError, ValueError):
                pass
        self._lib = ctypes.CDLL(str(self.lib_path))
        self._bind_functions()
        self._verify_abi()

    def _bind_functions(self) -> None:
        """Bind function prototypes with strict ctypes signatures."""
        self._jc_get_abi_version = self._lib.jc_get_abi_version
        self._jc_get_abi_version.argtypes = [ctypes.POINTER(CTypesVersionInfo)]
        self._jc_get_abi_version.restype = ctypes.c_int

        self._jc_get_library_version = self._lib.jc_get_library_version
        self._jc_get_library_version.argtypes = [ctypes.POINTER(CTypesVersionInfo)]
        self._jc_get_library_version.restype = ctypes.c_int

        self._jc_get_capabilities = self._lib.jc_get_capabilities
        self._jc_get_capabilities.argtypes = [ctypes.POINTER(CTypesCapabilities)]
        self._jc_get_capabilities.restype = ctypes.c_int

        self._jc_get_system_snapshot = self._lib.jc_get_system_snapshot
        self._jc_get_system_snapshot.argtypes = [ctypes.POINTER(CTypesSystemSnapshot)]
        self._jc_get_system_snapshot.restype = ctypes.c_int

        self._jc_scan_cleanup_targets = self._lib.jc_scan_cleanup_targets
        self._jc_scan_cleanup_targets.argtypes = [
            ctypes.POINTER(CTypesScanOptions),
            ctypes.POINTER(ctypes.POINTER(CTypesScanResult)),
        ]
        self._jc_scan_cleanup_targets.restype = ctypes.c_int

        self._jc_free_scan_result = self._lib.jc_free_scan_result
        self._jc_free_scan_result.argtypes = [ctypes.POINTER(CTypesScanResult)]
        self._jc_free_scan_result.restype = None

        self._jc_execute_cleanup = self._lib.jc_execute_cleanup
        self._jc_execute_cleanup.argtypes = [
            ctypes.POINTER(CTypesCleanupOptions),
            ctypes.POINTER(CTypesCleanupReport),
        ]
        self._jc_execute_cleanup.restype = ctypes.c_int

        self._jc_status_to_string = self._lib.jc_status_to_string
        self._jc_status_to_string.argtypes = [ctypes.c_int]
        self._jc_status_to_string.restype = ctypes.c_char_p

    def get_status_message(self, status: JcStatus) -> str:
        """Get the human-readable description for a status code."""
        ptr = self._jc_status_to_string(status.value)
        if ptr:
            return ptr.decode("utf-8", errors="replace")
        return "Unknown status"

    def _verify_abi(self) -> None:
        """Verify that the native library's ABI version matches our expectation."""
        abi_info = self.get_abi_version()
        expected_major = (JC_CURRENT_ABI_VERSION >> 24) & 0xFF
        if abi_info.major != expected_major:
            msg = (
                f"Native ABI version major {abi_info.major} is incompatible "
                f"with Python expectations {expected_major}."
            )
            raise JcAbiMismatchError(JcStatus.ERROR_ABI_MISMATCH, msg)

    def get_abi_version(self) -> JcVersionInfo:
        """Retrieve ABI version from native library."""
        info = CTypesVersionInfo()
        info.struct_size = ctypes.sizeof(CTypesVersionInfo)
        res = self._jc_get_abi_version(ctypes.byref(info))
        status = JcStatus(res)
        if status != JcStatus.OK:
            raise JcNativeError(status, self.get_status_message(status))
        return JcVersionInfo(
            major=info.major,
            minor=info.minor,
            patch=info.patch,
            abi_version=info.abi_version,
        )

    def get_library_version(self) -> JcVersionInfo:
        """Retrieve library release version from native library."""
        info = CTypesVersionInfo()
        info.struct_size = ctypes.sizeof(CTypesVersionInfo)
        res = self._jc_get_library_version(ctypes.byref(info))
        status = JcStatus(res)
        if status != JcStatus.OK:
            raise JcNativeError(status, self.get_status_message(status))
        return JcVersionInfo(
            major=info.major,
            minor=info.minor,
            patch=info.patch,
            abi_version=info.abi_version,
        )

    def get_capabilities(self) -> JcCapabilities:
        """Query platform and system capabilities."""
        caps = CTypesCapabilities()
        caps.struct_size = ctypes.sizeof(CTypesCapabilities)
        caps.abi_version = JC_CURRENT_ABI_VERSION
        res = self._jc_get_capabilities(ctypes.byref(caps))
        status = JcStatus(res)
        if status != JcStatus.OK:
            raise JcNativeError(status, self.get_status_message(status))

        return JcCapabilities(
            os_family=JcOsFamily(caps.os_family),
            architecture=JcArchitecture(caps.architecture),
            supported_capabilities=JcCapabilityFlags(caps.supported_capabilities),
            elevated_capabilities=JcCapabilityFlags(caps.elevated_capabilities),
            os_version_string=caps.os_version_string.decode("utf-8", errors="replace"),
        )

    def get_system_snapshot(self) -> JcSystemSnapshot:
        """Capture real-time system metrics snapshot."""
        snap = CTypesSystemSnapshot()
        snap.struct_size = ctypes.sizeof(CTypesSystemSnapshot)
        snap.abi_version = JC_CURRENT_ABI_VERSION
        res = self._jc_get_system_snapshot(ctypes.byref(snap))
        status = JcStatus(res)
        if status != JcStatus.OK:
            raise JcNativeError(status, self.get_status_message(status))

        disks: list[JcDiskInfo] = []
        for i in range(snap.disk_count):
            d = snap.disks[i]
            mount_str = d.mount_point.decode("utf-8", errors="replace")
            disks.append(
                JcDiskInfo(
                    mount_point=mount_str,
                    total_bytes=d.total_bytes,
                    free_bytes=d.free_bytes,
                    available_bytes=d.available_bytes,
                )
            )

        return JcSystemSnapshot(
            timestamp_ms=snap.timestamp_ms,
            validity_flags=JcSnapshotValidityFlags(snap.validity_flags),
            cpu_usage_percent=snap.cpu_usage_percent,
            logical_cpu_cores=snap.logical_cpu_cores,
            physical_cpu_cores=snap.physical_cpu_cores,
            memory_total_bytes=snap.memory_total_bytes,
            memory_used_bytes=snap.memory_used_bytes,
            memory_available_bytes=snap.memory_available_bytes,
            memory_cached_bytes=snap.memory_cached_bytes,
            memory_committed_bytes=snap.memory_committed_bytes,
            memory_commit_limit_bytes=snap.memory_commit_limit_bytes,
            swap_total_bytes=snap.swap_total_bytes,
            swap_used_bytes=snap.swap_used_bytes,
            process_count=snap.process_count,
            thread_count=snap.thread_count,
            disks=disks,
        )

    def scan_cleanup_targets(
        self,
        custom_root_override: str | None = None,
        min_age_seconds: int = 0,
        max_depth: int = 5,
    ) -> JcScanResult:
        """Scan allow-listed cleanup targets to discover disposable candidate files."""
        opts = CTypesScanOptions()
        opts.struct_size = ctypes.sizeof(CTypesScanOptions)
        opts.abi_version = JC_CURRENT_ABI_VERSION
        opts.custom_root_override = (
            custom_root_override.encode("utf-8") if custom_root_override else None
        )
        opts.min_age_seconds = min_age_seconds
        opts.max_depth = max_depth

        res_ptr = ctypes.POINTER(CTypesScanResult)()
        ret = self._jc_scan_cleanup_targets(ctypes.byref(opts), ctypes.byref(res_ptr))
        status = JcStatus(ret)
        if status != JcStatus.OK:
            raise JcNativeError(status, self.get_status_message(status))

        try:
            res = res_ptr.contents
            items: list[JcCleanupItem] = []
            for i in range(res.item_count):
                c_item = res.items[i]
                items.append(
                    JcCleanupItem(
                        target_id=c_item.target_id.decode("utf-8", errors="replace"),
                        relative_path=c_item.relative_path.decode("utf-8", errors="replace"),
                        display_path=c_item.display_path.decode("utf-8", errors="replace"),
                        size_bytes=c_item.size_bytes,
                        last_modified_ms=c_item.last_modified_ms,
                        risk_level=JcRiskLevel(c_item.risk_level),
                        is_locked=bool(c_item.is_locked),
                    )
                )

            return JcScanResult(
                total_candidates_count=res.total_candidates_count,
                total_estimated_bytes=res.total_estimated_bytes,
                items=items,
            )
        finally:
            self._jc_free_scan_result(res_ptr)

    def execute_cleanup(
        self,
        items: list[JcCleanupItem],
        custom_root_override: str | None = None,
        is_dry_run: bool = False,
        cancel_token: ctypes.c_int32 | None = None,
    ) -> JcCleanupReport:
        """Execute cleanup deletion of user-approved candidate items."""
        opts = CTypesCleanupOptions()
        opts.struct_size = ctypes.sizeof(CTypesCleanupOptions)
        opts.abi_version = JC_CURRENT_ABI_VERSION
        opts.custom_root_override = (
            custom_root_override.encode("utf-8") if custom_root_override else None
        )
        opts.item_count = len(items)
        opts.is_dry_run = 1 if is_dry_run else 0
        opts.cancel_token = ctypes.pointer(cancel_token) if cancel_token is not None else None

        c_items_array = (CTypesCleanupItem * len(items))()
        for i, item in enumerate(items):
            c_items_array[i].target_id = item.target_id.encode("utf-8")[:31]
            c_items_array[i].relative_path = item.relative_path.encode("utf-8")[:259]
            c_items_array[i].display_path = item.display_path.encode("utf-8")[:259]
            c_items_array[i].size_bytes = item.size_bytes
            c_items_array[i].last_modified_ms = item.last_modified_ms
            c_items_array[i].risk_level = item.risk_level.value
            c_items_array[i].is_locked = 1 if item.is_locked else 0

        opts.items = ctypes.cast(c_items_array, ctypes.POINTER(CTypesCleanupItem))

        report = CTypesCleanupReport()
        report.struct_size = ctypes.sizeof(CTypesCleanupReport)
        report.abi_version = JC_CURRENT_ABI_VERSION

        ret = self._jc_execute_cleanup(ctypes.byref(opts), ctypes.byref(report))
        status = JcStatus(ret)
        if status not in (JcStatus.OK, JcStatus.ERROR_PARTIAL_SUCCESS, JcStatus.ERROR_CANCELLED):
            raise JcNativeError(status, self.get_status_message(status))

        return JcCleanupReport(
            duration_ms=report.duration_ms,
            selected_count=report.selected_count,
            deleted_count=report.deleted_count,
            skipped_count=report.skipped_count,
            failed_count=report.failed_count,
            actual_bytes_deleted=report.actual_bytes_deleted,
            was_cancelled=bool(report.was_cancelled),
        )


_global_instance: NativeCore | None = None


def get_native_core() -> NativeCore:
    """Return a singleton instance of NativeCore."""
    global _global_instance
    if _global_instance is None:
        _global_instance = NativeCore()
    return _global_instance
