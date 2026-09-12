# Model Card — Corridor Cost & ETA Predictor

**Status:** Specification (not trained) · **Risk tier:** Medium
**Pack:** borderless_money · **Code:** `ml/models/corridor_cost_predictor/`

---

## Intended use

Predict, for a given send request, the **landed amount in BDT** and the **arrival time**
for each candidate payout path. These two predictions are the inputs the routing engine
optimises over, and they are what the user actually sees on the quote screen.

This is the commercial core of the product. The World Bank records a 2.71-percentage-point
gap between digital (4.59 %) and non-digital (7.30 %) remittance cost globally in
Q3 2025 [see `docs/research/data/01-global-remittance-baseline.md`]. Capturing a share of
that gap requires knowing, per request, which path is actually cheapest — a question no
incumbent currently answers for the user.

## Out-of-scope use

- Not a binding price. The quote shown to the user is produced by `fx-service` and the
  partner's committed fee; this model *ranks* candidates and estimates.
- Not valid for a corridor or partner with no evaluation history — unseen combinations
  fall back to a published-rate baseline, and the UI says the estimate is provisional.
- Never used to justify a fee to a user without the actual committed figures.

## Training data

| | |
|---|---|
| Sources | Own settled-transfer history (cost, timing, outcome per leg) · partner fee schedules with effective dates · published corridor benchmarks (n8n 04) · partner uptime and latency telemetry |
| Split | **Temporal**, by settlement date |
| Granularity | One row per attempted leg, including failures |
| Known gap | Pre-launch there is no own history. Cold start runs on published schedules only, clearly labelled as estimates. |

Failed legs are retained in training. A model trained only on successes systematically
underestimates both cost and time, because retries are exactly where both accumulate.

## Features

Corridor · partner · payout endpoint type (wallet / bank / agent cash) · amount band ·
day-of-week and hour · proximity to payday and to Eid · partner recent uptime and p95
latency · queue depth · FX volatility regime · public holiday calendars **on both sides**
of the corridor · promotional-fee flag.

Holiday calendars on both sides matter more than they appear: a transfer initiated on a
Friday from Riyadh into a Bangladeshi bank holiday can sit for three days on a path that
the naive model scores as "fast".

## Evaluation

| Metric | Target |
|---|---|
| Landed-cost MAPE | ≤ 8 % |
| ETA p90 absolute error | ≤ 30 min |
| Ranking quality (NDCG@3 vs realised best path) | ≥ 0.90 |
| Calibration of the ETA interval | 90 % coverage ± 3 pp |

Fairness is evaluated on **amount band and payout type**: the model must not be
systematically less accurate for small transfers or for agent cash-out — the paths used
by the poorest recipients. Accuracy that degrades as the amount falls is a regressive
failure mode, and aggregate MAPE hides it completely.

| Fairness gate | Threshold |
|---|---|
| MAPE ratio, smallest amount decile vs largest | ≤ 1.3 |
| MAPE ratio, agent cash-out vs bank payout | ≤ 1.3 |

## Known limitations

1. **Cold start.** No own history at launch; published rates only, labelled provisional.
2. **Partner opacity.** Some partners do not disclose the full fee stack; the model learns
   effective cost from outcomes, which takes volume.
3. **Regime shifts.** A fee-schedule change or a new corridor invalidates learned
   patterns immediately. Effective-dated fee data limits the damage; drift monitoring
   catches the rest.
4. **Rare corridors** have thin data and wide intervals. The UI must show the interval,
   not a false point estimate.
5. **Predicts, does not commit.** Actual cost is set at execution.

## Ethical considerations

The user-facing risk is a quote that reads better than reality. Two guards:

- The interval is displayed, not hidden behind a single number, whenever it is wide
- Realised-versus-predicted is monitored publicly in the app's transfer history, so the
  product is accountable for its own estimates rather than quietly forgetting them

Optimising this model to make the product's own rail look cheapest would be a direct
conflict of interest. The objective is realised landed amount for the user, and partner
identity is not a feature the model is permitted to optimise *toward*.

## Maintenance

Retrain monthly or on drift; immediate refresh on any partner fee-schedule change.
Promotion follows `docs/ai/eval-plan.md`.
