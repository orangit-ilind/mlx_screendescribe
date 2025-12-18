#!/usr/bin/env python3
"""Menu bar application entry point for MLX Screendescribe."""

import os

# Set TOKENIZERS_PARALLELISM to false to prevent warnings and deadlocks
# when using threading/forking (required by HuggingFace tokenizers)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import subprocess
import threading
import atexit
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import rumps
from rumps import notification

from src.screenshot import ScreenshotService
from src.model_inference import ModelInferenceService
from src.tracking import TrackingService
from src.scheduler import Scheduler
from src.logging_service import get_logging_service
from src.status_service import get_status_service, AppStatus
from config import OUTPUT_FILE
import config


class ScreendescribeMenuBarApp(rumps.App):
    """Menu bar application for Screendescribe."""

    def __init__(self):
        """Initialize the menu bar app."""
        super().__init__("Screendescribe", "📸")
        self.logger = get_logging_service()
        self.status_service = get_status_service()

        # Initialize services (using config values directly)
        self.screenshot_service = ScreenshotService()
        self.model_service = ModelInferenceService()
        # Use config for output file
        self.tracking_service = TrackingService(output_file=OUTPUT_FILE)
        self.scheduler: Optional[Scheduler] = None

        # Build menu
        self._build_menu()

        # Set up status update timer
        self._status_timer = rumps.Timer(
            self._update_menu_status, 5
        )  # Update every 5 seconds
        self._status_timer.start()

        # Start scheduler by default
        self.status_service.set_status(AppStatus.RUNNING)

        # Register cleanup function to run on exit
        atexit.register(self._cleanup)

        self.logger.info("Menu bar app initialized")

    def _build_menu(self):
        """Build the menu structure."""
        # Status section
        self.status_item = rumps.MenuItem("Status: Stopped", callback=None)
        self.last_entry_item = rumps.MenuItem("Last Entry: None", callback=None)
        self.menu = [
            self.status_item,
            self.last_entry_item,
            None,  # Separator
            rumps.MenuItem("Capture Now", callback=self._on_capture_now),
            rumps.MenuItem("View Logs...", callback=self._on_view_logs),
            None,  # Separator
            rumps.MenuItem("Preferences...", callback=self._on_preferences),
        ]

    def _update_menu_status(self, _=None):
        """Update menu status items."""
        status_str = self.status_service.get_status_string()

        # Update status item
        self.status_item.title = f"Status: {status_str}"

        # Update last entry item
        last_entry_preview = self.status_service.get_last_entry_preview()
        last_entry_timestamp = self.status_service.get_last_entry_timestamp()

        if last_entry_preview and last_entry_timestamp:
            time_str = last_entry_timestamp.strftime("%H:%M")
            preview = (
                last_entry_preview[:50] + "..."
                if len(last_entry_preview) > 50
                else last_entry_preview
            )
            self.last_entry_item.title = f"Last Entry ({time_str}): {preview}"
        else:
            self.last_entry_item.title = "Last Entry: None"

    @rumps.timer(1)  # Check every second
    def _check_scheduler(self, _):
        """Check if scheduler needs to be started/stopped."""
        status = self.status_service.get_status()
        is_running = status == AppStatus.RUNNING

        if is_running and not self.scheduler:
            # Start scheduler
            self.scheduler = Scheduler(
                task=self._execute_workflow,
                interval=config.SCREENSHOT_INTERVAL_SECONDS,
            )
            self.scheduler.start()
            self.logger.info("Scheduler started from menu bar app")
        elif not is_running and self.scheduler and status != AppStatus.PROCESSING:
            # Stop scheduler (but not if currently processing)
            self.scheduler.stop()
            self.scheduler = None
            self.logger.info("Scheduler stopped from menu bar app")

    def _execute_workflow(self) -> None:
        """Execute the complete workflow: screenshot -> inference -> logging."""
        self.status_service.set_status(AppStatus.PROCESSING)
        self.status_service.set_last_execution()

        try:
            self.logger.info("Starting workflow execution...")

            # Step 1: Capture screenshot
            self.logger.info("Capturing screenshot...")
            image = self.screenshot_service.capture()
            self.logger.info("Screenshot captured successfully")

            # Step 2: Run model inference
            self.logger.info("Running model inference...")
            description = self.model_service.describe_image(image)
            self.logger.info(f"Inference completed: {description[:100]}...")

            # Step 3: Log to tracking file
            self.logger.info("Logging to tracking file...")
            self.tracking_service.append_entry(description)
            self.logger.info("Entry logged successfully")

            # Update status
            self.status_service.set_last_entry(description)
            self.status_service.set_status(AppStatus.RUNNING)
            self.status_service.reset_error_count()

            # Show notification
            notification(
                title="Screendescribe",
                subtitle="Entry logged successfully",
                message=description[:100] + "..."
                if len(description) > 100
                else description,
            )

            self.logger.info("Workflow completed successfully!")

        except Exception as e:
            self.logger.error(f"Error in workflow execution: {e}")
            import traceback

            self.logger.error(traceback.format_exc())

            # Update status
            self.status_service.set_status(AppStatus.ERROR)
            self.status_service.increment_error_count()

            # Show error notification
            notification(
                title="Screendescribe Error",
                subtitle="Workflow execution failed",
                message=str(e)[:100],
            )

    def _on_capture_now(self, _):
        """Handle manual capture trigger."""
        if self.status_service.get_status() == AppStatus.PROCESSING:
            notification(
                title="Screendescribe",
                subtitle="Already processing",
                message="Please wait for current capture to complete.",
            )
            return

        self.logger.info("Manual capture triggered")
        # Execute in background thread
        thread = threading.Thread(target=self._execute_workflow, daemon=True)
        thread.start()

    def _on_view_logs(self, _):
        """Handle view logs menu item."""
        from src.log_viewer import show_log_viewer

        show_log_viewer(self)

    def _on_preferences(self, _):
        """Handle preferences menu item - opens config.py in TextEdit."""
        try:
            # Get the path to config.py (in the same directory as menu_bar.py)
            config_path = Path(__file__).parent / "config.py"

            # Open config.py in TextEdit using macOS 'open' command
            subprocess.run(
                ["open", "-a", "TextEdit", str(config_path)],
                check=True,
            )
            self.logger.info(f"Opened config.py in TextEdit: {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to open config.py in TextEdit: {e}")
            notification(
                title="Screendescribe",
                subtitle="Error",
                message=f"Failed to open config.py: {e}",
            )

    def _cleanup(self):
        """Cleanup before quitting."""
        self.logger.info("Cleaning up before quit...")
        if self.scheduler:
            self.scheduler.stop()


def main():
    """Main entry point for menu bar app."""
    app = ScreendescribeMenuBarApp()
    app.run()


if __name__ == "__main__":
    main()
