# Model Card — FX Forecasting

**Status:** Specification (not trained) · **Risk tier:** Medium
**Pack:** borderless_money · **Code:** `ml/models/fx_forecasting/`

---

## Intended use

Forecast short-horizon BDT exchange-rate movement (24h–7d) for the major sending
corridors, to produce **send-timing guidance**: "waiting until tomorrow may be worth
about Tk 400 on this amount — or it may not."

Output is advice the user may ignore. It never delays a transfer automatically.

## Out-of-scope use

- **Not investment advice.** Not a speculation tool, not a hedging product for users.
- Never used to auto-defer a transfer. A remittance is usually needed *now*, and a model
  that delays medicine money to capture 30 basis points has misunderstood the product.
- Not valid across a policy break (devaluation, regime change) — see limitations.

## Training data

Historical official and market BDT rates, corridor-specific spreads, remittance-flow
seasonality (Eid, harvest, payday cycles), oil-price and Gulf-employment indicators,
policy-announcement dates. Walk-forward backtest only, with a strict no-look-ahead
constraint on every feature.

Note the honest caveat for Bangladesh specifically: a managed rate with a persistent gap
between official and kerb markets means "the rate" is not one number. The model forecasts
the *official* rate and states that limitation on screen.

## Evaluation

| Metric | Target |
|---|---|
| Directional accuracy (24h) | ≥ 58 % |
| Interval calibration (80 % band coverage) | 80 % ± 5 pp |
| Realised user benefit when advice is followed | > 0, measured, not assumed |

The last row is the only one that matters commercially, and it is measured against the
counterfactual of sending immediately.

## Known limitations

1. **FX is close to a random walk at short horizons.** A directional accuracy target of
   58 % is deliberately modest; any backtest claiming much more is almost certainly
   leaking future information.
2. **Policy breaks are unforecastable.** A devaluation announcement invalidates the model
   instantly. Detection of a regime break suspends advice rather than continuing to
   publish it.
3. Managed-rate dynamics mean the official rate can be stable while the effective rate
   available to senders is not.
4. Thin corridors have wide intervals.

## Ethical considerations

Overconfident FX advice can cost a family real money on a real deadline. Therefore:

- Guidance is phrased with **explicit uncertainty**, in Bangla, never as a prediction
- The "send now" option is always at least as prominent as "wait"
- If urgency signals are present in the flow (an emergency category, a first-time
  high-value transfer), **timing advice is suppressed entirely**
- Realised outcome versus advice is shown in transfer history — the product is
  accountable for advice it gave

## Maintenance

Retrain weekly; suspend on detected regime break; reinstate only after re-evaluation.
