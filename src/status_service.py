"""Status tracking service for application state."""

import threading
from datetime import datetime
from typing import Optional
from enum import Enum


class AppStatus(Enum):
    """Application status enumeration."""
    STOPPED = "stopped"
    RUNNING = "running"
    PROCESSING = "processing"
    ERROR = "error"


class StatusService:
    """Service for tracking application state."""

    def __init__(self):
        """Initialize status service."""
        self._status = AppStatus.STOPPED
        self._last_execution_time: Optional[datetime] = None
        self._last_entry_preview: Optional[str] = None
        self._last_entry_timestamp: Optional[datetime] = None
        self._error_count = 0
        self._next_execution_time: Optional[datetime] = None
        self._lock = threading.Lock()

    def set_status(self, status: AppStatus) -> None:
        """
        Set application status.

        Args:
            status: Application status
        """
        with self._lock:
            self._status = status

    def get_status(self) -> AppStatus:
        """
        Get application status.

        Returns:
            Application status
        """
        with self._lock:
            return self._status

    def is_running(self) -> bool:
        """
        Check if application is running.

        Returns:
            True if running, False otherwise
        """
        return self.get_status() == AppStatus.RUNNING

    def set_last_execution(self, timestamp: Optional[datetime] = None) -> None:
        """
        Set last execution time.

        Args:
            timestamp: Execution timestamp (defaults to now)
        """
        with self._lock:
            self._last_execution_time = timestamp or datetime.now()

    def get_last_execution_time(self) -> Optional[datetime]:
        """
        Get last execution time.

        Returns:
            Last execution timestamp or None
        """
        with self._lock:
            return self._last_execution_time

    def set_last_entry(self, preview: str, timestamp: Optional[datetime] = None) -> None:
        """
        Set last entry preview.

        Args:
            preview: Entry preview text (first 50-100 chars)
            timestamp: Entry timestamp (defaults to now)
        """
        with self._lock:
            self._last_entry_preview = preview[:100] if preview else None  # Limit to 100 chars
            self._last_entry_timestamp = timestamp or datetime.now()

    def get_last_entry_preview(self) -> Optional[str]:
        """
        Get last entry preview.

        Returns:
            Last entry preview or None
        """
        with self._lock:
            return self._last_entry_preview

    def get_last_entry_timestamp(self) -> Optional[datetime]:
        """
        Get last entry timestamp.

        Returns:
            Last entry timestamp or None
        """
        with self._lock:
            return self._last_entry_timestamp

    def increment_error_count(self) -> None:
        """Increment error count."""
        with self._lock:
            self._error_count += 1

    def reset_error_count(self) -> None:
        """Reset error count."""
        with self._lock:
            self._error_count = 0

    def get_error_count(self) -> int:
        """
        Get error count.

        Returns:
            Error count
        """
        with self._lock:
            return self._error_count

    def set_next_execution_time(self, timestamp: Optional[datetime]) -> None:
        """
        Set next scheduled execution time.

        Args:
            timestamp: Next execution timestamp or None
        """
        with self._lock:
            self._next_execution_time = timestamp

    def get_next_execution_time(self) -> Optional[datetime]:
        """
        Get next scheduled execution time.

        Returns:
            Next execution timestamp or None
        """
        with self._lock:
            return self._next_execution_time

    def get_status_string(self) -> str:
        """
        Get human-readable status string.

        Returns:
            Status string
        """
        status = self.get_status()
        if status == AppStatus.RUNNING:
            return "Running"
        elif status == AppStatus.STOPPED:
            return "Stopped"
        elif status == AppStatus.PROCESSING:
            return "Processing..."
        elif status == AppStatus.ERROR:
            return "Error"
        return "Unknown"

    def get_status_info(self) -> dict:
        """
        Get comprehensive status information.

        Returns:
            Dictionary with status information
        """
        with self._lock:
            return {
                "status": self._status.value,
                "status_string": self.get_status_string(),
                "is_running": self._status == AppStatus.RUNNING,
                "last_execution_time": (
                    self._last_execution_time.isoformat()
                    if self._last_execution_time
                    else None
                ),
                "last_entry_preview": self._last_entry_preview,
                "last_entry_timestamp": (
                    self._last_entry_timestamp.isoformat()
                    if self._last_entry_timestamp
                    else None
                ),
                "error_count": self._error_count,
                "next_execution_time": (
                    self._next_execution_time.isoformat()
                    if self._next_execution_time
                    else None
                ),
            }


# Global instance
_status_service: Optional[StatusService] = None


def get_status_service() -> StatusService:
    """
    Get global status service instance.

    Returns:
        StatusService instance
    """
    global _status_service
    if _status_service is None:
        _status_service = StatusService()
    return _status_service

