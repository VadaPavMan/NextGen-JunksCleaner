"""Native C ABI bindings for JunksCleaner."""

from .ffi import NativeCore, get_native_core
from .types import (
    JcCapabilities,
    JcCleanupItem,
    JcCleanupReport,
    JcDiskInfo,
    JcRiskLevel,
    JcScanResult,
    JcSnapshotValidityFlags,
    JcStatus,
    JcSystemSnapshot,
    JcVersionInfo,
)

__all__ = [
    "JcCapabilities",
    "JcCleanupItem",
    "JcCleanupReport",
    "JcDiskInfo",
    "JcRiskLevel",
    "JcScanResult",
    "JcSnapshotValidityFlags",
    "JcStatus",
    "JcSystemSnapshot",
    "JcVersionInfo",
    "NativeCore",
    "get_native_core",
]
