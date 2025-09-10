"""Model management functionality."""

import os
from collections.abc import Callable

from ..config import Paths
from ..models.sam_model import SamModel
from ..utils.logger import logger

# Optional SAM-2 support
try:
    from ..models.sam2_model import Sam2Model

    SAM2_AVAILABLE = True
except ImportError:
    logger.info(
        "SAM-2 not available. Install with: pip install git+https://github.com/facebookresearch/sam2.git"
    )
    Sam2Model = None
    SAM2_AVAILABLE = False


class ModelManager:
    """Manages SAM model loading and selection."""

    def __init__(self, paths: Paths):
        self.paths = paths
        self.sam_model: SamModel | None = None
        self.current_models_folder: str | None = None
        self.on_model_changed: Callable[[str], None] | None = None

    def initialize_default_model(self, model_type: str = "vit_h") -> SamModel | None:
        """Initialize the default SAM model.

        Returns:
            SamModel instance if successful, None if failed
        """
        try:
            logger.info(f"Step 4/8: Loading {model_type.upper()} model...")
            self.sam_model = SamModel(model_type=model_type)
            self.current_models_folder = str(self.paths.models_dir)
            return self.sam_model
        except Exception as e:
            logger.error(f"Step 4/8: Failed to initialize default model: {e}")
            self.sam_model = None
            return None

    def get_available_models(self, folder_path: str) -> list[tuple[str, str]]:
        """Get list of available .pth models in folder.

        Returns:
            List of (display_name, full_path) tuples
        """
        pth_files = []
        for root, _dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".pth") or file.lower().endswith(".pt"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, folder_path)
                    pth_files.append((rel_path, full_path))

        return sorted(pth_files, key=lambda x: x[0])

    def detect_model_type(self, model_path: str) -> str:
        """Detect model type from filename."""
        filename = os.path.basename(model_path).lower()

        # Check if it's a SAM2 model
        if self._is_sam2_model(model_path):
            if "tiny" in filename or "_t" in filename:
                return "sam2_tiny"
            elif "small" in filename or "_s" in filename:
                return "sam2_small"
            elif "base_plus" in filename or "_b+" in filename:
                return "sam2_base_plus"
            elif "large" in filename or "_l" in filename:
                return "sam2_large"
            else:
                return "sam2_large"  # default for SAM2
        else:
            # Original SAM model types
            if "vit_l" in filename or "large" in filename:
                return "vit_l"
            elif "vit_b" in filename or "base" in filename:
                return "vit_b"
            elif "vit_h" in filename or "huge" in filename:
                return "vit_h"
            return "vit_h"  # default for SAM1

    def _is_sam2_model(self, model_path: str) -> bool:
        """Check if the model is a SAM2 model based on filename patterns."""
        filename = os.path.basename(model_path).lower()
        sam2_indicators = ["sam2", "sam2.1", "hiera", "_t.", "_s.", "_b+.", "_l."]
        return any(indicator in filename for indicator in sam2_indicators)

    def load_custom_model(self, model_path: str) -> bool:
        """Load a custom model from path.

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(model_path):
            return False

        model_type = self.detect_model_type(model_path)

        try:
            # Clear existing model from memory
            if self.sam_model is not None:
                del self.sam_model
                import torch

                torch.cuda.empty_cache() if torch.cuda.is_available() else None

            # Create appropriate model instance
            if self._is_sam2_model(model_path):
                if not SAM2_AVAILABLE:
                    logger.warning(
                        f"SAM-2 model detected but SAM-2 not installed: {model_path}"
                    )
                    logger.info(
                        "Install SAM-2 with: pip install git+https://github.com/facebookresearch/sam2.git"
                    )
                    return False

                logger.info(f"Loading SAM2 model: {model_type}")
                self.sam_model = Sam2Model(model_path)
            else:
                logger.info(f"Loading SAM1 model: {model_type}")
                # Convert SAM2 model types back to SAM1 types for compatibility
                sam1_model_type = model_type
                if model_type.startswith("sam2_"):
                    type_mapping = {
                        "sam2_tiny": "vit_b",
                        "sam2_small": "vit_b",
                        "sam2_base_plus": "vit_l",
                        "sam2_large": "vit_h",
                    }
                    sam1_model_type = type_mapping.get(model_type, "vit_h")

                # Create SAM1 model with custom path
                self.sam_model = SamModel(
                    model_type=sam1_model_type, custom_model_path=model_path
                )

            success = self.sam_model.is_loaded

            if success and self.on_model_changed:
                model_name = os.path.basename(model_path)
                self.on_model_changed(f"Current: {model_name}")

            return success

        except Exception as e:
            logger.error(f"Failed to load custom model: {e}")
            self.sam_model = None
            return False

    def set_models_folder(self, folder_path: str) -> None:
        """Set the current models folder."""
        self.current_models_folder = folder_path

    def get_models_folder(self) -> str | None:
        """Get the current models folder."""
        return self.current_models_folder

    def is_model_available(self) -> bool:
        """Check if a SAM model is loaded and available."""
        return self.sam_model is not None and getattr(
            self.sam_model, "is_loaded", False
        )

    def set_image_from_path(self, image_path: str) -> bool:
        """Set image for SAM model from file path."""
        if not self.is_model_available():
            return False
        return self.sam_model.set_image_from_path(image_path)

    def set_image_from_array(self, image_array) -> bool:
        """Set image for SAM model from numpy array."""
        if not self.is_model_available():
            return False
        return self.sam_model.set_image_from_array(image_array)
