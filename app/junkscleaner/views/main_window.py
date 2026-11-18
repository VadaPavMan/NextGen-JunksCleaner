"""Main application window for JunksCleaner."""

from junkscleaner.core.config import ConfigManager
from junkscleaner.native.ffi import NativeCore
from junkscleaner.native.types import JcSystemSnapshot
from junkscleaner.resources.theme import get_stylesheet
from junkscleaner.services.cleaner import JunkCleanerService
from junkscleaner.services.monitor import SystemMonitorService
from junkscleaner.views.activity_page import ActivityPage
from junkscleaner.views.cleaner_page import CleanerPage
from junkscleaner.views.dashboard_page import DashboardPage
from junkscleaner.views.settings_page import SettingsPage
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class MonitorBridge(QObject):
    """Bridge relaying worker callbacks safely into Qt main thread via signals."""

    snapshot_ready = Signal(object)


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation."""

    def __init__(
        self,
        native_core: NativeCore,
        config_mgr: ConfigManager,
        monitor_service: SystemMonitorService,
        cleaner_service: JunkCleanerService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.native_core = native_core
        self.config_mgr = config_mgr
        self.monitor_service = monitor_service
        self.cleaner_service = cleaner_service

        self.setWindowTitle("JunksCleaner - NextGen System Utility")
        self.resize(1050, 680)
        self.setMinimumSize(850, 520)

        # Bridge for thread-safe telemetry updates
        self.bridge = MonitorBridge()

        self._setup_ui()
        self._apply_theme(self.config_mgr.config.theme)

        # Connect telemetry bridge
        self.bridge.snapshot_ready.connect(self.dashboard_page.update_snapshot)
        self.monitor_service.subscribe(self._on_monitor_snapshot)
        self.monitor_service.start()

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Frame
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(8)

        # Logo / Title
        title_label = QLabel("JunksCleaner")
        title_label.setObjectName("AppTitle")
        sidebar_layout.addWidget(title_label)

        # Nav button group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_dashboard = self._create_nav_button("Dashboard", 0)
        self.btn_cleaner = self._create_nav_button("Junk Cleaner", 1)
        self.btn_activity = self._create_nav_button("Activity", 2)
        self.btn_settings = self._create_nav_button("Settings", 3)

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_cleaner)
        sidebar_layout.addWidget(self.btn_activity)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar)

        # 2. Main Stacked Pages
        self.stack = QStackedWidget()

        capabilities = None
        try:
            capabilities = self.native_core.get_capabilities()
        except Exception:
            pass

        self.dashboard_page = DashboardPage(capabilities=capabilities)
        self.cleaner_page = CleanerPage(service=self.cleaner_service)
        self.activity_page = ActivityPage(service=self.cleaner_service)
        self.settings_page = SettingsPage(
            config_mgr=self.config_mgr,
            monitor_service=self.monitor_service,
        )

        self.cleaner_page.cleanup_completed.connect(lambda _: self.activity_page.refresh())
        self.settings_page.theme_changed.connect(self._apply_theme)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.cleaner_page)
        self.stack.addWidget(self.activity_page)
        self.stack.addWidget(self.settings_page)

        main_layout.addWidget(self.stack)

        self.btn_dashboard.setChecked(True)

    def _create_nav_button(self, label: str, index: int) -> QPushButton:
        btn = QPushButton(label)
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        self.nav_group.addButton(btn, index)
        return btn

    def _on_monitor_snapshot(self, snap: JcSystemSnapshot) -> None:
        """Invoked on worker thread, emits signal to main thread."""
        self.bridge.snapshot_ready.emit(snap)

    @Slot(str)
    def _apply_theme(self, theme_name: str) -> None:
        self.setStyleSheet(get_stylesheet(theme_name))

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ensure clean shutdown of background services and threads."""
        self.monitor_service.unsubscribe(self._on_monitor_snapshot)
        self.monitor_service.stop()
        super().closeEvent(event)
