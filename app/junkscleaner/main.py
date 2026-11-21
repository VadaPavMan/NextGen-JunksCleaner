"""Application entry point for JunksCleaner."""

# ruff: noqa: E402
import sys
from pathlib import Path

# Ensure package directory is in sys.path when invoked directly as a script
_package_root = str(Path(__file__).resolve().parents[1])
if _package_root not in sys.path:
    sys.path.insert(0, _package_root)

from PySide6.QtWidgets import QApplication

from junkscleaner.core.config import ConfigManager
from junkscleaner.native.ffi import get_native_core
from junkscleaner.services.cleaner import JunkCleanerService
from junkscleaner.services.memory import MemoryCleanerService
from junkscleaner.services.monitor import SystemMonitorService
from junkscleaner.views.main_window import MainWindow


def main() -> int:
    """Initialize application runtime and launch main window."""
    app = QApplication(sys.argv)
    app.setApplicationName("JunksCleaner")
    app.setOrganizationName("JunksCleaner")

    native_core = get_native_core()
    config_mgr = ConfigManager()
    monitor_service = SystemMonitorService(
        native_core=native_core,
        interval_seconds=config_mgr.config.monitoring_interval_seconds,
    )
    cleaner_service = JunkCleanerService(native_core=native_core)
    memory_service = MemoryCleanerService(native_core=native_core)

    window = MainWindow(
        native_core=native_core,
        config_mgr=config_mgr,
        monitor_service=monitor_service,
        cleaner_service=cleaner_service,
        memory_service=memory_service,
    )
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
