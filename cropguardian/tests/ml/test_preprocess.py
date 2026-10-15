"""Train/serve preprocessing parity (app/ml/preprocess.py vs training transforms)."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_deterministic(): """same bytes twice → identical tensors (np.array_equal)."""
def test_shape_and_dtype(): """(1, 3, 224, 224), float32."""
def test_matches_training_eval_transform(): """max abs diff vs torchvision eval transform < 1e-5 on 20 fixtures."""
def test_exif_orientation_applied(): """rotated-EXIF fixture → same tensor as the physically rotated image."""
