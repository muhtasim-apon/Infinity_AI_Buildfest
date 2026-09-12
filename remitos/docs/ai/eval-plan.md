# AI Evaluation Plan

> The Congress asks judges to assess "explainability of the intelligence core" (§14) and
> scores Responsible AI as a full component (§11.1). Evaluation is how that claim becomes
> checkable rather than asserted.

## 1. Principle

**Nothing reaches production on a demo.** Every model and every agent has a golden set, a
target, and a regression gate. A model whose evaluation is "it looked right in testing"
is not a model, it is a guess with a version number.

## 2. What is evaluated, and against what

| Component | Golden set | Primary metric | Gate |
|---|---|---|---|
| Corridor cost predictor | Held-out corridor-quarter observations | MAPE on landed cost | ≤ 8 % |
| ETA predictor | Historical settlement times by rail | p90 absolute error | ≤ 30 min |
| FX forecaster | Walk-forward backtest, no look-ahead | Directional accuracy | ≥ 58 % |
| Fraud model | Labelled cases, temporally split | Recall @ 1 % FPR | ≥ 0.85 |
| AML risk model | Officer-adjudicated alerts | Recall @ fixed review capacity | ≥ 0.90 |
| Doc intelligence (NID OCR) | Annotated documents, incl. poor scans | Field-level exact match | ≥ 0.97 |
| Bangla NLU | Dialect-stratified utterances | Intent F1, per dialect | ≥ 0.88 each |
| RAG | Regulatory Q&A with gold citations | Citation precision | **1.00** |
| Agents | Scenario suite with rubric | Officer agreement | ≥ 0.90 |

**Temporal splits, never random.** A random split on transaction data leaks the future
into the training set and produces a model that evaluates beautifully and fails in
production. Every split in this project is by time.

## 3. Fairness and bias

Congress §15 requires active bias detection and mitigation. Vague commitment is not
mitigation; the following is.

**Protected and proxy dimensions** evaluated on every risk-bearing model: gender ·
age band · division/district (rural vs urban) · corridor of origin · transfer size band ·
account tenure · device tier.

That last one matters more than it looks. **Device tier is a wealth proxy.** A model that
scores older, cheaper Android devices as higher-risk has learned to penalise poverty, and
it will do so with excellent overall accuracy. This is the most likely way this system
becomes unfair, and it is checked explicitly.

| Fairness metric | Target |
|---|---|
| Demographic parity difference | ≤ 0.05 |
| Equal opportunity difference (TPR gap) | ≤ 0.05 |
| False-positive rate ratio, worst vs best group | ≤ 1.25 |

**The false-positive asymmetry is the ethical core of this product.** A false positive on
an AML model is not a statistic — it is a held transfer. The money was often for medicine
or school fees. The person affected has no recourse, no relationship manager, and
frequently no way to find out why. A 2 % false-positive rate concentrated on rural, older,
low-device-tier recipients is not an acceptable model; it is discrimination with a
confusion matrix. Group-wise FPR is therefore a **release gate**, not a report line.

## 4. Explainability

| Requirement | Mechanism |
|---|---|
| Every money-affecting decision has a reason code | Enforced in the service contract |
| Tabular model attribution | SHAP, stored with the prediction |
| RAG attribution | Citations, verified by the claim checker |
| Officer-facing explanation | Evidence bundle plus subgraph diagram |
| **User-facing explanation** | **Plain Bangla, no jargon, no numbers unless they help** |

The last row is the hardest and the most important. "Your transfer is being checked
because of the amount and how recently the account was opened — this usually takes two
hours" is an explanation. "Risk score 0.73" is a disclosure that explains nothing to
the person it is about.

## 5. Drift monitoring

| Type | Detection | Action |
|---|---|---|
| Data drift | PSI > 0.2 on any top-10 feature | Alert, investigate |
| Concept drift | Rolling performance below gate | Freeze auto-decisions, widen human review |
| Prediction drift | Output distribution shift | Alert |
| Corpus drift | New/superseded circular ingested | Re-run RAG regression |

Owned by n8n workflow 09. On concept drift the system **steps down the degradation
ladder** rather than continuing to decide confidently on a stale model.

## 6. Model cards and release gates

Every model ships with a card in `docs/ai/model-cards/`: intended use, out-of-scope use,
training data and its date range, evaluation results including per-group, known
limitations, ethical considerations, and an owner.

A model may be promoted only when: all primary gates pass · all fairness gates pass ·
the card is complete and reviewed · a rollback is tested · a human approves the
promotion (ADR 0010, L3).

**No model is promoted on aggregate accuracy alone.** A model that is 96 % accurate
overall and 78 % accurate for rural women over 50 has failed, and it will pass any
single-number gate you set.
