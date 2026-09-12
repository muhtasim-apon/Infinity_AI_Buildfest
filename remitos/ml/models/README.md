# Models

Eight models. Each has a card in `docs/ai/model-cards/` **before** it is referenced
anywhere else - a model referenced in code without a card fails the build.

| Model | Risk tier |
|---|---|
| `aml_risk_scoring/` · `fraud_detection/` · `doc_intelligence/` | **High** |
| `corridor_cost_predictor/` · `fx_forecasting/` · `bangla_nlu/` | Medium |
| `recipient_recommender/` · `churn_ltv/` | Low |

Specifications only. Nothing trained. No artefacts committed.
