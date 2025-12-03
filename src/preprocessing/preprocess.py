# src/preprocessing/preprocess.py
"""
Simple preprocessing utilities:
- load image
- resize
- save resized copies into processed folder
"""

import cv2
from pathlib import Path

def resize_image(src_path, dst_path, size=(640,640)):
    img = cv2.imread(str(src_path))
    if img is None:
        raise ValueError(f"Failed to read image: {src_path}")
    img_resized = cv2.resize(img, size)
    cv2.imwrite(str(dst_path), img_resized)

def batch_resize(src_dir, dst_dir, size=(640,640)):
    src = Path(src_dir)
    dst = Path(dst_dir)
    dst.mkdir(parents=True, exist_ok=True)
    for p in src.glob("*.*"):
        try:
            outp = dst / p.name
            resize_image(p, outp, size=size)
        except Exception as e:
            print(f"skipping {p.name}: {e}")

if __name__ == "__main__":
    # example usage (edit paths as needed)
    batch_resize("data/raw/custom_images", "data/processed/train")
    print("Done resizing.")
