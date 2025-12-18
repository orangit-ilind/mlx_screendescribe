# Agents / Services

This document describes the main services and components (agents) that make up the MLX Screendescribe application.

## Core Services

### ScreenshotService
**Location:** `src/screenshot.py`

Captures screenshots from the macOS screen using the `screencapture` command.

**Responsibilities:**
- Capture screenshots to a temporary file
- Handle screenshot capture errors
- Return PIL Image objects for processing

**Key Methods:**
- `capture() -> Image.Image` - Captures a screenshot and returns it as a PIL Image

---

### ModelInferenceService
**Location:** `src/model_inference.py`

Handles vision-language model inference using MLX framework.

**Responsibilities:**
- Load MLX-compatible vision-language models
- Find models in various locations (LM Studio cache, project `.models` directory)
- Download models from Hugging Face if not found locally
- Generate descriptions from screenshots using the model
- Handle model loading and inference errors

**Key Methods:**
- `__init__(model_path: Optional[str] = None)` - Initialize with optional model path
- `describe_image(image: Image.Image, prompt: Optional[str] = None) -> str` - Generate description from image

**Model Path Resolution:**
1. Checks `~/.lmstudio/models/{MODEL_NAME}` (legacy location)
2. Checks `.models/{MODEL_NAME_ONLY}` (project directory)
3. Downloads from Hugging Face if not found

---

### TrackingService
**Location:** `src/tracking.py`

Manages time tracking log file entries.

**Responsibilities:**
- Append entries to the tracking file
- Format entries with timestamps
- Handle file I/O errors

**Key Methods:**
- `append_entry(description: str) -> None` - Append a new entry to the tracking file

**Output Format:**
```
YYYY.MM.DD HH:MM {description}
```

---

### Scheduler
**Location:** `src/scheduler.py`

Manages scheduled execution of tasks at regular intervals.

**Responsibilities:**
- Schedule tasks to run at specified intervals
- Start and stop scheduled execution
- Handle task execution in background threads

**Key Methods:**
- `__init__(task: Callable, interval: int)` - Initialize with task and interval
- `start() -> None` - Start the scheduler
- `stop() -> None` - Stop the scheduler
- `is_running() -> bool` - Check if scheduler is running

---

## Support Services

### LoggingService
**Location:** `src/logging_service.py`

Centralized logging service for the application.

**Responsibilities:**
- Provide consistent logging interface
- Manage log file location (`~/Library/Logs/com.screendescribe/`)
- Handle log rotation and formatting
- Support different log levels

**Key Methods:**
- `get_logging_service() -> Logger` - Get the global logger instance

---

### StatusService
**Location:** `src/status_service.py`

Manages application status and state.

**Responsibilities:**
- Track application status (RUNNING, PROCESSING, ERROR, STOPPED)
- Store last execution timestamp
- Store last entry preview
- Track error counts

**Key Methods:**
- `get_status() -> AppStatus` - Get current status
- `set_status(status: AppStatus) -> None` - Update status
- `get_status_string() -> str` - Get human-readable status
- `get_last_entry_preview() -> Optional[str]` - Get preview of last entry

**Status Values:**
- `RUNNING` - Application is running normally
- `PROCESSING` - Currently executing workflow
- `ERROR` - Error occurred during execution
- `STOPPED` - Application is stopped

---

## UI Components

### ScreendescribeMenuBarApp
**Location:** `menu_bar.py`

Main menu bar application using rumps framework.

**Responsibilities:**
- Display menu bar icon and menu
- Handle user interactions (capture now, view logs, preferences, quit)
- Coordinate services (screenshot, model, tracking, scheduler)
- Update menu status display
- Show notifications

**Key Methods:**
- `_execute_workflow() -> None` - Execute the complete workflow
- `_on_capture_now(_)` - Handle manual capture trigger
- `_on_view_logs(_)` - Show log viewer window
- `_on_preferences(_)` - Open config.py in TextEdit
- `_update_menu_status(_)` - Update menu status items

---

### LogViewer
**Location:** `src/log_viewer.py`

Displays application logs in a window.

**Responsibilities:**
- Show log file contents
- Display logs in a readable format
- Allow users to view recent log entries

---

## Application Entry Points

### bootstrap.py
**Purpose:** Bootstrap script for launching the menu bar application.

**Responsibilities:**
- Set environment variables (TOKENIZERS_PARALLELISM)
- Launch menu bar application

**Flow:**
1. Set environment variables (TOKENIZERS_PARALLELISM)
2. Add src to Python path
3. Launch menu_bar.py

---

### main.py
**Purpose:** CLI entry point for command-line usage.

**Responsibilities:**
- Parse command-line arguments
- Run application in different modes (once, scheduled, GUI)
- Handle CLI workflow execution

**Usage:**
Recommended: Use `uv` package manager to run the script:
```bash
uv run main.py [arguments]
```

**Examples:**
- `uv run main.py --once` - Run workflow once and exit
- `uv run main.py --scheduled` - Run continuously at intervals
- `uv run main.py --scheduled --interval 300` - Run scheduled with custom interval
- `uv run main.py --gui` - Launch menu bar GUI

Alternatively, run directly with Python:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py [arguments]
```

**Modes:**
- `--once` - Run workflow once and exit
- `--scheduled` - Run continuously at intervals
- `--gui` - Launch menu bar GUI
- `--interval` - Set interval for scheduled mode

---

## Workflow

The main workflow executed by the application:

1. **Screenshot Capture** (ScreenshotService)
   - Captures current screen to temporary file
   - Returns PIL Image object

2. **Model Inference** (ModelInferenceService)
   - Loads model if not already loaded
   - Processes image with vision-language model
   - Generates description text

3. **Tracking** (TrackingService)
   - Appends entry to tracking file with timestamp
   - Formats entry according to template

4. **Status Update** (StatusService)
   - Updates application status
   - Stores last entry preview
   - Updates last execution timestamp

---

## Configuration

Configuration is managed through `config.py`:

- `MODEL_NAME` - Hugging Face model repository ID
- `MODEL_PATH` - Local model directory (`.models/{MODEL_NAME_ONLY}`)
- `SCREENSHOT_INTERVAL_SECONDS` - Interval between captures
- `OUTPUT_FILE` - Tracking file path
- `PROMPT_TEXT` - Prompt for model inference
- `TEMPERATURE`, `MAX_TOKENS`, `FREQUENCY_PENALTY` - Model parameters

---

## Dependencies

- **mlx** - MLX framework for Apple Silicon
- **mlx-vlm** - Vision-language model support
- **rumps** - macOS menu bar framework
- **Pillow** - Image processing
- **huggingface_hub** - Model downloading

