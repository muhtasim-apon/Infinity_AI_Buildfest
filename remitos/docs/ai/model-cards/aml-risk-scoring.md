# Model Card — AML Risk Scoring

**Status:** Specification (not trained) · **Owner:** Business Analyst / Data Scientist
**Pack:** borderless_money · **Code:** `ml/models/aml_risk_scoring/`

---

## Intended use

Score a transfer for money-laundering risk, to **prioritise human review**. The score
orders an officer's queue. It does not decide.

| Score | Action |
|---|---|
| < 0.40 | Allow, with reason code and audit event |
| 0.40 – 0.70 | Enhanced automated checks, RAG-grounded agent investigation |
| > 0.70 | **Mandatory human gate** (ADR 0010) |
| Any sanctions hit | **Block + human**, regardless of score |

## Out-of-scope use

- **Never** as the sole basis for blocking a transfer or closing an account
- Never for credit decisions, employment, insurance, or any purpose outside AML triage
- Never applied to a corridor it was not evaluated on
- Never used to score a person rather than a transaction

## Training data

| | |
|---|---|
| Source | Internal transaction history with officer adjudications |
| Split | **Temporal** — train on earlier period, test on later. Never random |
| Labels | Officer-adjudicated outcomes, not model-generated |
| Class balance | Severely imbalanced; handled by cost-sensitive learning, not by resampling the test set |
| Cold start | Pre-launch, the model does not exist. The system operates rules-only (degradation level 3) until sufficient adjudicated volume accumulates. **This is stated plainly rather than solved with synthetic labels.** |

## Features

Behavioural (velocity, amount deviation from personal baseline, timing anomaly, dormancy
break) · Network, from the entity graph (beneficiary in-degree, shared-device count,
path length to a flagged entity, agent concentration) · Corridor risk baseline ·
Account tenure · Document verification quality · Structuring proximity (clustering just
below reporting thresholds).

**Deliberately excluded:** name, ethnicity, religion, and any direct demographic
attribute. Note that exclusion is not sufficient — proxies remain, which is why the
fairness evaluation below is mandatory rather than advisory.

## Evaluation

| Metric | Target |
|---|---|
| Recall at fixed review capacity | ≥ 0.90 |
| Precision at operating threshold | ≥ 0.35 (triage, not verdict) |
| Calibration (ECE) | ≤ 0.05 |
| Officer agreement on top decile | ≥ 0.85 |

### Fairness — release gates, not report lines

Evaluated on gender · age band · division (rural/urban) · corridor · transfer-size band ·
account tenure · **device tier**.

| Gate | Threshold |
|---|---|
| False-positive rate ratio, worst group vs best | ≤ 1.25 |
| Equal opportunity difference | ≤ 0.05 |
| Demographic parity difference | ≤ 0.05 |

**Why device tier is called out.** It is a wealth proxy. A model that flags older, cheaper
Android handsets learns to penalise poverty and will do so while reporting excellent
aggregate accuracy. This is the single most likely way this model becomes unjust.

## Known limitations

1. **Cold start.** No model at launch. Rules-only until adjudicated volume exists.
2. **Label bias.** Trained on officer decisions, which carry their own historical bias.
   The model can only reproduce and amplify that; it cannot correct it. Mitigated by
   periodic blind re-adjudication of a random sample, including of cases the model
   passed.
3. **Adversarial adaptation.** Laundering typologies change deliberately in response to
   detection. Performance decays by design, not by accident — hence continuous drift
   monitoring rather than annual revalidation.
4. **Novel typologies are invisible.** The model detects what resembles the past. New
   patterns are caught by graph anomaly detection and by officers, not by this model.
5. **Class imbalance** makes precision inherently low. This is correct for a triage tool
   and must not be "improved" by raising the threshold until the queue looks clean.

## Ethical considerations

The harm is asymmetric and falls on people with the least recourse. A false positive
holds a transfer that was often for medicine, school fees or rent, affecting someone with
no relationship manager to call and frequently no way to learn why.

Consequently:

- Every hold produces a **plain-Bangla explanation** and a stated SLA
- Every hold is appealable to a human, and the appeal route is visible in the app
- Group-wise false-positive rates are monitored continuously in production, not only at
  training time
- A sustained FPR ratio above 1.25 for any group triggers **model rollback**, not a
  backlog ticket

## Maintenance

Retrain quarterly or on drift. Promotion requires all gates, a complete card, a tested
rollback, and human approval (ADR 0010, L3). Rollback is a config flip to the previous
version, exercised in staging every release.
