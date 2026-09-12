"""Compliance decision engine — cite or refuse.

STUB. Never executed. Signatures and contracts only.

THE STANDARD
------------
Every decision this module produces must be defensible to a supervisor years later.
That means each verdict carries:

    * a reason code,
    * the citations it relied on, with effective dates,
    * the model version in force,
    * and — where a human decided — who, when, and what evidence they were shown.

A fluent, uncited compliance opinion is worse than no opinion: it manufactures a
decision the institution cannot defend. See ADR 0004 and docs/security/aml-kyc-policy.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

__all__ = ["Verdict", "ReasonCode", "Citation", "ComplianceDecision", "DecisionEngine"]


class Verdict(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"      # -> human queue
    BLOCK = "block"        # -> human queue + report consideration
    NOT_FOUND = "not_found"  # no governing rule retrievable -> human. Never a guess.


class ReasonCode(str, Enum):
    """Machine-stable reason codes. The user-facing text is generated separately, in
    Bangla, and must never be a rendering of the enum name."""

    CLEAR = "clear"
    SANCTIONS_HIT = "sanctions_hit"
    PEP_MATCH = "pep_match"
    ADVERSE_MEDIA = "adverse_media"
    AMOUNT_THRESHOLD = "amount_threshold"
    VELOCITY_ANOMALY = "velocity_anomaly"
    NEW_BENEFICIARY_HIGH_VALUE = "new_beneficiary_high_value"
    STRUCTURING_PATTERN = "structuring_pattern"
    NETWORK_PROXIMITY = "network_proximity"
    DOCUMENT_QUALITY = "document_quality"
    CORRIDOR_RISK = "corridor_risk"
    RULE_NOT_FOUND = "rule_not_found"


@dataclass(frozen=True, slots=True)
class Citation:
    """A retrieved passage supporting a decision.

    ``effective_from``/``effective_to`` are not decoration. Retrieval filters on
    effective date *before* searching, because last year's circular is not merely
    irrelevant — applying it is wrong, and citing it makes the error look authoritative.
    """

    document_id: str
    authority: str          # "Bangladesh Bank" | "BFIU" | "FATF" | partner
    section: str            # e.g. "BRPD Circular 14/2025 § 3.2(b)"
    effective_from: datetime
    effective_to: datetime | None
    retrieval_score: float
    excerpt: str
    language: str           # "bn" | "en" — many circulars are Bangla-only


@dataclass(slots=True)
class ComplianceDecision:
    """A defensible verdict."""

    verdict: Verdict
    reason_codes: list[ReasonCode]
    citations: list[Citation]
    risk_score: float | None
    model_version: str | None

    #: Plain Bangla, written for the person affected. "পরিমাণ এবং হিসাবটি নতুন হওয়ায়
    #: আমরা যাচাই করছি" — not "risk score 0.73", which discloses without explaining.
    explanation_bn: str = ""
    explanation_en: str = ""

    #: Evidence presented to the human, snapshotted at decision time. Re-deriving it
    #: later is not equivalent: a decision can only be judged against what the decider
    #: actually saw. See docs/security/audit-readiness.md §1.
    evidence_snapshot: dict = field(default_factory=dict)

    #: Contradictory findings, kept deliberately. A bundle that presents only the
    #: supporting evidence persuades rather than informs, and a human gate that only
    #: ever agrees is a rubber stamp with a name attached.
    contradictions: list[str] = field(default_factory=list)

    human_required: bool = False
    decided_by: str | None = None
    decided_at: datetime | None = None
    decision_rationale: str | None = None


class DecisionEngine:
    """Produces compliance verdicts for transfers."""

    async def decide(
        self,
        *,
        transfer_id: str,
        sender_id: str,
        beneficiary_id: str,
        amount_usd_equivalent: float,
        corridor: str,
        as_of: datetime | None = None,
    ) -> ComplianceDecision:
        """Evaluate a transfer.

        TODO(compliance): implement in this order. Order matters — screening precedes
        scoring so that a sanctions hit is never diluted by a low model score.

        1. **Sanctions screening.** Deterministic matching: exact, phonetic,
           transliteration-aware, fuzzy. NOT semantic similarity — it is the wrong tool
           for names and produces both misses and unexplainable hits.

           Bangla-English transliteration is non-deterministic: রহিমা romanises as
           Rahima, Rohima or Rahema, all legitimately. Exact string matching would both
           miss real hits and generate unfair false positives against ordinary people.

           **Any hit -> BLOCK + human. No exceptions, whatever the confidence.**

        2. **Travel Rule.** At or above TRAVEL_RULE_THRESHOLD_USD, attach originator and
           beneficiary data. Log the disclosure with its legal basis — it is an
           obligation, not a residency breach (ADR 0011 §6).

        3. **AML risk model.** Score. Record the model version with the score; a score
           without a version cannot be reproduced or challenged later.

        4. **Rule retrieval.** Query rag-service for the governing rule, filtered to
           rules effective at ``as_of``. If nothing clears RAG_MIN_CITATION_SCORE,
           return Verdict.NOT_FOUND and escalate. **Never generate an ungrounded
           compliance opinion.**

        5. **Band the verdict.**
             score < 0.40           -> ALLOW
             0.40 <= score <= 0.70  -> REVIEW (agent investigates, drafts only)
             score > 0.70           -> BLOCK/REVIEW with a mandatory human gate

        6. **Explain.** Generate ``explanation_bn`` in Bangla for the affected user, and
           assemble the officer evidence bundle — **including contradictions**.

        7. **Audit.** Emit ``compliance.decided`` with the full decision, citations and
           evidence snapshot.

        Note on ``as_of``: it exists so a historical decision can be re-evaluated against
        the rules that were actually in force at the time. Without it, an audit
        re-run silently applies today's rules to last year's transfer and concludes the
        original decision was wrong.

        Returns:
            ComplianceDecision. Never raises on an inconclusive result — inconclusive is
            a verdict (NOT_FOUND) that routes to a human, not an exception that a caller
            might swallow.
        """
        raise NotImplementedError("Stub — see TODO above.")
