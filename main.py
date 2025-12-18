#!/usr/bin/env python3
"""Main entry point for MLX Screendescribe.

Usage:
    Recommended: Use uv package manager to run the script:
        uv run main.py [arguments]
    
    Examples:
        uv run main.py --once
        uv run main.py --scheduled
        uv run main.py --scheduled --interval 300
        uv run main.py --gui
    
    Alternatively, run directly with Python:
        python3 main.py [arguments]
"""

import argparse
import signal
import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.screenshot import ScreenshotService
from src.model_inference import ModelInferenceService
from src.tracking import TrackingService
from src.scheduler import Scheduler
from src.logging_service import get_logging_service


class ScreendescribeApp:
    """Main application class."""

    def __init__(self):
        """Initialize the application."""
        self.screenshot_service = ScreenshotService()
        self.model_service = ModelInferenceService()
        self.tracking_service = TrackingService()
        self.scheduler: Optional[Scheduler] = None
        self._shutdown_requested = False
        self.logger = get_logging_service()

    def execute_workflow(self) -> None:
        """Execute the complete workflow: screenshot -> inference -> logging."""
        try:
            self.logger.info("=" * 60)
            self.logger.info("Starting workflow execution...")

            # Step 1: Capture screenshot
            self.logger.info("Step 1: Capturing screenshot...")
            image = self.screenshot_service.capture()
            self.logger.info("✓ Screenshot captured successfully")

            # Step 2: Run model inference
            self.logger.info("Step 2: Running model inference...")
            description = self.model_service.describe_image(image)
            self.logger.info(f"✓ Inference completed: {description[:100]}...")

            # Step 3: Log to tracking file
            self.logger.info("Step 3: Logging to tracking file...")
            self.tracking_service.append_entry(description)
            self.logger.info("✓ Entry logged successfully")

            self.logger.info("Workflow completed successfully!")
            self.logger.info("=" * 60)

        except Exception as e:
            self.logger.error(f"Error in workflow execution: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

    def run_scheduled(self, interval: Optional[int] = None) -> None:
        """Run the application in scheduled mode."""
        self.logger.info("Starting in scheduled mode...")
        self.logger.info("Press Ctrl+C to stop")

        # Create scheduler
        self.scheduler = Scheduler(
            task=self.execute_workflow,
            interval=interval,
        )

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start scheduler
        self.scheduler.start()

        # Keep main thread alive
        try:
            while self.scheduler.is_running() and not self._shutdown_requested:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self._shutdown()

    def run_once(self) -> None:
        """Run the workflow once and exit."""
        self.logger.info("Running workflow once...")
        self.execute_workflow()
        self.logger.info("Done!")

    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals."""
        self.logger.info(f"\nReceived signal {signum}, shutting down...")
        self._shutdown_requested = True
        self._shutdown()

    def _shutdown(self) -> None:
        """Shutdown the application gracefully."""
        if self.scheduler:
            self.scheduler.stop()
        self.logger.info("Application stopped.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MLX Screendescribe - Vision-language model inference for time tracking"
    )
    parser.add_argument(
        "--scheduled",
        action="store_true",
        help="Run in scheduled mode (every 5 minutes by default)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit",
    )
    parser.add_argument(
        "--interval",
        type=int,
        help="Interval in seconds for scheduled mode (default: 300)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch menu bar GUI application",
    )

    args = parser.parse_args()

    # Launch GUI if requested
    if args.gui:
        from menu_bar import main as menu_bar_main
        menu_bar_main()
        return

    # Default to once if no mode specified
    if not args.scheduled and not args.once:
        args.once = True

    app = ScreendescribeApp()

    if args.scheduled:
        app.run_scheduled(interval=args.interval)
    else:
        app.run_once()


if __name__ == "__main__":
    main()

