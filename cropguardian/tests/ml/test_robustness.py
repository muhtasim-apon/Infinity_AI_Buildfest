"""Robustness — prediction stability under realistic phone/field perturbations (statistics.md §8).
Metric: top-1 agreement with the clean image's prediction over the validation split. Gate ≥ 0.90."""

import pytest

pytestmark = pytest.mark.skip("stub — needs trained model")

PERTURBATIONS = [
    ("gaussian_blur_sigma_2", {"sigma": 2.0}),
    ("brightness_minus_30", {"factor": 0.7}),
    ("brightness_plus_30", {"factor": 1.3}),
    ("rotate_30", {"degrees": 30}),
    ("jpeg_q40", {"quality": 40}),
    ("center_crop_80", {"fraction": 0.8}),
]


@pytest.mark.parametrize("name, params", PERTURBATIONS)
def test_agreement_under_perturbation(name, params): ...
