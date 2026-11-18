"""ctypes FFI wrapper for JunksCleaner native C ABI."""

import ctypes
import os
import platform
import sys
from pathlib import Path

from .types import (
    JC_CURRENT_ABI_VERSION,
    CTypesCapabilities,
    CTypesSystemSnapshot,
    CTypesVersionInfo,
    JcArchitecture,
    JcCapabilities,
    JcCapabilityFlags,
    JcDiskInfo,
    JcOsFamily,
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
        Path(__file__).parents[2] / "build" / "src" / "native",
        Path(__file__).parents[2] / "build" / "windows-ninja" / "bin",
        Path(__file__).parents[2] / "build" / "linux-ninja" / "bin",
        Path.cwd() / "build" / "bin",
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


_global_instance: NativeCore | None = None


def get_native_core() -> NativeCore:
    """Return a singleton instance of NativeCore."""
    global _global_instance
    if _global_instance is None:
        _global_instance = NativeCore()
    return _global_instance
