
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from models.preprocessing.optic_disc import (
    locate_optic_disc,
    crop_optic_disc,
)

IMAGE_DIR = "../data/REFUGE/val"
MASK_DIR = (
    "../data/REFUGE/REFUGE-Validation400-GT/"
    "REFUGE-Validation400-GT/Disc_Cup_Masks"
)

NUM_IMAGES = 10
random.seed(42)

# Find validation images with corresponding masks
image_files = sorted([
    filename for filename in os.listdir(IMAGE_DIR)
    if filename.lower().endswith((".jpg", ".jpeg", ".png"))
    and os.path.isfile(
        os.path.join(
            MASK_DIR,
            os.path.splitext(filename)[0] + ".bmp"
        )
    )
])

selected = random.sample(
    image_files,
    min(NUM_IMAGES, len(image_files))
)

errors = []

fig, axes = plt.subplots(
    len(selected), 2,
    figsize=(12, 4 * len(selected)),
    squeeze=False
)

for i, filename in enumerate(selected):
    image_path = os.path.join(IMAGE_DIR, filename)
    mask_path = os.path.join(
        MASK_DIR,
        os.path.splitext(filename)[0] + ".bmp"
    )

    image = Image.open(image_path).convert("RGB")
    mask = np.array(Image.open(mask_path).convert("L"))

    if image.size != (mask.shape[1], mask.shape[0]):
        raise ValueError(f"Image/mask size mismatch: {filename}")

    ys, xs = np.where(mask < 255)

    actual_x = float(xs.mean())
    actual_y = float(ys.mean())

    predicted_x, predicted_y = locate_optic_disc(image)

    error = np.sqrt(
        (predicted_x - actual_x) ** 2
        + (predicted_y - actual_y) ** 2
    )

    errors.append(error)

    cropped = crop_optic_disc(image)

    axes[i, 0].imshow(image)
    axes[i, 0].scatter(
        actual_x, actual_y,
        color="lime", marker="x", s=100
    )
    axes[i, 0].scatter(
        predicted_x, predicted_y,
        color="red", marker="x", s=100
    )
    axes[i, 0].set_title(
        f"{filename} | Error: {error:.1f}px"
    )
    axes[i, 0].axis("off")

    axes[i, 1].imshow(cropped)
    axes[i, 1].set_title("Automatic Crop")
    axes[i, 1].axis("off")

plt.tight_layout()
plt.show()

print("\nLocalization Results")
print("--------------------")
print(f"Images tested: {len(errors)}")
print(f"Mean error: {np.mean(errors):.2f} pixels")
print(f"Median error: {np.median(errors):.2f} pixels")
print(f"Maximum error: {np.max(errors):.2f} pixels")
print(f"Within 60 pixels: {np.mean(np.array(errors) < 60) * 100:.1f}%")
