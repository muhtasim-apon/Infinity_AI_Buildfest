# Model Cards

Every model referenced anywhere in this repository has a card here **before** it is
referenced. A model without a card does not exist as far as the architecture is
concerned.

| Model | Card | Purpose | Risk tier |
|---|---|---|---|
| AML risk scoring | [aml-risk-scoring.md](aml-risk-scoring.md) | Prioritise human AML review | **High** |
| Fraud detection | [fraud-detection.md](fraud-detection.md) | Real-time transaction defence | **High** |
| Corridor cost predictor | [corridor-cost-predictor.md](corridor-cost-predictor.md) | Predict landed cost and ETA per rail | Medium |
| FX forecasting | [fx-forecasting.md](fx-forecasting.md) | Send-timing advice | Medium |
| Document intelligence | [doc-intelligence.md](doc-intelligence.md) | NID/passport OCR and extraction | **High** |
| Bangla NLU | [bangla-nlu.md](bangla-nlu.md) | Intent, ASR and TTS for voice flows | Medium |
| Recipient recommender | [recipient-recommender.md](recipient-recommender.md) | Reduce entry errors and friction | Low |
| Churn / LTV | [churn-ltv.md](churn-ltv.md) | Retention and unit-economics analytics | Low |

## Risk tiers

| Tier | Definition | Requirements |
|---|---|---|
| **High** | Output can deny a person access to their money, or misidentify them | Full fairness gates · mandatory human gate · appeal route · continuous group-wise monitoring · quarterly blind re-adjudication |
| **Medium** | Output shapes a recommendation the user can override | Fairness evaluation · explainability · drift monitoring |
| **Low** | Output affects convenience or internal analytics only | Drift monitoring · documented limitations |

## Card template

Required sections, in order: **Intended use · Out-of-scope use · Training data ·
Features · Evaluation (including fairness) · Known limitations · Ethical considerations ·
Maintenance.**

Two rules that make cards honest rather than decorative:

1. **"Known limitations" may not be empty.** A card claiming no limitations has not been
   written, it has been skipped.
2. **Fairness results are stated per group, never as an aggregate.** An aggregate hides
   exactly the failure the section exists to expose.
