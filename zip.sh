#!/bin/bash
# Create a zip archive of the project excluding files in .gitignore

set -e

# Get the project directory name (parent directory)
PROJECT_NAME="mlx_screendescribe"
ZIP_FILE="${PROJECT_NAME}.zip"

# Remove existing zip file if it exists
if [ -f "$ZIP_FILE" ]; then
    echo "Removing existing $ZIP_FILE..."
    rm "$ZIP_FILE"
fi

# Check if we're in a git repository
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Using git archive (respects .gitignore)..."
    # Use git archive which automatically respects .gitignore
    git archive -o "$ZIP_FILE" HEAD
    echo "Created $ZIP_FILE using git archive"
else
    echo "Not a git repository, using zip with .gitignore exclusions..."
    
    # Use zip with exclusions based on .gitignore
    # Common patterns from .gitignore: __pycache__/, *.pyc, .venv, .models, etc.
    zip -r "$ZIP_FILE" . \
        -x "__pycache__/*" \
        -x "*.pyc" \
        -x "*.pyo" \
        -x "*.pyd" \
        -x ".venv/*" \
        -x ".models/*" \
        -x "*.egg-info/*" \
        -x "wheels/*" \
        -x "$ZIP_FILE" \
        -x ".git/*" \
        -x ".DS_Store" \
        -x "zip.sh" \
        -x "*~" \
        > /dev/null 2>&1 || {
        echo "Warning: Some files may not have been excluded properly"
        echo "Consider using git archive for better .gitignore support"
    }
    echo "Created $ZIP_FILE using zip with exclusions"
fi

echo "Done! Archive created: $ZIP_FILE"

