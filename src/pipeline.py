import os
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