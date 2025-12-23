import cv2
import numpy as np

def generate_heatmap(image, detections, alpha=0.5):
    """
    Create heatmap overlay from YOLO detections
    """
    heatmap = np.zeros(image.shape[:2], dtype=np.float32)

    for det in detections:
        x1, y1, x2, y2, conf = det
        heatmap[y1:y2, x1:x2] += conf

    heatmap = np.clip(heatmap, 0, 1)
    heatmap = cv2.GaussianBlur(heatmap, (31, 31), 0)

    heatmap_color = cv2.applyColorMap(
        np.uint8(255 * heatmap),
        cv2.COLORMAP_JET
    )

    overlay = cv2.addWeighted(image, 1 - alpha, heatmap_color, alpha, 0)
    return overlay