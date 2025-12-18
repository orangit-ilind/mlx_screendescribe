"""Progress window for package installation."""

import rumps
from typing import Optional, Callable


class ProgressWindow:
    """Simple progress window for package installation."""

    def __init__(self, title: str = "Installing Packages"):
        """
        Initialize progress window.

        Args:
            title: Window title
        """
        self.title = title
        self.current_text = "Initializing..."
        self.percentage = 0.0
        self._cancelled = False

    def update(self, text: str, percentage: float) -> None:
        """
        Update progress.

        Args:
            text: Progress text
            percentage: Progress percentage (0-100)
        """
        self.current_text = text
        self.percentage = max(0.0, min(100.0, percentage))

    def show(self) -> None:
        """Show progress window (non-blocking)."""
        # For rumps, we'll use notifications and menu bar updates
        # A full progress window would require PyObjC
        pass

    def cancel(self) -> None:
        """Mark as cancelled."""
        self._cancelled = True

    def is_cancelled(self) -> bool:
        """Check if cancelled."""
        return self._cancelled


def show_progress_notification(text: str, percentage: float) -> None:
    """
    Show progress notification.

    Args:
        text: Progress text
        percentage: Progress percentage (0-100)
    """
    # Show notification for major milestones
    if percentage >= 100.0:
        rumps.notification(
            title="Screendescribe",
            subtitle="Installation Complete",
            message="Packages have been installed successfully.",
        )
    elif percentage == 0.0:
        rumps.notification(
            title="Screendescribe",
            subtitle="Installing Packages",
            message="Downloading and installing required packages...",
        )

