"""Whitebox: app/ml/decision.py — 100 % branch coverage required (safety-critical, ADR 0005).

Each test maps to one branch in ``decide()``; see docs/testing/test-strategy.md §2.
"""

import pytest

pytestmark = pytest.mark.skip("stub — implement with app.ml.decision")


def test_confident_prediction_is_diagnosed():
    """logits strongly favour class 4 (blast), T=1, τ=0.7 → abstained False, band high, top3[0] == 4."""


def test_low_confidence_abstains():
    """near-uniform logits → max prob < τ → abstained True, reason 'low_confidence', band 'low'."""


def test_exactly_threshold_diagnoses():
    """construct logits whose calibrated max prob == τ (within 1e-9) → diagnosed (boundary is inclusive)."""


def test_nan_or_inf_logits_abstain():
    """any non-finite logit → abstained True, reason 'invalid_logits'; never raises."""


def test_out_of_distribution_abstains_even_if_confident():
    """energy score above ood_threshold → abstained True, reason 'out_of_distribution'."""


def test_temperature_above_one_never_increases_confidence():
    """Hypothesis: for random logits and T > 1, max softmax_t(logits, T) ≤ max softmax_t(logits, 1)."""


def test_softmax_sums_to_one_and_is_stable_for_large_logits():
    """Hypothesis: logits in [-1e4, 1e4] → finite probs summing to 1 ± 1e-6."""


def test_band_medium_between_threshold_and_high_cutoff():
    """τ ≤ p < max(τ, 0.90) → band 'medium'."""
