import os
import cv2
import numpy as np
from ultralytics import YOLO


# ==================================================
# LOAD MODEL
# ==================================================
def load_model(model_path: str):
    """
    Load YOLO crack detection model.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    return YOLO(model_path)


# ==================================================
# DETECT CRACKS + GENERATE HEATMAP
# ==================================================
def detect_and_save(
    model,
    image_path: str,
    output_path: str,
    conf_threshold: float = 0.25
):
    """
    Detect cracks, save annotated image, generate heatmap,
    and return analysis results.

    Returns:
        annotated_image (np.ndarray)
        crack_percentage (float)
        severity_score (float)
        risk_level (str)
        heatmap_path (str)
    """

    # ------------------------------
    # Load image
    # ------------------------------
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    height, width = image.shape[:2]
    total_area = height * width

    # ------------------------------
    # YOLO inference
    # ------------------------------
    results = model(image, conf=conf_threshold)

    annotated = image.copy()

    detections = []

    # 🔥 Heatmap mask (single channel)
    heatmap_mask = np.zeros((height, width), dtype=np.float32)

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            confidence = float(box.conf[0])
            if confidence < conf_threshold:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            detections.append((x1, y1, x2, y2, confidence))

            # ------------------------------
            # Draw bounding box
            # ------------------------------
            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            label_y = max(y1 - 8, 15)
            cv2.putText(
                annotated,
                f"Crack {confidence:.2f}",
                (x1, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA
            )

            # ------------------------------
            # 🔥 Heatmap accumulation
            # ------------------------------
            heatmap_mask[y1:y2, x1:x2] += confidence

    # ------------------------------
    # Crack percentage calculation
    # ------------------------------
    crack_area = sum(
        max(0, x2 - x1) * max(0, y2 - y1)
        for x1, y1, x2, y2, _ in detections
    )

    crack_percentage = (
        (crack_area / total_area) * 100
        if detections else 0.0
    )

    # ------------------------------
    # Severity & risk level
    # ------------------------------
    severity_score = min(100.0, crack_percentage * 2.0)

    if severity_score < 20:
        risk_level = "Low"
    elif severity_score < 50:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # ------------------------------
    # 🔥 Heatmap generation
    # ------------------------------
    heatmap_norm = cv2.normalize(
        heatmap_mask, None, 0, 255, cv2.NORM_MINMAX
    ).astype(np.uint8)

    heatmap_color = cv2.applyColorMap(
        heatmap_norm, cv2.COLORMAP_JET
    )

    heatmap_overlay = cv2.addWeighted(
        image, 0.6, heatmap_color, 0.4, 0
    )

    # ------------------------------
    # Save outputs
    # ------------------------------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    heatmap_path = output_path.replace(".jpg", "_heatmap.jpg")

    cv2.imwrite(output_path, annotated)
    cv2.imwrite(heatmap_path, heatmap_overlay)

    # ------------------------------
    # Return results
    # ------------------------------
    return (
        annotated,
        crack_percentage,
        severity_score,
        risk_level,
        heatmap_path
    )