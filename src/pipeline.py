# src/pipeline.py
"""
High-level pipeline skeleton: load models, run detection, crop patches for severity model.
This file should be extended with proper error handling & model paths.
"""

from src.inference.detect import load_model, detect_image
# severity model loader will be added later
import cv2
from pathlib import Path

def load_models(yolo_weights="models/yolov8_crack.pt"):
    yolo = load_model(yolo_weights)
    # placeholder: severity model loader can be added here
    return {"yolo": yolo, "severity": None}

def detect_and_save(image_path, models, out_image="results/detections/out.jpg"):
    yolo = models["yolo"]
    annotated = detect_image(yolo, image_path, save_path=out_image)
    return out_image

if __name__ == "__main__":
    models = load_models()
    res = detect_and_save("data/processed/test/example.jpg", models)
    print("Pipeline complete, annotated at:", res)
