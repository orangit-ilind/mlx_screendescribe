"""Logging service for UI-friendly logging with in-memory storage."""

import logging
import sys
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogEntry:
    """Represents a single log entry."""

    def __init__(
        self, level: LogLevel, message: str, timestamp: Optional[datetime] = None
    ):
        """
        Initialize log entry.

        Args:
            level: Log level
            message: Log message
            timestamp: Optional timestamp (defaults to now)
        """
        self.level = level
        self.message = message
        self.timestamp = timestamp or datetime.now()

    def __str__(self) -> str:
        """Format log entry as string."""
        time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{time_str}] [{self.level.value}] {self.message}"

    def to_dict(self) -> dict:
        """Convert log entry to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
        }


class LoggingService:
    """Service for UI-friendly logging with in-memory storage."""

    def __init__(self, max_entries: int = 100):
        """
        Initialize logging service.

        Args:
            max_entries: Maximum number of log entries to keep in memory
        """
        self.max_entries = max_entries
        self._entries: List[LogEntry] = []
        self._lock = False  # Simple lock for thread safety (can be enhanced with threading.Lock if needed)
        self._logging_directly = False  # Flag to prevent recursion

        # Set up Python logging for console output only (not forwarding back to service)
        self._logger = logging.getLogger("screendescribe")
        self._logger.setLevel(logging.DEBUG)
        # Prevent propagation to root logger to avoid duplicate messages
        self._logger.propagate = False

        # Only log to console, don't create circular handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)

    def log(self, level: LogLevel, message: str) -> None:
        """
        Log a message.

        Args:
            level: Log level
            message: Log message
        """
        # Prevent recursion
        if self._logging_directly:
            return

        entry = LogEntry(level, message)
        self._entries.append(entry)

        # Keep only the most recent entries
        if len(self._entries) > self.max_entries:
            self._entries.pop(0)

        # Also log via Python logging for console output (but prevent recursion)
        self._logging_directly = True
        try:
            if level == LogLevel.DEBUG:
                self._logger.debug(message)
            elif level == LogLevel.INFO:
                self._logger.info(message)
            elif level == LogLevel.WARNING:
                self._logger.warning(message)
            elif level == LogLevel.ERROR:
                self._logger.error(message)
        finally:
            self._logging_directly = False

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.log(LogLevel.DEBUG, message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.log(LogLevel.INFO, message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.log(LogLevel.WARNING, message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.log(LogLevel.ERROR, message)

    def get_entries(
        self,
        level: Optional[LogLevel] = None,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """
        Get log entries.

        Args:
            level: Optional filter by log level
            limit: Optional limit on number of entries to return

        Returns:
            List of log entries
        """
        entries = self._entries

        # Filter by level if specified
        if level:
            entries = [e for e in entries if e.level == level]

        # Apply limit if specified
        if limit:
            entries = entries[-limit:]

        return entries

    def get_recent(self, count: int = 100) -> List[LogEntry]:
        """
        Get recent log entries.

        Args:
            count: Number of entries to return

        Returns:
            List of recent log entries
        """
        return self.get_entries(limit=count)

    def get_formatted_logs(self, level: Optional[LogLevel] = None) -> str:
        """
        Get formatted log entries as string.

        Args:
            level: Optional filter by log level

        Returns:
            Formatted log string
        """
        entries = self.get_entries(level=level)
        return "\n".join(str(entry) for entry in entries)

    def clear(self) -> None:
        """Clear all log entries."""
        self._entries.clear()

    def get_logger(self) -> logging.Logger:
        """
        Get Python logger instance.

        Returns:
            Python logger
        """
        return self._logger


# Global instance
_logging_service: Optional[LoggingService] = None


def get_logging_service() -> LoggingService:
    """
    Get global logging service instance.

    Returns:
        LoggingService instance
    """
    global _logging_service
    if _logging_service is None:
        _logging_service = LoggingService()
    return _logging_service
