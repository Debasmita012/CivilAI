# src/pipeline.py
from src.inference.detect import load_model, detect_image

def load_models(yolo_weights="models/yolov8_crack.pt"):
    yolo = load_model(yolo_weights)
    return {"yolo": yolo}

def detect_and_save(image_path, models, out_image):
    yolo = models["yolo"]
    annotated = detect_image(
        yolo,
        image_path,
        save_path=out_image
    )
    return annotated

