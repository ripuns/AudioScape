"""Image preprocessing with Pillow."""
from __future__ import annotations

import io

from PIL import Image, ImageOps, UnidentifiedImageError

from . import config


def load_image(data: bytes, max_side: int = config.MAX_IMAGE_SIDE) -> Image.Image:
    """Decode upload bytes -> upright RGB image, downscaled so the longest side <= max_side."""
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("not a valid image file") from exc
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")
    if max(img.size) > max_side:
        img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return img
