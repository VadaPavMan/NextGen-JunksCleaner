"""Background QThread worker for executing memory optimization without blocking GUI."""

from PySide6.QtCore import QThread, Signal

from junkscleaner.native.types import JcMemoryOperationFlags
from junkscleaner.services.memory import MemoryCleanerService


class MemoryCleanWorker(QThread):
    """Worker thread running memory optimization operations asynchronously."""

    clean_started = Signal()
    clean_finished = Signal(object)  # JcMemoryCleanResult
    clean_failed = Signal(str)

    def __init__(
        self,
        service: MemoryCleanerService,
        operations: JcMemoryOperationFlags | int,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.service = service
        self.operations = operations

    def run(self) -> None:
        self.clean_started.emit()
        try:
            result = self.service.clean(self.operations)
            self.clean_finished.emit(result)
        except Exception as e:
            self.clean_failed.emit(str(e))
