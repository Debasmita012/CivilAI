# src/inference/detect.py
from ultralytics import YOLO
import cv2

def load_model(weights_path):
    return YOLO(weights_path)

def detect_image(model, image_path, save_path=None):
    results = model(image_path)

    annotated = results[0].plot()

    if save_path:
        cv2.imwrite(save_path, annotated)

    return annotated
