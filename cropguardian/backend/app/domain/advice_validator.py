"""Validator for the advisory agent's JSON (Gantt P3, Salwa step 3). Pure logic.

Rules (each failure is a named code; the service retries once, then falls back to the static card):
  V1 shape     - exact keys, types and sizes
  V2 citations - non-empty, every id is one of the chunks actually retrieved for this scan
  V3 numbers   - every number in summary/steps appears verbatim in a cited chunk (no invented doses)
  V4 chemical  - `chemical` must be null and no pesticide product/class word may appear, because the
                 Bangladesh banned-ingredient list is not sourced yet (ml/rag/banned_ingredients.md)
  V5 language  - summary + steps are mostly Bangla script
  V6 injection - no URLs, markup or prompt-like text leaking from the model
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

KEYS = frozenset({"summary_bn", "steps_bn", "chemical", "safety_bn", "citations"})
MAX_STEPS = 6
MAX_STEP_CHARS = 280
MAX_SUMMARY_CHARS = 400
MIN_BANGLA_RATIO = 0.6

_BN_DIGITS = str.maketrans("".join(chr(0x09E6 + i) for i in range(10)), "0123456789")
_NUMBER = re.compile(r"[0-9\u09E6-\u09EF]+(?:[.,][0-9\u09E6-\u09EF]+)?")
_BANGLA = re.compile(r"[\u0980-\u09FF]")
_LETTER = re.compile(r"[\u0980-\u09FFA-Za-z]")
_INJECTION = re.compile(
    r"https?://|www\.|<\s*/?\s*(source|script|system)|ignore (all|previous)|system prompt",
    re.IGNORECASE,
)
# Product and class words that must not appear in farmer-facing steps while V4 is in force.
# Product names are the ones seen in the BRRI factsheets plus common actives; extend, never shrink.
BLOCKED_TERMS = (
    "ছত্রাকনাশক", "কীটনাশক", "কৃমিনাশক", "বালাইনাশক", "ট্রুপার", "নেটিভো", "জিল", "টিল্ট",
    "ব্যাভিস্টিন", "ফুরাডান", "কুরাটার", "থিওভিট", "কার্বোফুরান", "কার্বেন্ডাজিম", "ট্রাইসাইক্লাজল",
    "fungicide", "pesticide", "insecticide", "nematicide", "carbofuran", "carbendazim",
    "tricyclazole", "furadan", "bavistin", "tilt", "nativo", "trooper",
)  # fmt: skip


def normalise_number(raw: str) -> str:
    return raw.translate(_BN_DIGITS).replace(",", ".")


def numbers_in(text: str) -> set[str]:
    return {normalise_number(m) for m in _NUMBER.findall(text or "")}


def bangla_ratio(text: str) -> float:
    letters = _LETTER.findall(text)
    if not letters:
        return 0.0
    return len(_BANGLA.findall(text)) / len(letters)


def validate(advice: Any, retrieved: Mapping[str, str]) -> list[str]:
    """Return a list of failed rule codes (empty = valid). `retrieved` maps chunk id -> text."""
    if not isinstance(advice, dict) or set(advice) != KEYS:
        return ["V1_shape"]
    summary, steps = advice["summary_bn"], advice["steps_bn"]
    safety, citations = advice["safety_bn"], advice["citations"]
    if (
        not isinstance(summary, str)
        or not 1 <= len(summary.strip()) <= MAX_SUMMARY_CHARS
        or not isinstance(safety, str)
        or len(safety) > MAX_SUMMARY_CHARS
        or not isinstance(steps, list)
        or not 1 <= len(steps) <= MAX_STEPS
        or not all(isinstance(s, str) and 1 <= len(s.strip()) <= MAX_STEP_CHARS for s in steps)
        or not isinstance(citations, list)
        or not all(isinstance(c, str) for c in citations)
    ):
        return ["V1_shape"]

    errors: list[str] = []
    cited = [c for c in citations if c in retrieved]
    if not citations or len(cited) != len(citations):
        errors.append("V2_citations")

    body = " ".join([summary, *steps])
    cited_numbers: set[str] = set()
    for chunk_id in cited:
        cited_numbers |= numbers_in(retrieved[chunk_id])
    if numbers_in(body) - cited_numbers:
        errors.append("V3_numbers")

    lowered = (body + " " + safety).lower()
    if advice["chemical"] is not None or any(term in lowered for term in BLOCKED_TERMS):
        errors.append("V4_chemical")

    if bangla_ratio(body) < MIN_BANGLA_RATIO:
        errors.append("V5_language")

    if _INJECTION.search(body + " " + safety):
        errors.append("V6_injection")
    return errors
