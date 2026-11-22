"""Settings view for user preferences, appearance, and polling intervals."""

from junkscleaner.core.config import ConfigManager
from junkscleaner.services.monitor import SystemMonitorService
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
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
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        title = QLabel("Settings")
        title.setObjectName("PageTitle")
        header.addWidget(title)

        subtitle = QLabel("Application theme, monitoring, and preferences")
        subtitle.setObjectName("PageSubtitle")
        header.addWidget(subtitle)
        layout.addLayout(header)

        # ── Appearance section ───────────────────────────────────────
        appearance_card = QFrame()
        appearance_card.setObjectName("Card")
        ac = QVBoxLayout(appearance_card)
        ac.setContentsMargins(16, 14, 16, 14)
        ac.setSpacing(12)

        sec_title = QLabel("Appearance")
        sec_title.setObjectName("SectionTitle")
        ac.addWidget(sec_title)

        theme_row = QHBoxLayout()
        theme_label = QLabel("Visual Theme")
        theme_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        theme_row.addWidget(theme_label)
        theme_row.addStretch()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setFixedWidth(140)
        current_theme = self.config_mgr.config.theme.capitalize()
        idx = self.theme_combo.findText(current_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_combo)

        ac.addLayout(theme_row)
        layout.addWidget(appearance_card)

        # ── Monitoring section ───────────────────────────────────────
        monitoring_card = QFrame()
        monitoring_card.setObjectName("Card")
        mc = QVBoxLayout(monitoring_card)
        mc.setContentsMargins(16, 14, 16, 14)
        mc.setSpacing(12)

        mon_title = QLabel("Monitoring")
        mon_title.setObjectName("SectionTitle")
        mc.addWidget(mon_title)

        interval_row = QHBoxLayout()
        interval_label = QLabel("Telemetry Polling Interval")
        interval_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        interval_row.addWidget(interval_label)
        interval_row.addStretch()

        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.5, 10.0)
        self.interval_spin.setSingleStep(0.5)
        self.interval_spin.setSuffix(" sec")
        self.interval_spin.setFixedWidth(120)
        self.interval_spin.setValue(self.monitor_service.interval)
        self.interval_spin.valueChanged.connect(self._on_interval_changed)
        interval_row.addWidget(self.interval_spin)

        mc.addLayout(interval_row)
        layout.addWidget(monitoring_card)

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
