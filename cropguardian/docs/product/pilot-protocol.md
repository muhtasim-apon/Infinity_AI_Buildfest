# Pilot protocol (pre-registration draft) — field-level loss reduction

Status: **draft** — finalise with the partner extension office before any data collection.

## Question
Does access to Crop Guardian shorten time-to-correct-treatment and reduce
disease-affected area / yield loss compared with usual practice?

## Design
- Matched comparison: pilot farmers vs comparison farmers in neighbouring blocks, same variety and season.
- Unit: field. Sample size: decided with the partner from available farmers; power analysis recorded here before start.
- Duration: one season.

## Outcomes (pre-declared)
Primary: yield per decimal at harvest.
Secondary: days from first symptom to correct treatment (farmer's field diary, checked against the
cited guide); affected area at a fixed growth stage (photo-based estimate by the team); number of
pesticide applications; alert lead time vs official reports.
Sample size and expected effect: see [`docs/evaluation/field-loss-reduction.md`](../evaluation/field-loss-reduction.md) §4 and §6.

## Analysis
Difference in medians with bootstrap CI; regression adjusting for variety, sowing date, area.
All results reported, including null results.

## Ethics
Informed consent in Bangla; farmers can withdraw anytime; no farmer is denied usual extension
services; data handled per `docs/security/privacy.md`.
