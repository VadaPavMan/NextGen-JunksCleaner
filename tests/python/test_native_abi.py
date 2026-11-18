"""Tests for the Python to C ABI native binding."""

import platform
from pathlib import Path

from junkscleaner.native.ffi import (
    NativeCore,
    find_native_library,
)
from junkscleaner.native.types import (
    JC_ABI_VERSION_MAJOR,
    JcArchitecture,
    JcCapabilityFlags,
    JcOsFamily,
    JcStatus,
)


def test_native_library_discovery() -> None:
    """Ensure the native shared library is found on disk."""
    lib_path = find_native_library()
    assert lib_path.is_file()
    assert lib_path.stat().st_size > 0


def test_abi_version(native_core: NativeCore) -> None:
    """Verify ABI version matches Python expectations."""
    abi = native_core.get_abi_version()
    assert abi.major == JC_ABI_VERSION_MAJOR
    assert abi.minor == 0
    assert abi.patch == 0
    assert abi.version_string == "1.0.0"


def test_library_version(native_core: NativeCore) -> None:
    """Verify library implementation version is readable."""
    lib_ver = native_core.get_library_version()
    assert lib_ver.major == 0
    assert lib_ver.minor == 1
    assert lib_ver.patch == 0
    assert lib_ver.version_string == "0.1.0"


def test_capabilities(native_core: NativeCore) -> None:
    """Verify capabilities reflect the current host operating system."""
    caps = native_core.get_capabilities()

    current_system = platform.system()
    if current_system == "Windows":
        assert caps.os_family == JcOsFamily.WINDOWS
        assert caps.supports(JcCapabilityFlags.STANDBY_LIST_OPS)
        assert caps.requires_elevation(JcCapabilityFlags.STANDBY_LIST_OPS)
    elif current_system == "Linux":
        assert caps.os_family == JcOsFamily.LINUX
        assert caps.supports(JcCapabilityFlags.DROP_CACHES_OPS)
        assert caps.requires_elevation(JcCapabilityFlags.DROP_CACHES_OPS)

    assert caps.architecture != JcArchitecture.UNKNOWN
    assert caps.supports(JcCapabilityFlags.CPU_MONITORING)
    assert caps.supports(JcCapabilityFlags.MEMORY_MONITORING)
    assert caps.supports(JcCapabilityFlags.DISK_MONITORING)
    assert caps.supports(JcCapabilityFlags.CLEANUP_TEMP_FILES)
    assert len(caps.os_version_string) > 0


def test_status_messages(native_core: NativeCore) -> None:
    """Verify status code to string mappings."""
    assert native_core.get_status_message(JcStatus.OK) == "Success"
    assert "Invalid argument" in native_core.get_status_message(JcStatus.ERROR_INVALID_ARGUMENT)
    assert "ABI version mismatch" in native_core.get_status_message(JcStatus.ERROR_ABI_MISMATCH)


def test_safe_temp_workspace_safety(safe_temp_workspace: Path) -> None:
    """Verify safety fixture properties."""
    assert safe_temp_workspace.exists()
    assert safe_temp_workspace.is_dir()
    assert "jc_safe_test_" in safe_temp_workspace.name
    # Ensure it's not root or user home
    assert safe_temp_workspace != Path.home()
    assert safe_temp_workspace != safe_temp_workspace.parent
