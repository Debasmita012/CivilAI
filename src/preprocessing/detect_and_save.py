import cv2
import numpy as np
from ultralytics import YOLO
import os

def detect_and_save(model, image_path):
    """
    Detects cracks and generates both annotated image and heatmap.
    
    Returns:
        tuple: (annotated_image, crack_percentage, severity_score, risk_level, heatmap_path)
    """
    
    # Load YOLO model
    if isinstance(model, str):
        yolo_model = YOLO(model)
    else:
        yolo_model = model
    
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    original_img = img.copy()
    h, w = img.shape[:2]
    
    # Run detection
    results = yolo_model(img, conf=0.25)
    
    # Initialize metrics
    total_crack_area = 0
    detections = []
    
    # Process detections
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            
            # Calculate crack area
            crack_area = (x2 - x1) * (y2 - y1)
            total_crack_area += crack_area
            
            detections.append({
                'bbox': (x1, y1, x2, y2),
                'conf': conf,
                'area': crack_area
            })
            
            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(img, f'{conf:.2f}', (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Calculate metrics
    image_area = h * w
    crack_percentage = (total_crack_area / image_area) * 100
    
    # Calculate severity score (0-100)
    # Based on crack percentage and number of cracks
    severity_score = min(100, crack_percentage * 10 + len(detections) * 2)
    
    # Determine risk level
    if severity_score < 30:
        risk_level = "Low"
    elif severity_score < 60:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    # Generate heatmap
    heatmap_path = None
    if len(detections) > 0:
        heatmap = generate_heatmap(original_img, detections)
        
        # Save heatmap
        heatmap_dir = os.path.join(os.path.dirname(image_path), "..", "results")
        os.makedirs(heatmap_dir, exist_ok=True)
        heatmap_path = os.path.join(heatmap_dir, "heatmap.jpg")
        cv2.imwrite(heatmap_path, heatmap)
    
    return img, crack_percentage, severity_score, risk_level, heatmap_path


def generate_heatmap(img, detections):
    """
    Generate a heatmap overlay showing crack density and severity.
    """
    h, w = img.shape[:2]
    
    # Create blank heatmap
    heatmap = np.zeros((h, w), dtype=np.float32)
    
    # Add intensity for each detection
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        conf = det['conf']
        
        # Create a gaussian-like intensity around the crack
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        radius = max((x2 - x1), (y2 - y1)) // 2
        
        # Create circular gradient
        y_coords, x_coords = np.ogrid[:h, :w]
        distances = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        
        # Apply gaussian-like falloff
        mask = np.exp(-(distances**2) / (2 * (radius * 1.5)**2))
        heatmap += mask * conf * 100
    
    # Normalize heatmap
    if heatmap.max() > 0:
        heatmap = (heatmap / heatmap.max() * 255).astype(np.uint8)
    else:
        heatmap = heatmap.astype(np.uint8)
    
    # Apply colormap
    heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    
    # Blend with original image
    alpha = 0.6
    overlay = cv2.addWeighted(img, 1 - alpha, heatmap_colored, alpha, 0)
    
    return overlay