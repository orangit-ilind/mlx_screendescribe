"""MLX model inference module for vision-language models."""

import os
from typing import Optional
from PIL import Image

from config import (
    MODEL_NAME,
    MODEL_PATH,
    PROMPT_TEXT,
)
from src.logging_service import get_logging_service


def find_model_path() -> str:
    """
    Find the model path by checking LM Studio location first, then project location.
    Returns the path where the model exists or should be downloaded.

    Returns:
        Path to the model directory
    """
    # LM Studio location (check first)
    lmstudio_path = os.path.expanduser(f"~/.lmstudio/models/{MODEL_NAME}")
    # Project path (relative to project root)
    project_path = MODEL_PATH

    logger = get_logging_service()

    # Check LM Studio location first
    lmstudio_config_path = os.path.join(lmstudio_path, "config.json")
    if os.path.exists(lmstudio_config_path):
        logger.info(f"Found model at LM Studio location: {lmstudio_path}")
        return lmstudio_path

    # Check project path
    project_config_path = os.path.join(project_path, "config.json")
    if os.path.exists(project_config_path):
        logger.info(f"Found model at project location: {project_path}")
        return project_path

    # Model not found in either location, return project path for download
    logger.debug(f"Model not found at LM Studio location: {lmstudio_path}")
    logger.debug(f"Model not found at project location: {project_path}")
    return project_path


