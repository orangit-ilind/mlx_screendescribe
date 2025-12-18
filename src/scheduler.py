"""Scheduler module for periodic execution."""

import threading
import time
from typing import Callable, Optional

from config import SCREENSHOT_INTERVAL_SECONDS
from src.logging_service import get_logging_service


class Scheduler:
    """Scheduler for periodic task execution."""

    def __init__(
        self,
        task: Callable[[], None],
        interval: Optional[int] = None,
    ):
        """
        Initialize scheduler.

        Args:
            task: Callable to execute periodically (should be async-safe)
            interval: Interval in seconds. Defaults to config.SCREENSHOT_INTERVAL_SECONDS
        """
        self.task = task
        self.interval = interval or SCREENSHOT_INTERVAL_SECONDS
        self._timer: Optional[threading.Timer] = None
        self._running = False
        self._lock = threading.Lock()
        self._is_processing = False
        self.logger = get_logging_service()

    def start(self) -> None:
        """Start the scheduler."""
        with self._lock:
            if self._running:
                self.logger.warning("Scheduler is already running")
                return

            self._running = True
            self.logger.info(f"Scheduler started with {self.interval}s interval")
            self._schedule_next()

    def stop(self) -> None:
        """Stop the scheduler."""
        with self._lock:
            if not self._running:
                return

            self._running = False
            if self._timer:
                self._timer.cancel()
                self._timer = None
            self.logger.info("Scheduler stopped")

    def _schedule_next(self) -> None:
        """Schedule the next execution."""
        if not self._running:
            return

        self._timer = threading.Timer(self.interval, self._execute)
        self._timer.daemon = True
        self._timer.start()

    def _execute(self) -> None:
        """Execute the task and schedule the next one."""
        # Prevent concurrent executions
        if self._is_processing:
            self.logger.warning("Task already in progress, skipping this execution")
            self._schedule_next()
            return

        self._is_processing = True

        try:
            self.logger.info(
                f"Executing scheduled task at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self.task()
        except Exception as e:
            self.logger.error(f"Error in scheduled task: {e}")
        finally:
            self._is_processing = False
            # Schedule next execution
            if self._running:
                self._schedule_next()

    def trigger_now(self) -> None:
        """Manually trigger the task immediately (for testing)."""
        if self._is_processing:
            self.logger.warning("Task already in progress, cannot trigger now")
            return

        self.logger.info("Manually triggering task")
        self._execute()

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running
