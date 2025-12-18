#!/usr/bin/env python3
"""Bootstrap script for launching the menu bar application."""

import os

# Set TOKENIZERS_PARALLELISM to false to prevent warnings and deadlocks
# when using threading/forking (required by HuggingFace tokenizers)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entry point for bootstrap."""
    # Launch the menu bar app
    from menu_bar import main as menu_bar_main

    menu_bar_main()


if __name__ == "__main__":
    main()
