
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from models.preprocessing.optic_disc import locate_optic_disc

IMAGE_DIR = "../data/REFUGE/val"
MASK_DIR = (
    "../data/REFUGE/REFUGE-Validation400-GT/"
    "REFUGE-Validation400-GT/Disc_Cup_Masks"
)

filenames = ["V0005", "V0213"]

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

for i, name in enumerate(filenames):
    image = Image.open(
        os.path.join(IMAGE_DIR, name + ".jpg")
    ).convert("RGB")

    mask = np.array(Image.open(
        os.path.join(MASK_DIR, name + ".bmp")
    ).convert("L"))

    if image.size != (mask.shape[1], mask.shape[0]):
        raise ValueError(f"Image/mask dimensions differ: {name}")

    ys, xs = np.where(mask < 255)
    actual_x, actual_y = xs.mean(), ys.mean()

    pred_x, pred_y = locate_optic_disc(image)

    error = np.hypot(
        pred_x - actual_x,
        pred_y - actual_y
    )

    axes[i, 0].imshow(image)
    axes[i, 0].scatter(
        actual_x, actual_y,
        c="lime", marker="x", s=150,
        label="Actual"
    )
    axes[i, 0].scatter(
        pred_x, pred_y,
        c="red", marker="x", s=150,
        label="Predicted"
    )
    axes[i, 0].legend()
    axes[i, 0].set_title(
        f"{name} | Error: {error:.1f}px"
    )
    axes[i, 0].axis("off")

    # Visualize the green channel used by our locator
    axes[i, 1].imshow(
        np.array(image)[:, :, 1],
        cmap="gray"
    )
    axes[i, 1].scatter(
        pred_x, pred_y,
        c="red", marker="x", s=150
    )
    axes[i, 1].set_title(f"{name} | Green channel")
    axes[i, 1].axis("off")

plt.tight_layout()
plt.show()
