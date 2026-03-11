import os
import sys

# ==================================================
# ROBUST PROJECT ROOT DETECTION
# Works regardless of whether you run from ui/, src/,
# or the project root itself.
# ==================================================
def _find_project_root():
    """Walk up from this file until we find the 'models' folder."""
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):  # max 6 levels up
        if os.path.isdir(os.path.join(current, "models")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # Fallback: two levels up from src/pipeline.py → project root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_ROOT = _find_project_root()
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "crack.pt")

from src.inference.detect import load_model, detect_and_save


def load_models():
    """Loads the trained crack detection model."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found at: {MODEL_PATH}\n"
            f"Project root resolved to: {PROJECT_ROOT}\n"
            f"Please ensure 'crack.pt' exists inside the 'models/' folder at your project root."
        )
    return load_model(MODEL_PATH)


def run_pipeline(model, image_path, output_path):
    """Runs crack detection pipeline."""
from src.inference.detect import load_model, detect_and_save

# ==================================================
# PROJECT PATHS
# ==================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "crack.pt")

# ==================================================
# LOAD MODEL (USED BY app.py)
# ==================================================
def load_models():
    """
    Loads the trained crack detection model.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

    return load_model(MODEL_PATH)

# ==================================================
# RUN PIPELINE (CORE INFERENCE WRAPPER)
# ==================================================
def run_pipeline(model, image_path, output_path):
    """
    Runs crack detection pipeline.

    Returns a dictionary compatible with app.py:
    - annotated_image (NumPy array)
    - annotated_image_path (str)
    - heatmap_path (str)
    - crack_percentage (float)
    - severity_score (float)
    - risk_level (str)
    """

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image not found: {image_path}")

    (
        annotated_img,
        crack_pct,
        severity,
        risk,
        heatmap_path
    ) = detect_and_save(
        model=model,
        image_path=image_path,
        output_path=output_path
    )

    return {
        "annotated_image": annotated_img,
        "annotated_image_path": output_path,
        "heatmap_path": heatmap_path,
        "crack_percentage": float(crack_pct),
        "severity_score": float(severity),
        "risk_level": str(risk)
    }