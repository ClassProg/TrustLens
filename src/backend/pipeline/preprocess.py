from io import BytesIO
from PIL import Image, UnidentifiedImageError

def validate_image(file):
    raw = file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise ValueError("Image must be smaller than 10 MB.")
    try:
        image = Image.open(BytesIO(raw))
        if image.format not in ("PNG", "JPEG"):
            raise ValueError("Please upload a PNG or JPG image.")
        image.verify()
        image = Image.open(BytesIO(raw)).convert("RGB")
        return image
    except (UnidentifiedImageError, OSError):
        raise ValueError("The uploaded image could not be opened.")
