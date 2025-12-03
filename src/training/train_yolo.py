# src/training/train_yolo.py
"""
Minimal YOLOv8 training starter using ultralytics.
Edit dataset.yaml path and hyperparameters before running.
"""

from ultralytics import YOLO

def train(dataset_yaml="dataset.yaml", epochs=30, imgsz=640, model="yolov8n.pt"):
    print("Starting YOLOv8 training...")
    model = YOLO(model)
    model.train(data=dataset_yaml, epochs=epochs, imgsz=imgsz)
    print("Training finished.")

if __name__ == "__main__":
    train()
