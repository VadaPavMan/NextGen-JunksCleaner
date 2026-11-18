"""System monitoring service providing asynchronous metrics sampling and history tracking."""

import logging
import threading
from collections import deque
from collections.abc import Callable

from junkscleaner.native.ffi import NativeCore, get_native_core
from junkscleaner.native.types import JcSystemSnapshot

logger = logging.getLogger(__name__)

SnapshotSubscriber = Callable[[JcSystemSnapshot], None]


class SystemMonitorService:
    """Background system monitoring service.

    Features:
    - Periodically samples JcSystemSnapshot from NativeCore on a worker thread.
    - Maintains a bounded, thread-safe history buffer (default: 60 samples).
    - Distributes snapshots to registered callbacks/subscribers.
    - Supports pausing (e.g. when application window is minimized).
    - Deterministic, graceful shutdown.
    """

    def __init__(
        self,
        native_core: NativeCore | None = None,
        interval_seconds: float = 2.0,
        max_history_size: int = 60,
    ) -> None:
        self._native_core = native_core or get_native_core()
        self._interval = max(0.2, interval_seconds)
        self._max_history = max(10, max_history_size)

        self._lock = threading.Lock()
        self._history: deque[JcSystemSnapshot] = deque(maxlen=self._max_history)
        self._subscribers: list[SnapshotSubscriber] = []

        self._running = False
        self._paused = False
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    @property
    def interval(self) -> float:
        return self._interval

    @interval.setter
    def interval(self, val: float) -> None:
        self._interval = max(0.2, val)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    def subscribe(self, callback: SnapshotSubscriber) -> None:
        """Register a callback invoked whenever a new snapshot is captured."""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: SnapshotSubscriber) -> None:
        """Unregister a subscriber callback."""
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    def sample_now(self) -> JcSystemSnapshot:
        """Take an immediate synchronous snapshot and store it in history."""
        snapshot = self._native_core.get_system_snapshot()
        with self._lock:
            self._history.append(snapshot)
            subscribers = list(self._subscribers)

        for sub in subscribers:
            try:
                sub(snapshot)
            except Exception as e:
                logger.error("Error in snapshot subscriber callback: %s", e)

        return snapshot

    def get_latest_snapshot(self) -> JcSystemSnapshot | None:
        """Return the most recently captured snapshot, if any."""
        with self._lock:
            return self._history[-1] if self._history else None

    def get_history(self) -> list[JcSystemSnapshot]:
        """Return a copy of the recent snapshot history buffer."""
        with self._lock:
            return list(self._history)

    def clear_history(self) -> None:
        """Clear recorded history buffer."""
        with self._lock:
            self._history.clear()

    def start(self) -> None:
        """Start the background sampling thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._paused = False
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._worker_loop,
                name="JcSystemMonitorWorker",
                daemon=True,
            )
            self._thread.start()

    def pause(self) -> None:
        """Pause polling without terminating the worker thread."""
        with self._lock:
            self._paused = True

    def resume(self) -> None:
        """Resume polling if currently paused."""
        with self._lock:
            self._paused = False

    def stop(self, timeout_seconds: float = 3.0) -> None:
        """Stop the background sampling thread and wait for it to join."""
        with self._lock:
            if not self._running:
                return
            self._running = False
            self._stop_event.set()
            thread = self._thread

        if thread and thread.is_alive():
            thread.join(timeout=timeout_seconds)

        with self._lock:
            self._thread = None

    def _worker_loop(self) -> None:
        """Internal sampling loop running on worker thread."""
        while not self._stop_event.is_set():
            if not self._paused:
                try:
                    self.sample_now()
                except Exception as e:
                    logger.error("Failed to capture system snapshot: %s", e)

            # Wait for next interval or stop event
            self._stop_event.wait(self._interval)
