# Pilot protocol (pre-registration draft) — field-level loss reduction

Status: **draft** — finalise with the partner extension office before any data collection.

## Question
Does access to Crop Guardian (with agronomist loop) shorten time-to-correct-treatment and reduce
disease-affected area / yield loss compared with usual practice?

## Design
- Matched comparison: pilot farmers vs comparison farmers in neighbouring blocks, same variety and season.
- Unit: field. Sample size: decided with the partner from available farmers; power analysis recorded here before start.
- Duration: one season.

## Outcomes (pre-declared)
Primary: days from first symptom report to correct treatment (agronomist-verified).
Secondary: affected area at a fixed growth stage (agronomist estimate); yield per decimal at
harvest; number of pesticide applications.

## Analysis
Difference in medians with bootstrap CI; regression adjusting for variety, sowing date, area.
All results reported, including null results.

## Ethics
Informed consent in Bangla; farmers can withdraw anytime; no farmer is denied usual extension
services; data handled per `docs/security/privacy.md`.
