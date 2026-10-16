# ADR 0005 — Calibrated confidence with an honest "not sure"

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** whole team

## Context
A confident wrong diagnosis can lead a farmer to spray the wrong chemical or ignore a real outbreak.
Field photos differ from training photos (lighting, background, diseases outside our label set), and
neural-network softmax scores are usually over-confident. The team has no time to build a human
expert review step, so the system itself must be safe when it is uncertain.

## Decision
1. Calibrate with **temperature scaling** on the validation split; store T in `model_versions`.
2. Choose threshold τ from the **risk–coverage curve** so selective accuracy on validation meets the
   target in `docs/ai/eval-plan.md`; store τ (admin-tunable, audited).
3. Add an **out-of-distribution guard** (energy score) for non-leaf / non-rice photos.
4. If max calibrated probability < τ, or the OOD guard fires, or logits are invalid → status
   **`not_sure`**. The UI shows "নিশ্চিত নই / Not sure", **does not name a disease as the answer**, gives
   retake tips (one leaf, close, daylight), says "do not spray on a guess", and shows a static card to
   contact the local Upazila Agriculture Office. No advice is generated for not-sure results.

## Alternatives rejected
- **Always answer with the top class** — unsafe; hides uncertainty.
- **Human expert review queue** — out of scope (no time to build or staff it).

## Consequences
+ Trust: the system admits uncertainty. + No dependency on people being available.
− Coverage < 100 %; the not-sure rate is reported alongside accuracy, never hidden, and watched by the
weekly drift workflow. − The admin can raise τ instantly from `/admin` if a problem appears.
