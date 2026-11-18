
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from models.preprocessing.optic_disc import locate_optic_disc

IMAGE_DIR = "../data/REFUGE/val"
MASK_DIR = (
    "../data/REFUGE/REFUGE-Validation400-GT/"
    "REFUGE-Validation400-GT/Disc_Cup_Masks"
)
OUTPUT_DIR = "models/outputs/optic_disc_tests"
CROP_FRACTION = 0.45

os.makedirs(OUTPUT_DIR, exist_ok=True)

results = []
failures = []

mask_files = sorted([
    f for f in os.listdir(MASK_DIR)
    if f.lower().endswith(".bmp")
])

for mask_file in mask_files:
    name = os.path.splitext(mask_file)[0]
    image_path = os.path.join(IMAGE_DIR, name + ".jpg")
    mask_path = os.path.join(MASK_DIR, mask_file)

    if not os.path.isfile(image_path):
        failures.append(f"{name}: missing retinal image")
        continue

    try:
        with Image.open(image_path) as im:
            image = im.convert("RGB")

        with Image.open(mask_path) as im:
            mask = np.asarray(im.convert("L"))

        if image.size != (mask.shape[1], mask.shape[0]):
            raise ValueError("Image and mask dimensions do not match")

        ys, xs = np.where(mask < 255)
        if len(xs) == 0:
            raise ValueError("Mask contains no optic disc")

        actual_x = float(xs.mean())
        actual_y = float(ys.mean())

        pred_x, pred_y = locate_optic_disc(image)

        error = float(np.hypot(
            pred_x - actual_x,
            pred_y - actual_y
        ))

        w, h = image.size
        crop_size = int(min(w, h) * CROP_FRACTION)
        half = crop_size // 2

        left = max(0, min(pred_x - half, w - crop_size))
        top = max(0, min(pred_y - half, h - crop_size))
        right = left + crop_size
        bottom = top + crop_size

        # Check whether the entire disc bounding box is inside
        fully_covered = (
            xs.min() >= left
            and xs.max() < right
            and ys.min() >= top
            and ys.max() < bottom
        )

        # Fraction of disc pixels retained in the crop
        disc_pixels = mask < 255
        retained = np.count_nonzero(
            disc_pixels[top:bottom, left:right]
        )
        coverage = retained / np.count_nonzero(disc_pixels)

        results.append({
            "image": name,
            "error_px": error,
            "coverage": coverage,
            "fully_covered": fully_covered,
            "pred_x": pred_x,
            "pred_y": pred_y,
            "actual_x": actual_x,
            "actual_y": actual_y,
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
        })

    except Exception as exc:
        failures.append(f"{name}: {exc}")

if not results:
    raise RuntimeError("No images were successfully evaluated")

errors = np.array([r["error_px"] for r in results])
coverage = np.array([r["coverage"] for r in results])
full = np.array([r["fully_covered"] for r in results])

print("\nOPTIC DISC LOCALIZATION RESULTS")
print("--------------------------------")
print(f"Masks found: {len(mask_files)}")
print(f"Images evaluated: {len(results)}")
print(f"Failures: {len(failures)}")
print(f"Mean error: {errors.mean():.2f} px")
print(f"Median error: {np.median(errors):.2f} px")
print(f"95th percentile error: {np.percentile(errors, 95):.2f} px")
print(f"Maximum error: {errors.max():.2f} px")
print(f"Within 60 pixels: {(errors < 60).mean() * 100:.1f}%")
print(f"Fully covered discs: {full.sum()}/{len(full)}")
print(f"Average disc coverage: {coverage.mean() * 100:.2f}%")
print(f"Minimum disc coverage: {coverage.min() * 100:.2f}%")

# Save complete results
csv_path = os.path.join(OUTPUT_DIR, "localization_results.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

# Save worst 10 examples, prioritizing incomplete crops
worst = sorted(
    results,
    key=lambda r: (r["coverage"], -r["error_px"])
)[:10]

for r in worst:
    image_path = os.path.join(IMAGE_DIR, r["image"] + ".jpg")
    image = Image.open(image_path).convert("RGB")

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    axes[0].imshow(image)
    axes[0].scatter(
        r["actual_x"], r["actual_y"],
        color="lime", marker="x", s=120,
        label="Ground truth"
    )
    axes[0].scatter(
        r["pred_x"], r["pred_y"],
        color="red", marker="x", s=120,
        label="Predicted"
    )
    axes[0].legend()
    axes[0].set_title(
        f'{r["image"]} | Error: {r["error_px"]:.1f}px'
    )
    axes[0].axis("off")

    axes[1].imshow(image.crop((
        r["left"], r["top"],
        r["right"], r["bottom"]
    )))
    axes[1].set_title(
        f'Disc coverage: {r["coverage"] * 100:.1f}%'
    )
    axes[1].axis("off")

    plt.tight_layout()
    fig.savefig(
        os.path.join(OUTPUT_DIR, f'{r["image"]}_worst.png'),
        dpi=120
    )
    plt.close(fig)

if failures:
    with open(
        os.path.join(OUTPUT_DIR, "failures.txt"), "w"
    ) as f:
        f.write("\n".join(failures))

print(f"\nResults saved to: {OUTPUT_DIR}")
