# Model Card - Churn and Lifetime Value

**Status:** Specification (not trained) · **Risk tier:** Low
**Pack:** core · **Code:** `ml/models/churn_ltv/`

---

## Intended use

Internal analytics. Estimate the probability a sender lapses and their expected lifetime
contribution, to inform retention work and to keep the unit-economics model in
`docs/product/prd.md` grounded in observed behaviour rather than assumption.

## Out-of-scope use

This is the model most likely to be misused, so the boundaries are explicit:

- **Never used to price differentially by predicted value.** Charging a high-LTV user
  more, or a price-sensitive user less, is discriminatory pricing on a remittance
  product used by people sending subsistence income. It is prohibited here.
- Never used to deprioritise support for low-value users.
- Never used in a risk or compliance decision.
- Never exposed to users.

## Training data

Own transaction and engagement history, temporally split. Churn defined as no transfer
for 2x the user's own median inter-transfer interval, which respects that a quarterly
sender is not a lapsed monthly sender.

## Features

Transfer frequency and its trend, amount trend, corridor, tenure, support-contact count,
failed-transfer count, competitor promotional periods, and seasonality.

## Evaluation

| Metric | Target |
|---|---|
| Churn AUC | >= 0.78 |
| LTV MAPE (12-month) | <= 25 % |
| Calibration (ECE) | <= 0.07 |

Evaluated for group differences so that retention effort is not systematically directed
away from rural or low-value users - a self-fulfilling prophecy in which the model
predicts churn, the business withdraws attention, and churn duly follows.

## Known limitations

1. Remittance behaviour is driven by external events - job loss, visa expiry, a family
   emergency - that the model cannot observe.
2. Migration cycles produce long gaps that are not churn.
3. Cold start until a full seasonal cycle is observed.

## Ethical considerations

A failed transfer is one of the strongest churn predictors, which points the correct
intervention at fixing failures rather than at discounting. Retention work informed by
this model must improve the product, not target individuals with pricing.

## Maintenance

Retrain quarterly. Internal use only; no user-facing surface.
