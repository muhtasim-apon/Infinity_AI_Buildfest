"""Advice validator (ADR 0006). Safety-critical → 100 % branch coverage
(tests/whitebox/test_advisory_validator.py). Rules, all must pass:

  V1 output parses into the AdvisoryOut JSON schema
  V2 len(citations) ≥ 1
  V3 every cited id ∈ ids of the retrieved chunks
  V4 if chemical: its ``dose`` string occurs verbatim (after Unicode NFC + whitespace
     normalisation) in at least one cited chunk
  V5 no banned active ingredient anywhere in the output (case-insensitive, bn + en names)
  V6 if chemical: ``safety_bn`` non-empty
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.rag.retriever import Chunk

RuleId = Literal["V1", "V2", "V3", "V4", "V5", "V6"]


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    failed: tuple[RuleId, ...]


def validate(raw_output: str, retrieved: list[Chunk], banned_ingredients: frozenset[str]) -> ValidationResult:
    raise NotImplementedError
