import os

splits = ["train", "val"]

for split in splits:
    img_dir = f"data/processed/{split}/images"
    label_dir = f"data/processed/{split}/labels"
    os.makedirs(label_dir, exist_ok=True)

    for img in os.listdir(img_dir):
        if img.lower().endswith((".jpg", ".png")):
            label_file = img.rsplit(".", 1)[0] + ".txt"
            with open(os.path.join(label_dir, label_file), "w") as f:
                # class 0 = crack, full-image bounding box
                f.write("0 0.5 0.5 1.0 1.0\n")
