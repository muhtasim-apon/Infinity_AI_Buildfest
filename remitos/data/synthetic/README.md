# Synthetic Data

Generator **specifications**. No generated data is committed.

## The rule that governs this folder

Congress section 20.4 prohibits "fabricated demos, fake or simulated results" presented
as real. Synthetic data for a demo is legitimate; presenting it as real is not.

Therefore: **every surface that renders synthetic data displays a persistent label.**
Not a footnote, not a disclaimer on slide 12 - a visible marker on the screen itself.

## Generators

| Generator | Produces | Notes |
|---|---|---|
| `senders.py` | Sender profiles across corridors | Names from a synthetic name bank, never real people |
| `transfers.py` | Transfer history with realistic seasonality | Eid, payday and harvest cycles; includes **failed legs** |
| `beneficiaries.py` | Recipients with rural/urban distribution | Matched to real division population weights |
| `fraud_cases.py` | Labelled fraud typologies | For pipeline testing only - **never for reported accuracy figures** |
| `partner_statements.py` | Settlement statements with deliberate breaks | Exercises reconciliation |

## Constraints

- No real NID numbers, real names, or real account numbers - ever, including in tests.
  CI scans fixtures for PII patterns.
- Distributions are documented so a reader can judge whether the demo is representative.
- **Synthetic data never produces a quoted metric.** A model accuracy figure derived
  from synthetic labels is a fabricated result, and quoting one would be disqualifiable.

Stubs only.
