"""Dashboard page showing live system resource telemetry and status."""

from junkscleaner.native.types import (
    JcCapabilities,
    JcSnapshotValidityFlags,
    JcSystemSnapshot,
)
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class MetricCard(QFrame):
    """Reusable visual card displaying a single telemetry metric."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        layout.addWidget(self.title_label)

        self.value_label = QLabel("Loading...")
        self.value_label.setObjectName("MetricValue")
        layout.addWidget(self.value_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.subtext_label = QLabel("")
        self.subtext_label.setObjectName("MetricSubtext")
        layout.addWidget(self.subtext_label)

    def set_data(
        self,
        value: str,
        subtext: str = "",
        percent: float | None = None,
        available: bool = True,
    ) -> None:
        if not available:
            self.value_label.setText("N/A")
            self.subtext_label.setText("Metric unavailable on this system")
            self.progress_bar.hide()
            return

        self.value_label.setText(value)
        self.subtext_label.setText(subtext)
        if percent is not None:
            self.progress_bar.setValue(int(percent))
            self.progress_bar.show()
        else:
            self.progress_bar.hide()


class DashboardPage(QWidget):
    """Dashboard view presenting live system metrics."""

    def __init__(
        self,
        capabilities: JcCapabilities | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.capabilities = capabilities

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Header section
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        title = QLabel("System Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        os_info = capabilities.os_version_string if capabilities else "Local System"
        subtitle = QLabel(f"Live telemetry for {os_info}")
        subtitle.setStyleSheet("color: #71717a; font-size: 13px;")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Grid of cards
        grid = QGridLayout()
        grid.setSpacing(16)

        self.cpu_card = MetricCard("Processor (CPU)")
        grid.addWidget(self.cpu_card, 0, 0)

        self.memory_card = MetricCard("Physical Memory (RAM)")
        grid.addWidget(self.memory_card, 0, 1)

        self.disk_card = MetricCard("Primary Storage")
        grid.addWidget(self.disk_card, 1, 0)

        self.system_card = MetricCard("System Environment")
        grid.addWidget(self.system_card, 1, 1)

        main_layout.addLayout(grid)
        main_layout.addStretch()

        if capabilities:
            self.system_card.set_data(
                value=capabilities.os_family.name.capitalize(),
                subtext=f"{capabilities.architecture.name} - {capabilities.os_version_string}",
                available=True,
            )

    @Slot(object)
    def update_snapshot(self, snap: JcSystemSnapshot) -> None:
        """Update telemetry metrics on the dashboard."""
        # CPU
        if snap.is_valid(JcSnapshotValidityFlags.CPU_USAGE):
            cores_txt = f"{snap.logical_cpu_cores} Logical Cores"
            self.cpu_card.set_data(
                value=snap.cpu_usage_display,
                subtext=cores_txt,
                percent=snap.cpu_usage_percent,
                available=True,
            )
        else:
            self.cpu_card.set_data("N/A", available=False)

        # Memory
        if (
            snap.is_valid(JcSnapshotValidityFlags.MEM_TOTAL)
            and snap.memory_used_percent is not None
        ):
            val_txt = f"{snap.memory_used_percent:.1f}%"
            sub_txt = f"{snap.memory_used_display} used of {snap.memory_total_display}"
            if snap.is_valid(JcSnapshotValidityFlags.MEM_CACHED):
                sub_txt += f" ({snap.memory_cached_display} cached)"
            self.memory_card.set_data(
                value=val_txt,
                subtext=sub_txt,
                percent=snap.memory_used_percent,
                available=True,
            )
        else:
            self.memory_card.set_data("N/A", available=False)

        # Storage
        if snap.is_valid(JcSnapshotValidityFlags.PRIMARY_DISK) and snap.disks:
            d = snap.disks[0]
            val_txt = f"{d.used_percent:.1f}%"
            sub_txt = f"Volume {d.mount_point}: {d.free_display} free of {d.total_display}"
            self.disk_card.set_data(
                value=val_txt,
                subtext=sub_txt,
                percent=d.used_percent,
                available=True,
            )
        else:
            self.disk_card.set_data("N/A", available=False)
