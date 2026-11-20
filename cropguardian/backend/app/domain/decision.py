"""Turn a vision-model answer into diagnosed / healthy / not_sure (Gantt P2 step 3). Pure logic.

Honesty rules encoded here:
- the model's confidence is SELF-REPORTED and uncalibrated (no labelled eval set exists yet), so the
  app never shows a percentage; it shows a coarse band and abstains below a fixed threshold;
- anything outside the knowledge base (other crops, unknown diseases) is "not sure", never a guess;
- a malformed model answer is "not sure", never an exception shown to the farmer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

ABSTAIN_BELOW = 0.60  # self-reported confidence under this => not_sure
HIGH_FROM = 0.80  # band boundary between medium and high
HEALTHY = "healthy"
SUPPORTED_CROP = "rice"

REASONS = frozenset(
    {
        "model_error",
        "not_rice",
        "poor_image",
        "unknown_disease",
        "low_confidence",
        "not_a_plant",
    }
)


@dataclass(frozen=True)
class Decision:
    status: str  # diagnosed | healthy | not_sure
    disease: str | None = None
    band: str | None = None  # high | medium (only when diagnosed/healthy)
    reason: str | None = None  # one of REASONS (only when not_sure)
    crop: str | None = None


def _not_sure(reason: str, crop: str | None = None) -> Decision:
    if reason not in REASONS:
        raise ValueError("unknown reason")
    return Decision(status="not_sure", reason=reason, crop=crop)


def _confidence(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    number = float(value)
    if math.isnan(number) or number < 0 or number > 1:
        return None
    return number


def band_for(confidence: float) -> str:
    return "high" if confidence >= HIGH_FROM else "medium"


def decide(answer: Any, known_diseases: frozenset[str]) -> Decision:  # noqa: PLR0911
    """`answer` is the parsed JSON from the vision model (untrusted). Never raises."""
    if not isinstance(answer, dict):
        return _not_sure("model_error")
    crop_raw = answer.get("crop")
    crop = crop_raw.strip().lower()[:40] if isinstance(crop_raw, str) else None
    quality = answer.get("image_quality")
    confidence = _confidence(answer.get("confidence"))
    disease_raw = answer.get("disease")
    disease = disease_raw.strip().lower() if isinstance(disease_raw, str) else None

    if crop is None or confidence is None or disease is None:
        return _not_sure("model_error", crop)
    if crop in ("none", "not_a_plant", "unknown_object"):
        return _not_sure("not_a_plant")
    if quality == "poor":
        return _not_sure("poor_image", crop)
    if crop != SUPPORTED_CROP:
        return _not_sure("not_rice", crop)
    if disease != HEALTHY and disease not in known_diseases:
        return _not_sure("unknown_disease", crop)
    if confidence < ABSTAIN_BELOW:
        return _not_sure("low_confidence", crop)
    if disease == HEALTHY:
        return Decision(status="healthy", band=band_for(confidence), crop=crop)
    return Decision(status="diagnosed", disease=disease, band=band_for(confidence), crop=crop)
