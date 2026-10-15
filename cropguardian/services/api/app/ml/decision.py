"""Calibrated decision: answer or abstain (ADR 0005). Safety-critical → 100 % branch coverage
required (tests/whitebox/test_decision.py).

    probs = softmax(logits / T)
    if any(not finite(logits))            → abstain (reason "invalid_logits")
    if ood_score(logits) > ood_threshold  → abstain (reason "out_of_distribution")
    if max(probs) <  τ                     → abstain (reason "low_confidence")
    if max(probs) >= τ                     → diagnose   (boundary: exactly τ diagnoses)

Confidence band shown to farmers (never raw probability alone):
    high ≥ max(τ, 0.90) · medium ≥ τ · low < τ (abstained)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import numpy.typing as npt

AbstainReason = Literal["invalid_logits", "out_of_distribution", "low_confidence"]


@dataclass(frozen=True)
class Decision:
    abstained: bool
    reason: AbstainReason | None
    top3: list[tuple[int, float]]       # (class index, calibrated prob)
    band: Literal["high", "medium", "low"]


def softmax_t(logits: npt.NDArray[np.float32], temperature: float) -> npt.NDArray[np.float64]:
    """Numerically stable temperature softmax. ``temperature`` > 0."""
    raise NotImplementedError


def energy_score(logits: npt.NDArray[np.float32], temperature: float = 1.0) -> float:
    """OOD energy: ``-T * logsumexp(logits / T)``; higher = more out-of-distribution."""
    raise NotImplementedError


def decide(logits: npt.NDArray[np.float32], temperature: float, threshold: float, ood_threshold: float) -> Decision:
    raise NotImplementedError
