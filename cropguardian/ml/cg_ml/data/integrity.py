"""Image integrity + normalisation (spec 9.4 steps 2-3) and per-image statistics (step 6).

Integrity: Pillow `verify()` then a full decode; drop corrupt/truncated files and images with a
side < 128 px. Normalise: apply EXIF orientation, convert to RGB, strip metadata (EXIF/GPS never
leaves the raw archive - spec 16.11).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from PIL import Image, ImageOps, UnidentifiedImageError

MIN_SIDE_PX = 128
MAX_PIXELS = 100_000_000  # decompression-bomb guard (Pillow default warns at ~89M)
Image.MAX_IMAGE_PIXELS = MAX_PIXELS

IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".bmp", ".webp"})


@dataclass(frozen=True)
class ImageCheck:
    ok: bool
    reason: str  # "" when ok; else corrupt | too_small | unreadable
    width: int = 0
    height: int = 0


def check_image(path: Path, min_side: int = MIN_SIDE_PX) -> ImageCheck:
    try:
        with Image.open(path) as im:
            im.verify()  # structural check; the file object is unusable afterwards
        with Image.open(path) as im:
            im.load()  # full decode catches truncated data
            upright = ImageOps.exif_transpose(im) or im  # None when no rotation was needed
            width, height = upright.size
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, Image.DecompressionBombError):
        return ImageCheck(False, "corrupt")
    if min(width, height) < min_side:
        return ImageCheck(False, "too_small", width, height)
    return ImageCheck(True, "", width, height)


def normalise_image(path: Path) -> Image.Image:
    """EXIF-transpose, RGB, metadata dropped (a fresh Image holds pixels only)."""
    with Image.open(path) as im:
        im.load()
        rotated = ImageOps.exif_transpose(im) or im
        rgb = rotated.convert("RGB")
        # frombytes copies pixels only: no EXIF, ICC profile or text chunks carry over
        return Image.frombytes("RGB", rgb.size, rgb.tobytes())


def laplacian_variance(gray: npt.NDArray[np.floating[Any]]) -> float:
    """Blur measure: variance of the 4-neighbour Laplacian on a float grayscale array."""
    if gray.ndim != 2 or min(gray.shape) < 3:
        raise ValueError("need a 2-D array of at least 3x3")
    g = gray.astype(np.float64)
    lap = -4 * g[1:-1, 1:-1] + g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:]
    return float(lap.var())


def image_stats(im: Image.Image) -> dict[str, float]:
    """Brightness mean (0-255), blur (Laplacian variance), pixel dimensions."""
    gray = np.asarray(im.convert("L"), dtype=np.float64)
    return {
        "brightness_mean": float(gray.mean()),
        "laplacian_var": laplacian_variance(gray),
        "width": float(im.size[0]),
        "height": float(im.size[1]),
    }
