"""Background QThread workers for non-blocking cleanup scanning and deletion."""

from PySide6.QtCore import QThread, Signal

from junkscleaner.native.types import JcCleanupItem
from junkscleaner.services.cleaner import JunkCleanerService


class ScanWorker(QThread):
    """Worker thread running filesystem scan without blocking GUI."""

    scan_started = Signal()
    scan_finished = Signal(object)  # JcScanResult
    scan_failed = Signal(str)

    def __init__(
        self,
        service: JunkCleanerService,
        custom_root_override: str | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.service = service
        self.custom_root_override = custom_root_override

    def run(self) -> None:
        self.scan_started.emit()
        try:
            result = self.service.scan(custom_root_override=self.custom_root_override)
            self.scan_finished.emit(result)
        except Exception as e:
            self.scan_failed.emit(str(e))


class CleanWorker(QThread):
    """Worker thread executing safe deletion without blocking GUI."""

    clean_started = Signal()
    clean_finished = Signal(object)  # JcCleanupReport
    clean_failed = Signal(str)

    def __init__(
        self,
        service: JunkCleanerService,
        items: list[JcCleanupItem],
        confirmed: bool,
        custom_root_override: str | None = None,
        is_dry_run: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.service = service
        self.items = items
        self.confirmed = confirmed
        self.custom_root_override = custom_root_override
        self.is_dry_run = is_dry_run

    def cancel(self) -> None:
        """Trigger cooperative cancellation."""
        self.service.cancel()

    def run(self) -> None:
        self.clean_started.emit()
        try:
            report = self.service.execute(
                items=self.items,
                confirmed=self.confirmed,
                custom_root_override=self.custom_root_override,
                is_dry_run=self.is_dry_run,
            )
            self.clean_finished.emit(report)
        except Exception as e:
            self.clean_failed.emit(str(e))
