"""Time tracking file logging module."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import threading

from config import OUTPUT_FILE
from src.logging_service import get_logging_service


class TrackingService:
    """Service for logging time tracking entries to file."""

    def __init__(self, output_file: Optional[str] = None):
        """
        Initialize tracking service.

        Args:
            output_file: Optional path to output file.
                        Defaults to config.OUTPUT_FILE
        """
        self.output_file = output_file or OUTPUT_FILE
        self._lock = threading.Lock()
        self.logger = get_logging_service()

    def append_entry(self, description: str) -> None:
        """
        Append a time tracking entry to the output file.

        Args:
            description: Description text to log

        Raises:
            IOError: If file writing fails
        """
        # Format timestamp: YYYY.MM.DD HH:MM
        timestamp = datetime.now().strftime("%Y.%m.%d %H:%M")

        # Format entry: timestamp description
        entry = f"{timestamp} {description}\n"

        # Thread-safe file writing
        with self._lock:
            try:
                # Ensure directory exists
                output_path = Path(self.output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Append to file
                with open(self.output_file, "a", encoding="utf-8") as f:
                    f.write(entry)

                self.logger.info(f"Logged entry to {self.output_file}")

            except IOError as e:
                raise IOError(
                    f"Failed to write to tracking file {self.output_file}: {e}"
                ) from e

