import os
import random
import shutil

BASE = "data/processed"
SRC = f"{BASE}/train"
VAL = f"{BASE}/val"
TEST = f"{BASE}/test"

os.makedirs(VAL, exist_ok=True)
os.makedirs(TEST, exist_ok=True)

images = [f for f in os.listdir(SRC) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
random.shuffle(images)

total = len(images)
val_count = int(0.15 * total)
test_count = int(0.15 * total)

for img in images[:val_count]:
    shutil.move(os.path.join(SRC, img), os.path.join(VAL, img))

for img in images[val_count:val_count + test_count]:
    shutil.move(os.path.join(SRC, img), os.path.join(TEST, img))

print("Split complete")
