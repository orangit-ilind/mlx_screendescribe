"""Log viewer window for menu bar app."""

import rumps
from typing import Any

from src.logging_service import get_logging_service, LogLevel


def show_log_viewer(app: Any):
    """Show log viewer window."""
    logger = get_logging_service()

    # Get recent log entries
    entries = logger.get_recent(100)
    
    if not entries:
        rumps.alert("No log entries available.", "Log Viewer")
        return

    # Format log entries
    log_text = "\n".join(str(entry) for entry in entries)

    # Create window to display logs
    # Note: rumps doesn't have a built-in text view, so we'll use a simple window
    # For a better experience, you might want to use PyObjC's NSTextView
    
    # Show logs in a window (rumps limitation: can't easily show multi-line text)
    # We'll create a simple display
    response = rumps.Window(
        message="Recent Log Entries (last 100):\n\n" + log_text[-2000:],  # Limit to last 2000 chars
        default_text="",
        title="Log Viewer",
        ok="Close",
        cancel=None,
        dimensions=(800, 600),
    ).run()

    # For a better log viewer, we could:
    # 1. Use PyObjC to create a proper NSTextView window
    # 2. Save logs to a file and open it in TextEdit
    # 3. Use a web view with HTML formatting
    
    # Alternative: Open logs in TextEdit
    import tempfile
    import subprocess
    import os
    
    # Create temporary file with logs
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(log_text)
        temp_path = f.name
    
    try:
        # Open in TextEdit
        subprocess.run(['open', '-a', 'TextEdit', temp_path], check=False)
    except Exception as e:
        logger.error(f"Failed to open log viewer: {e}")
        # Fallback: show in alert (truncated)
        rumps.alert(
            "Recent Log Entries:\n\n" + log_text[-500:],
            "Log Viewer"
        )


def show_log_viewer_advanced(app: Any):
    """Show advanced log viewer with filtering."""
    logger = get_logging_service()

    # Get all entries
    all_entries = logger.get_recent(100)
    
    # Filter options
    response = rumps.alert(
        "Log Viewer Options",
        "Choose log level to view:",
        "All",
        "Errors Only",
        "Warnings and Errors",
        "Cancel"
    )

    if response == 1:  # All
        entries = all_entries
    elif response == 2:  # Errors Only
        entries = logger.get_entries(level=LogLevel.ERROR)
    elif response == 3:  # Warnings and Errors
        error_entries = logger.get_entries(level=LogLevel.ERROR)
        warning_entries = logger.get_entries(level=LogLevel.WARNING)
        entries = sorted(error_entries + warning_entries, key=lambda e: e.timestamp)
    else:
        return

    if not entries:
        rumps.alert("No log entries match the selected filter.", "Log Viewer")
        return

    # Format and display
    log_text = "\n".join(str(entry) for entry in entries)
    
    # Open in TextEdit
    import tempfile
    import subprocess
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(log_text)
        temp_path = f.name
    
    try:
        subprocess.run(['open', '-a', 'TextEdit', temp_path], check=False)
    except Exception as e:
        logger.error(f"Failed to open log viewer: {e}")

