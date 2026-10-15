"""Image → tensor. MUST match training preprocessing exactly (ml/vision/train.md §Preprocess):
resize short side 256 (bilinear) → centre crop 224 → float32 /255 → ImageNet mean/std →
CHW → batch dim. Deterministic: same bytes → same tensor (tests/ml/test_preprocess.py).
"""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
INPUT_SIZE = 224


def to_tensor(jpeg_bytes: bytes) -> npt.NDArray[np.float32]:
    """Return array of shape (1, 3, 224, 224)."""
    raise NotImplementedError
