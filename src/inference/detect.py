# src/inference/detect.py
"""
Simple wrapper to run YOLOv8 inference and save annotated result.
Requires ultralytics and a trained weights file (models/yolov8_crack.pt)
"""

from ultralytics import YOLO
import cv2
from pathlib import Path

def load_model(weights_path="models/yolov8_crack.pt"):
    model = YOLO(weights_path)
    return model

def detect_image(model, image_path, save_path=None, conf=0.25):
    results = model.predict(source=str(image_path), conf=conf, save=False, verbose=False)
    # results is a list-like; take first
    r = results[0]
    # get annotated image from r.orig_img (numpy)
    img = r.orig_img if hasattr(r, "orig_img") else None
    if img is None:
        # fallback: read original
        img = cv2.imread(str(image_path))
    # draw boxes using ultralytics convenience
    annotated = r.plot()  # returns annotated image (numpy)
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(save_path), annotated[:,:,::-1])  # BGR/RGB fix
    return annotated

if __name__ == "__main__":
    model = load_model()
    out = detect_image(model, "data/processed/test/example.jpg", save_path="results/detections/example_annotated.jpg")
    print("Saved annotated:", "results/detections/example_annotated.jpg")
