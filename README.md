# MLX Screendescribe

A Python application that automatically captures screenshots, performs vision-language model inference using MLX, and logs time tracking entries to `~/Desktop/TimeTracking.txt`.

## Features

- Automatic screenshot capture using macOS `screencapture` command
- Local vision-language model inference using MLX framework (optimized for Apple Silicon)
- Scheduled execution every 5 minutes (configurable)
- Manual execution mode for one-time runs
- Time tracking log file on Desktop

## Requirements

- macOS (for `screencapture` command)
- Python 3.8 or higher
- Apple Silicon Mac (M1/M2/M3) for optimal MLX performance
- Screen Recording permission (will be prompted on first run)
- MLX-compatible Qwen3-VL-8B model

## Installation

1. **Install Python dependencies:**

   **Recommended: Use `uv` package manager:** ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))
   ```bash
   uv sync
   ```

   **Alternative: Use pip with virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   This will install:
   - `mlx` - Core MLX framework
   - `mlx-vlm` - Vision-language model support for MLX
   - `Pillow` - Image processing

2. **Set up the model:**

   The application will look for the model in:
   - LM Studio location: `~/.lmstudio/models/{MODEL_NAME}` (for backward compatibility)
   - Project location: `.models/{MODEL_NAME_ONLY}` (recommended)

   **Important:** LM Studio models (GGUF format) are not directly compatible with MLX. You need an MLX-compatible version with [Vision capabilities](https://www.nvidia.com/en-us/glossary/vision-language-models/)

   **Option A: Download MLX-compatible model to project directory (Recommended)**
   
   ```bash
   git lfs install
   git clone https://huggingface.co/lmstudio-community/Qwen3-VL-8B-Instruct-MLX-4bit .models/Qwen3-VL-8B-Instruct-MLX-4bit
   ```

   **Option B: Use LM Studio to download**
   
   Use LM Studio to download the MLX-compatible model:
   1. Open LM Studio
   2. Search for and download `lmstudio-community/Qwen3-VL-8B-Instruct-MLX-4bit`
   3. The model will be saved to `~/.lmstudio/models/Qwen3-VL-8B-Instruct-MLX-4bit`
   
   **Note:** LM Studio typically downloads GGUF format models. Make sure to download the MLX-compatible version, or use Option C to convert after downloading.


   **Option C: Convert your existing model**

   Use the MLX conversion tool on Hugging Face Spaces to convert your existing model to MLX format:
   
   Visit: [https://huggingface.co/spaces/mlx-community/mlx-my-repo](https://huggingface.co/spaces/mlx-community/mlx-my-repo)
   
   This Space allows you to convert models from various formats (GGUF, PyTorch, etc.) to MLX-compatible format. After conversion, download the model and place it in the project `.models/` directory.

   

3. **Grant Screen Recording permission:**

   On first run, macOS will prompt you to grant Screen Recording permission. Go to:
   - System Settings → Privacy & Security → Screen Recording
   - Enable the permission for Terminal (or your Python environment)

## Usage

### Run Once

Execute the workflow once and exit:

**Recommended:**
```bash
uv run main.py --once
```

**Alternative:**
```bash
python3 main.py --once
```

### Run Scheduled (Default)

Run continuously, executing every 5 minutes:

**Recommended:**
```bash
uv run main.py --scheduled
```

**Alternative:**
```bash
python3 main.py --scheduled
```

### Custom Interval

Run scheduled with a custom interval (in seconds):

**Recommended:**
```bash
uv run main.py --scheduled --interval 600  # Every 10 minutes
```

**Alternative:**
```bash
python3 main.py --scheduled --interval 600  # Every 10 minutes
```

### Stop Scheduled Execution

Press `Ctrl+C` to stop the scheduler gracefully.

## Configuration

Edit `config.py` to customize:

- **Model path**: `MODEL_PATH`
- **Screenshot interval**: `SCREENSHOT_INTERVAL_SECONDS` (default: 300 = 5 minutes)
- **Output file**: `OUTPUT_FILE` (default: `~/Desktop/TimeTracking.txt`)
- **Prompt text**: `PROMPT_TEXT` (customize the description prompt)
- **Model parameters**: `TEMPERATURE`, `MAX_TOKENS`, `FREQUENCY_PENALTY`

## Output Format

Entries are logged to `~/Desktop/TimeTracking.txt` in the format:

```
YYYY.MM.DD HH:MM {description}
```

Example:
```
2024.01.15 14:30 Client: Acme Corp − Working on API integration. Reviewing authentication endpoints and testing connection flow.
```

## Project Structure

```
mlx_screendescribe/
├── README.md              # This file
├── Agents.md              # Service and component documentation
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration (for uv)
├── config.py              # Configuration constants
├── main.py                # CLI entry point
├── menu_bar.py            # Menu bar GUI application
├── bootstrap.py           # Bootstrap script for menu bar app
├── .models/               # Model storage directory (created on first use)
│   └── Qwen3-VL-8B-Instruct-MLX-4bit/  # MLX model files
└── src/
    ├── __init__.py
    ├── screenshot.py      # Screenshot capture service
    ├── model_inference.py # MLX model inference service
    ├── tracking.py         # File logging service
    ├── scheduler.py       # Timer-based execution scheduler
    ├── logging_service.py # Centralized logging service
    ├── status_service.py  # Application status management
    ├── log_viewer.py      # Log viewer UI component
    └── progress_window.py # Progress window UI component
```

## Troubleshooting

### Model Loading Errors

**Error:** "Failed to load model from ... The model may not be in MLX format"

**Solution:** Download the MLX-compatible version from Hugging Face to the project directory:
```bash
git lfs install
git clone https://huggingface.co/lmstudio-community/Qwen3-VL-8B-Instruct-MLX-4bit .models/Qwen3-VL-8B-Instruct-MLX-4bit
```

### Screenshot Permission Denied

**Error:** "Failed to capture screenshot"

**Solution:** 
1. Go to System Settings → Privacy & Security → Screen Recording
2. Enable permission for Terminal (or your Python environment)
3. Restart the application

```
## Notes

- The app runs in the foreground (use `nohup` or `screen` for background execution)
- Screenshots are temporarily saved and cleaned up after processing
- The app continues running even if individual executions fail
- Errors are logged to console with full tracebacks

## License

MIT License

