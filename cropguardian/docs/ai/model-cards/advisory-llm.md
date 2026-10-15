# Model card — Advisory LLM (RAG)

**Status:** Specification · **Risk tier:** High · **Code:** `services/api/app/services/advisory.py`, `services/api/app/rag/`

## Intended use
Turn a diagnosis plus retrieved DAE/BRRI/BARI text into short, cited, Bangla advice.

## Model
Default `claude-sonnet-5-5` via Anthropic API; provider-swappable (`LLM_PROVIDER`). Selection
logic: Bangla quality, JSON reliability, latency, cost; re-evaluated on the golden set when
switching. Temperature 0.2. Max output 1,500 tokens.

## Inputs / outputs
In: disease, crop, stage, weather summary, ≤ 8 source chunks, optional farmer question (data only).
Out: JSON `{summary_bn, steps_bn[], chemical|null, safety_bn, citations[]}`. **No personal data in.**

## Evaluation
See `docs/ai/eval-plan.md` §3 — citation coverage 1.00, banned leakage 0, red-team 0 (hard gates).

## Limitations
Quality bounded by KB coverage; Bangla OCR errors in sources propagate; may be overly cautious
(escalates often) — acceptable trade-off.

## Ethical considerations
Safety advice; IPM-first ordering; never recommends dose not in source; disclaimers.
