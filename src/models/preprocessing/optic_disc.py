import numpy as np
from PIL import Image, ImageFilter

def locate_optic_disc(image):
    """
    Estimate the optic disc center using brightness,
    saturation, and local contrast.

    Does not require segmentation masks.
    """
    image = image.convert("RGB")
    rgb = np.asarray(image, dtype=np.float32) / 255.0

    h, w = rgb.shape[:2]

    # Green channel often provides useful disc contrast
    green = rgb[:, :, 1]

    # HSV saturation helps identify nearly white regions
    max_rgb = rgb.max(axis=2)
    min_rgb = rgb.min(axis=2)

    saturation = np.where(
        max_rgb > 0,
        (max_rgb - min_rgb) / np.maximum(max_rgb, 1e-6),
        0,
    )

    # Smooth brightness to suppress vessels and small artifacts
    green_img = Image.fromarray(
        (green * 255).astype(np.uint8)
    )
    blurred = green_img.filter(
        ImageFilter.GaussianBlur(radius=25)
    )

    brightness = np.asarray(
        blurred, dtype=np.float32
    ) / 255.0

    # Smooth saturation to evaluate larger regions
    sat_img = Image.fromarray(
        (saturation * 255).astype(np.uint8)
    )
    sat_blurred = sat_img.filter(
        ImageFilter.GaussianBlur(radius=25)
    )

    smooth_sat = np.asarray(
        sat_blurred, dtype=np.float32
    ) / 255.0

    # Brightness is useful, but low-saturation white
    # artifacts should receive a penalty.
    score = brightness * (0.4 + 0.6 * smooth_sat)

    # Exclude the outer image border
    margin_y = int(h * 0.15)
    margin_x = int(w * 0.15)

    search = score[
        margin_y:h - margin_y,
        margin_x:w - margin_x,
    ]

    y, x = np.unravel_index(
        np.argmax(search),
        search.shape
    )

    return int(x + margin_x), int(y + margin_y)



def crop_optic_disc(image, crop_fraction=0.45):
    """
    Crop a square region around the estimated optic disc.
    """
    image = image.convert("RGB")
    w, h = image.size

    center_x, center_y = locate_optic_disc(image)

    crop_size = int(min(w, h) * crop_fraction)
    half = crop_size // 2

    left = max(0, min(center_x - half, w - crop_size))
    top = max(0, min(center_y - half, h - crop_size))

    return image.crop((
        left,
        top,
        left + crop_size,
        top + crop_size,
    ))