def download_model_from_huggingface(repo_id: str, local_dir: str) -> None:
    """
    Download model from Hugging Face to local directory.

    Args:
        repo_id: Hugging Face repository ID (e.g., "lmstudio-community/Qwen3-VL-8B-Instruct-MLX-4bit")
        local_dir: Local directory path to save the model
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        raise RuntimeError(
            "huggingface_hub is required to download models. "
            "Please install it with: pip install huggingface_hub"
        )

    logger = get_logging_service()
    logger.info(f"Downloading model from Hugging Face: {repo_id}")
    logger.info(f"Target directory: {local_dir}")
    logger.info("This may take a while depending on your internet connection...")

    try:
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(local_dir), exist_ok=True)

        # Download the model
        snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
        )
        logger.info(f"Model downloaded successfully to {local_dir}")
    except Exception as e:
        raise RuntimeError(
            f"Failed to download model from Hugging Face: {e}\n"
            f"Repository: {repo_id}\n"
            f"Target directory: {local_dir}"
        ) from e


class ModelInferenceService:
    """Service for running vision-language model inference using MLX."""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize model inference service.

        Args:
            model_path: Optional path to model directory.
                       If not provided, will check old location first,
                       then new location, and download if not found.
        """
        if model_path:
            self.model_path = model_path
        else:
            # Auto-detect model path (checks old location first)
            self.model_path = find_model_path()
        self.model = None
        self.processor = None
        self._loaded = False
        self.logger = get_logging_service()

    def _load_model(self):
        """Load the MLX model and processor."""
        if self._loaded:
            return

        # Check for config.json (required by mlx-vlm) - if not found, download the model
        config_path = os.path.join(self.model_path, "config.json")
        if not os.path.exists(config_path):
            # Model doesn't exist or is incomplete, download it
            download_model_from_huggingface(
                repo_id=MODEL_NAME,
                local_dir=self.model_path,
            )
            # Verify download was successful
            if not os.path.exists(config_path):
                raise RuntimeError(
                    f"Model download completed but config.json not found at {config_path}\n"
                    "The downloaded model may be incomplete or corrupted."
                )

        try:
            # Use mlx_vlm.load() function (standard API)
            from mlx_vlm import load

            self.logger.info(f"Loading model from {self.model_path}...")
            self.model, self.processor = load(self.model_path)
            self._loaded = True
            self.logger.info(f"Model loaded successfully from {self.model_path}")
            return

        except Exception as e:
            error_msg = str(e)

            # Check for safetensors error and retry download
            if (
                "safetensors" in error_msg.lower()
                or "No safetensors found" in error_msg
            ):
                self.logger.warning(
                    f"Safetensors error detected: {error_msg}. "
                    "Attempting to re-download the model..."
                )
                try:
                    import shutil

                    # Remove the incomplete/corrupted model directory
                    if os.path.exists(self.model_path):
                        shutil.rmtree(self.model_path)
                        self.logger.info(
                            f"Removed incomplete model at {self.model_path}"
                        )

                    # Re-download the model
                    download_model_from_huggingface(
                        repo_id=MODEL_NAME,
                        local_dir=self.model_path,
                    )

                    # Verify download was successful
                    if not os.path.exists(config_path):
                        raise RuntimeError(
                            f"Model re-download completed but config.json not found at {config_path}\n"
                            "The downloaded model may be incomplete or corrupted."
                        )

                    # Try loading again after re-download
                    self.logger.info(f"Re-loading model from {self.model_path}...")
                    from mlx_vlm import load

                    self.model, self.processor = load(self.model_path)
                    self._loaded = True
                    self.logger.info(
                        f"Model loaded successfully after re-download from {self.model_path}"
                    )
                    return

                except Exception as retry_error:
                    raise RuntimeError(
                        f"Failed to re-download model after safetensors error: {retry_error}\n"
                        f"Original error: {e}\n"
                        "Please check your internet connection and try again."
                    ) from retry_error

            if "Config not found" in error_msg or "config.json" in error_msg.lower():
                raise RuntimeError(
                    f"Model configuration not found at {self.model_path}\n"
                    "The model may not be in MLX format or is missing required files.\n"
                    "Please download the MLX-compatible version from Hugging Face: "
                    "https://huggingface.co/lmstudio-community/Qwen3-VL-8B-Instruct-MLX-4bit"
                ) from e
            elif (
                "PyTorch" in error_msg
                or "Torchvision" in error_msg
                or "torch" in error_msg.lower()
            ):
                raise RuntimeError(
                    f"Missing dependencies: PyTorch and/or Torchvision\n"
                    f"Error: {e}\n\n"
                    "Please install the missing dependencies:\n"
                    "  pip install torch torchvision\n\n"
                    "Note: These are required by mlx-vlm for some model processors."
                ) from e
            else:
                raise RuntimeError(
                    f"Error loading model from {self.model_path}: {e}\n"
                    "Please ensure:\n"
                    "1. The model is in MLX format (not GGUF)\n"
                    "2. All model files are present in the directory\n"
                    "3. The model path is correct\n"
                    "4. All dependencies are installed (pip install -r requirements.txt)"
                ) from e

    def describe_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """
        Generate description for an image using the vision-language model.

        Args:
            image: PIL Image object
            prompt: Optional custom prompt. Defaults to config.PROMPT_TEXT

        Returns:
            Generated description text

        Raises:
            RuntimeError: If model loading or inference fails
        """
        if not self._loaded:
            self._load_model()

        prompt_text = prompt or PROMPT_TEXT

        try:
            # Use mlx_vlm.generate() function with proper API
            from mlx_vlm import generate
            from mlx_vlm.prompt_utils import apply_chat_template
            from mlx_vlm.utils import load_config

            # Load config for chat template
            config = load_config(self.model_path)

            # Format prompt using chat template
            # Note: mlx-vlm expects images as file paths or PIL Images
            formatted_prompt = apply_chat_template(
                self.processor, config, prompt_text, num_images=1
            )

            # Generate output
            # mlx_vlm.generate signature: generate(model, processor, formatted_prompt, image, verbose=False)
            # Returns a GenerationResult object
            result = generate(
                self.model,
                self.processor,
                formatted_prompt,
                [image],  # images should be a list
                verbose=False,
            )

            # Extract text from GenerationResult object
            # GenerationResult typically has a 'text' or 'generated_text' attribute
            if hasattr(result, "text"):
                return result.text
            elif hasattr(result, "generated_text"):
                return result.generated_text
            elif hasattr(result, "__str__"):
                return str(result)
            else:
                # Fallback: try to convert to string
                return str(result)

        except Exception as e:
            raise RuntimeError(f"Error during inference: {e}") from e
