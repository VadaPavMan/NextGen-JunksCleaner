"""Pytest configuration and safety-first fixtures for JunksCleaner."""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from junkscleaner.native.ffi import NativeCore, find_native_library
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Ensure a single shared QApplication instance exists for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(scope="session")
def native_core() -> NativeCore:
    """Fixture providing initialized NativeCore instance connected to the compiled library."""
    lib_path = find_native_library()
    assert lib_path.exists(), f"Native library does not exist at {lib_path}"
    return NativeCore(lib_path=lib_path)


@pytest.fixture
def safe_temp_workspace() -> Generator[Path, None, None]:
    """Safety fixture providing a completely isolated temporary root directory.

    Guarantees:
    - Never points to user home directory or system roots.
    - Path must contain 'jc_safe_test_' to verify test-isolation prefix.
    - Cleaned up automatically upon test completion.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="jc_safe_test_")).resolve()

    # Assert safety invariants
    assert "jc_safe_test_" in temp_dir.name
    assert temp_dir != Path.home().resolve()
    assert temp_dir != Path(temp_dir.anchor).resolve()

    try:
        yield temp_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
