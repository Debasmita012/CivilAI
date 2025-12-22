from src.inference.detect import load_model, detect_image


def load_models(yolo_weights="models/crack.pt"):
    """
    Load all ML models (currently YOLO only)
    """
    yolo = load_model(yolo_weights)
    return {"yolo": yolo}


def detect_and_save(image_path, models, out_image):
    """
    Complete detection pipeline
    """
    yolo = models["yolo"]

    annotated_img, crack_percentage, risk_level, severity_score = detect_image(
        model=yolo,
        image_path=image_path,
        save_path=out_image
    )

    return annotated_img, crack_percentage, risk_level, severity_score
