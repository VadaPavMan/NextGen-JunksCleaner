"""Native C ABI bindings for JunksCleaner."""

from .ffi import NativeCore, get_native_core
from .types import (
    JcCapabilities,
    JcDiskInfo,
    JcSnapshotValidityFlags,
    JcStatus,
    JcSystemSnapshot,
    JcVersionInfo,
)

__all__ = [
    "JcCapabilities",
    "JcDiskInfo",
    "JcSnapshotValidityFlags",
    "JcStatus",
    "JcSystemSnapshot",
    "JcVersionInfo",
    "NativeCore",
    "get_native_core",
]
