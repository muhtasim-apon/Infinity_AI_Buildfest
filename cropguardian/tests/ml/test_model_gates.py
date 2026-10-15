"""ML release gates — values from docs/ai/eval-plan.md §1. Run per model release against the
held-out split; reads the evaluation report JSON, never recomputes on training data."""

import pytest

pytestmark = pytest.mark.skip("stub — needs trained model + report")


def test_macro_f1_gate(): """report.test.macro_f1 ≥ 0.85 (lower CI bound reported alongside)."""
def test_notifiable_recall_gate(): """recall for blast, bacterial_leaf_blight, tungro ≥ 0.85 each."""
def test_calibration_gate(): """ECE after temperature scaling ≤ 0.05."""
def test_int8_parity_gate(): """top-1 agreement int8 vs fp32 ≥ 0.99 on validation."""
def test_latency_gate(): """CPU p95 ≤ 1000 ms single image, intra_op_num_threads=1."""
def test_slice_floor(): """no slice recall for a notifiable disease < overall − 0.10 unless listed in model card limitations."""
