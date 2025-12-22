from ultralytics import YOLO
import cv2
import numpy as np


def load_model(weights_path):
    """
    Load YOLO crack detection model
    """
    return YOLO(weights_path)


def detect_image(model, image_path, save_path=None):
    """
    Detect cracks and compute severity

    Returns:
    - annotated image
    - crack percentage
    - risk level
    - severity score
    """

    # Load image
    image = cv2.imread(image_path)
    h, w, _ = image.shape
    image_area = h * w

    # Run inference
    results = model(image_path)

    annotated = results[0].plot()

    total_crack_area = 0
    confidences = []

    if results[0].boxes is not None:
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            area = (x2 - x1) * (y2 - y1)
            total_crack_area += area
            confidences.append(float(box.conf[0]))

    # Crack percentage
    crack_percentage = (total_crack_area / image_area) * 100 if image_area > 0 else 0

    # Severity score (0–100)
    avg_conf = np.mean(confidences) if confidences else 0
    severity_score = min((crack_percentage * avg_conf * 10), 100)

    # Risk logic (ENGINEERING BASED)
    if severity_score < 20:
        risk = "Low"
    elif severity_score < 50:
        risk = "Medium"
    else:
        risk = "High"

    # Save annotated image
    if save_path:
        cv2.imwrite(save_path, annotated)

    return annotated, crack_percentage, risk, severity_score
