"""Screenshot capture module using macOS screencapture command."""

import os
import subprocess
import time
from PIL import Image
from typing import Optional

from config import SCREENSHOT_TEMP_FILE
from src.logging_service import get_logging_service


class ScreenshotService:
    """Service for capturing screenshots on macOS."""

    def __init__(self, temp_file: Optional[str] = None):
        """
        Initialize screenshot service.

        Args:
            temp_file: Optional path for temporary screenshot file.
                      Defaults to config.SCREENSHOT_TEMP_FILE
        """
        self.temp_file = temp_file or SCREENSHOT_TEMP_FILE
        self.logger = get_logging_service()

    def capture(self) -> Image.Image:
        """
        Capture a screenshot and return as PIL Image.

        Returns:
            PIL Image object

        Raises:
            RuntimeError: If screenshot capture fails
            FileNotFoundError: If screenshot file was not created
        """
        try:
            # Wait 3 seconds before capturing to allow UI to stabilize
            time.sleep(3)
            
            # Use screencapture command (native macOS tool)
            # -x flag prevents the sound effect
            result = subprocess.run(
                ["screencapture", "-x", self.temp_file],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"Failed to capture screenshot: {result.stderr}"
                )

            # Verify file was created
            if not os.path.exists(self.temp_file):
                raise FileNotFoundError(
                    f"Screenshot file was not created at {self.temp_file}"
                )

            # Load image with PIL
            image = Image.open(self.temp_file)

            # Clean up temporary file
            try:
                os.remove(self.temp_file)
            except OSError:
                # Ignore cleanup errors
                pass

            return image

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Screenshot capture failed: {e}") from e
        except Exception as e:
            # Clean up on any error
            try:
                if os.path.exists(self.temp_file):
                    os.remove(self.temp_file)
            except OSError:
                pass
            raise

