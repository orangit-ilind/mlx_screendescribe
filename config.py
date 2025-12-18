"""Configuration constants for MLX Screendescribe."""

import os
from pathlib import Path

# Model configuration
# MODEL_NAME uses Hugging Face repository ID format: "organization/model-name"
MODEL_NAME = "lmstudio-community/Qwen3-VL-8B-Instruct-MLX-4bit"

# Screenshot configuration
SCREENSHOT_INTERVAL_SECONDS = 1800  # 30 minutes (30 * 60 seconds)
SCREENSHOT_TEMP_FILE = os.path.expanduser("~/Desktop/screenshot.png")

# Output file configuration
OUTPUT_FILE = os.path.expanduser("~/Desktop/TimeTracking.txt")

# Prompt text
# vscode window title hack, to make it easier to identify projects ~/clients/clientname/projectname/ will show up in title
# "window.title": "${activeEditorLong}${separator}${rootName}${separator}${profileName}",
PROMPT_TEXT = (
    "Describe whats on the screenshot for personal time tracking purposes, "
    'if you see "clients" on the window title describe to whom should the billing go to '
    "after the forwarding slash. The summary should be 500 characters long maximum in the "
    "following format: Client: {clientname} − {summaryofwhatishappening} in two sentences. "
    "If you see a chat window, social media, passwords, secrets or password manager window don't mention them."
)

# Extract just the model name (after the slash) for file paths
MODEL_NAME_ONLY = MODEL_NAME.split("/")[-1]

# Model path - relative to project root (where main.py resides)
# Note: "~/.lmstudio/models/{MODEL_NAME}" is looked at first for backward compatibility
MODEL_PATH = str(Path(__file__).parent / ".models" / MODEL_NAME_ONLY)

# Model inference parameters
TEMPERATURE = 0.9
MAX_TOKENS = 500
FREQUENCY_PENALTY = 1.1
