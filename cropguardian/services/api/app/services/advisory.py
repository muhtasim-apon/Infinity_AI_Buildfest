"""Advisory agent (owner: Raisa; retrieval: Salwa). Design: docs/ai/agent-design.md.

    cache lookup by (disease, crop, stage, kb_version)  → hit: return cached
    chunks = rag.retriever.retrieve(...)                → none / low score: fallback + escalate
    messages = rag.prompt.build_messages(...)
    raw = llm.complete(messages, timeout=LLM_TIMEOUT_MS, max_tokens=1500, temperature=0.2)
    result = rag.validator.validate(raw, chunks, BANNED)  → fail: retry once (V1 only), else 'blocked'
    return AdvisoryOut(status='ok', ...)

Failure modes → ``status``: LLM timeout/429/5xx → 'fallback' (cached or static agronomist card
for the disease); validator failure → 'blocked' (+ escalate to review queue).
Agent loop limits: ≤ 4 tool calls, 20 s, read-only tools + gated ``create_alert_draft``.
"""

from __future__ import annotations

from app.schemas.scan import AdvisoryOut


async def advise(disease_code: str, crop: str, stage: str | None, confidence_band: str,
                 coarse_lat: float | None, coarse_lon: float | None,
                 farmer_question: str | None = None) -> AdvisoryOut:
    raise NotImplementedError
