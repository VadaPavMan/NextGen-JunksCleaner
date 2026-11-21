"""Main application window for JunksCleaner."""

from junkscleaner.core.config import ConfigManager
from junkscleaner.native.ffi import NativeCore
from junkscleaner.native.types import JcSystemSnapshot
from junkscleaner.resources.assets import get_asset_path
from junkscleaner.resources.theme import get_stylesheet
from junkscleaner.services.cleaner import JunkCleanerService
from junkscleaner.services.memory import MemoryCleanerService
from junkscleaner.services.monitor import SystemMonitorService
from junkscleaner.views.activity_page import ActivityPage
from junkscleaner.views.cleaner_page import CleanerPage
from junkscleaner.views.dashboard_page import DashboardPage
from junkscleaner.views.memory_page import MemoryPage
from junkscleaner.views.settings_page import SettingsPage
from PySide6.QtCore import QObject, QSize, Qt, Signal, Slot
from PySide6.QtGui import QCloseEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
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
        memory_service: MemoryCleanerService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.native_core = native_core
        self.config_mgr = config_mgr
        self.monitor_service = monitor_service
        self.cleaner_service = cleaner_service
        self.memory_service = memory_service or MemoryCleanerService(native_core=self.native_core)

        self.setWindowTitle("JunksCleaner - NextGen System Utility")
        self.setWindowIcon(QIcon(get_asset_path("appicon.png")))
        self.resize(1060, 680)
        self.setMinimumSize(880, 560)

        # Bridge for thread-safe telemetry updates
        self.bridge = MonitorBridge()

        self._setup_ui()
        self._apply_theme(self.config_mgr.config.theme)

        # Connect telemetry bridge
        self.bridge.snapshot_ready.connect(self.dashboard_page.update_snapshot)
        self.bridge.snapshot_ready.connect(self.memory_page.update_snapshot)
        self.monitor_service.subscribe(self._on_monitor_snapshot)
        self.monitor_service.start()

    @staticmethod
    def _wrap_scroll(widget: QWidget) -> QScrollArea:
        """Wrap view page in responsive scroll container to support any window size."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(widget)
        return scroll

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Brand header
        brand_frame = QWidget()
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(16, 20, 16, 16)
        brand_layout.setSpacing(10)

        logo_label = QLabel()
        app_icon_pixmap = QPixmap(get_asset_path("appicon.png"))
        if not app_icon_pixmap.isNull():
            logo_label.setPixmap(
                app_icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        logo_label.setFixedSize(24, 24)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(1)
        brand_text.setContentsMargins(0, 0, 0, 0)
        title_label = QLabel("JunksCleaner")
        title_label.setObjectName("AppTitle")
        subtitle_label = QLabel("System Utility")
        subtitle_label.setObjectName("SidebarSubtitle")
        brand_text.addWidget(title_label)
        brand_text.addWidget(subtitle_label)

        brand_layout.addWidget(logo_label)
        brand_layout.addLayout(brand_text)
        brand_layout.addStretch()
        sidebar_layout.addWidget(brand_frame)

        # Separator
        sep = QFrame()
        sep.setObjectName("SidebarSeparator")
        sep.setFixedHeight(1)
        sidebar_layout.addWidget(sep)

        # Navigation
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 8, 0, 8)
        nav_layout.setSpacing(2)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_dashboard = self._create_nav_button("Dashboard", "dashboard.png", 0)
        self.btn_cleaner = self._create_nav_button("Junk Cleaner", "clean.png", 1)
        self.btn_memory = self._create_nav_button("Clean Memory", "ram.png", 2)
        self.btn_activity = self._create_nav_button("Activity Log", "activitylog.png", 3)
        self.btn_settings = self._create_nav_button("Settings", "settings.png", 4)

        nav_layout.addWidget(self.btn_dashboard)
        nav_layout.addWidget(self.btn_cleaner)
        nav_layout.addWidget(self.btn_memory)
        nav_layout.addWidget(self.btn_activity)
        nav_layout.addWidget(self.btn_settings)

        sidebar_layout.addWidget(nav_container)
        sidebar_layout.addStretch()

        # Sidebar footer — engine status (compact)
        footer = QWidget()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(16, 8, 16, 14)
        footer_layout.setSpacing(2)

        status_line = QLabel("Native Core Active")
        status_line.setObjectName("BadgeGreen")
        status_line.setStyleSheet(
            "color: #27ae60; font-size: 10px; font-weight: 600; "
            "background: transparent; border: none; padding: 0;"
        )
        engine_line = QLabel("C ABI Engine v1.0.0")
        engine_line.setStyleSheet("color: #5a5856; font-size: 10px;")

        footer_layout.addWidget(status_line)
        footer_layout.addWidget(engine_line)
        sidebar_layout.addWidget(footer)

        main_layout.addWidget(sidebar)

        # ── Main content area ────────────────────────────────────────
        self.stack = QStackedWidget()

        capabilities = None
        try:
            capabilities = self.native_core.get_capabilities()
        except Exception:
            pass

        self.dashboard_page = DashboardPage(capabilities=capabilities)
        self.cleaner_page = CleanerPage(service=self.cleaner_service)
        self.memory_page = MemoryPage(service=self.memory_service)
        self.activity_page = ActivityPage(service=self.cleaner_service)
        self.settings_page = SettingsPage(
            config_mgr=self.config_mgr,
            monitor_service=self.monitor_service,
        )

        self.cleaner_page.cleanup_completed.connect(lambda _: self.activity_page.refresh())
        self.memory_page.memory_cleaned.connect(lambda _: self.activity_page.refresh())
        self.settings_page.theme_changed.connect(self._apply_theme)

        self.stack.addWidget(self._wrap_scroll(self.dashboard_page))
        self.stack.addWidget(self._wrap_scroll(self.cleaner_page))
        self.stack.addWidget(self._wrap_scroll(self.memory_page))
        self.stack.addWidget(self._wrap_scroll(self.activity_page))
        self.stack.addWidget(self._wrap_scroll(self.settings_page))

        main_layout.addWidget(self.stack)

        self.btn_dashboard.setChecked(True)

    def _create_nav_button(self, label: str, icon_filename: str, index: int) -> QPushButton:
        btn = QPushButton(f"  {label}")
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setToolTip(label)
        icon_path = get_asset_path(icon_filename)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(18, 18))
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
