# ADR 0005 — Calibrated confidence with abstain → human review

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** whole team

## Context
A confident wrong diagnosis can lead a farmer to spray the wrong chemical or ignore a real
outbreak. Field photos differ from training photos (lighting, background, other diseases not in
our label set). Softmax scores of neural networks are typically over-confident.

## Decision
1. Calibrate with **temperature scaling** on the validation split; record T in `model_versions`.
2. Choose threshold τ from the **risk–coverage curve** so that selective accuracy on validation
   meets the target agreed in `docs/ai/eval-plan.md`; record τ.
3. If max calibrated probability < τ, or the "is it a leaf?" check fails → status
   `needs_review`, UI says "নিশ্চিত নই — কৃষি কর্মকর্তার কাছে পাঠানো হয়েছে" (not sure — sent to an
   agronomist). No disease name is shown as an answer.
4. Agronomist verdicts become labels (data flywheel).

## Consequences
+ Trust: the system admits uncertainty. + Generates the hardest, most valuable labels.
− Needs agronomist capacity → partner with DAE/university agronomy dept; queue SLA shown.
− Coverage < 100 % — reported alongside accuracy, never hidden.
