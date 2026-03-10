import os
from src.config import MODEL_PATH
from ultralytics import YOLO

def load_model():
    return YOLO(str(MODEL_PATH))

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = YOLO(model_path)
    return model

def predict(model, image_path):
    results = model(image_path)
    return results
