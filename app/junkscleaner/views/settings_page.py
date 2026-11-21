"""Settings view for user preferences, appearance, and polling intervals."""

from junkscleaner.core.config import ConfigManager
from junkscleaner.services.monitor import SystemMonitorService
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QWidget):
    """Settings page allowing configuration changes."""

    theme_changed = Signal(str)

    def __init__(
        self,
        config_mgr: ConfigManager,
        monitor_service: SystemMonitorService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.config_mgr = config_mgr
        self.monitor_service = monitor_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Settings & Preferences")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Personalize application theme, monitoring frequency, and options")
        subtitle.setStyleSheet("color: #888888; font-size: 13px;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Card container
        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        form.setContentsMargins(16, 16, 16, 16)
        form.setSpacing(16)

        # Theme selector
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        current_theme = self.config_mgr.config.theme.capitalize()
        idx = self.theme_combo.findText(current_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        form.addRow("Visual Theme:", self.theme_combo)

        # Monitoring interval
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.5, 10.0)
        self.interval_spin.setSingleStep(0.5)
        self.interval_spin.setSuffix(" seconds")
        self.interval_spin.setValue(self.monitor_service.interval)
        self.interval_spin.valueChanged.connect(self._on_interval_changed)
        form.addRow("Telemetry Polling Interval:", self.interval_spin)

        layout.addWidget(card)
        layout.addStretch()

    @Slot(str)
    def _on_theme_changed(self, text: str) -> None:
        theme = text.lower()
        self.config_mgr.config.theme = theme
        self.config_mgr.save()
        self.theme_changed.emit(theme)

    @Slot(float)
    def _on_interval_changed(self, val: float) -> None:
        self.monitor_service.interval = val
        self.config_mgr.config.monitoring_interval_seconds = val
        self.config_mgr.save()
