# Model Card — Fraud Detection

**Status:** Specification (not trained) · **Risk tier:** High
**Pack:** borderless_money · **Code:** `ml/models/fraud_detection/`

---

## Intended use

Real-time scoring of a transfer for **fraud against the user** — account takeover,
social-engineering ("your son is in hospital, send money now"), agent collusion, and
mule-account payout. Distinct from AML, which is fraud *through* the system rather than
*against* the customer.

| Score | Action |
|---|---|
| < 0.30 | Proceed |
| 0.30 – 0.65 | Step-up authentication; for social-engineering signals, a Bangla scam-warning interstitial |
| > 0.65 | Hold, notify the user on a second channel, human review |

## Out-of-scope use

Not an AML model (separate card, separate objective). Not a creditworthiness signal.
Never used to close an account without human review.

## Training data

Own confirmed-fraud cases and disputes, temporally split. Labels come from confirmed
outcomes, not suspicion. Heavily imbalanced; cost-sensitive learning with an explicit
asymmetric cost matrix — a missed takeover costs a user their savings, a false positive
costs them minutes.

**Cold start is severe here**: a new product has no fraud history and fraudsters find new
products quickly. Launch operates on deterministic rules plus graph anomaly detection,
with a widened human-review band, until labelled volume exists.

## Features

Device fingerprint and change history · behavioural biometrics (typing cadence, hesitation
on the amount field) · session anomaly · **new-beneficiary + high-amount + urgency
combination** (the social-engineering signature) · geo-velocity · graph features from
Neo4j (mule-network proximity, beneficiary in-degree) · time-of-day deviation from the
user's own baseline.

## Evaluation

| Metric | Target |
|---|---|
| Recall @ 1 % false-positive rate | ≥ 0.85 |
| Detection latency | ≤ 150 ms p95 (synchronous path) |
| Calibration (ECE) | ≤ 0.05 |

Fairness gates as per `docs/ai/eval-plan.md`, with device tier and age band watched most
closely: **elderly users on old handsets are simultaneously the most-targeted victims and
the group most likely to be flagged by proxy.** Getting this wrong penalises the people
the model exists to protect.

## Known limitations

1. Adversarial and adaptive — performance decays by design; continuous retraining assumed.
2. Social engineering leaves few *technical* signals; the victim authenticates
   legitimately. Behavioural and contextual signals carry most of the weight, and they
   are weak individually.
3. Cannot detect fraud that completes outside the platform.
4. False positives block genuine emergency transfers, which is the worst possible timing.

## Ethical considerations

The scam-warning interstitial must warn without paternalising, and must be dismissible —
an adult sending their own money is entitled to do so after being informed. Warnings are
in Bangla, concrete ("Have you spoken to this person by voice today?"), and never
repeated so often that users learn to tap through them.

## Maintenance

Retrain monthly or on drift; emergency retrain on a new confirmed typology.
