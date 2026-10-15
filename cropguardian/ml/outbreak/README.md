# ml/outbreak — outbreak risk

Card: [`../../docs/ai/model-cards/outbreak-risk.md`](../../docs/ai/model-cards/outbreak-risk.md).

## Rules v1 parameters (config, editable from /admin, audited)
| Parameter | Default | Source of default |
|---|---|---|
| `OUTBREAK_RADIUS_KM` | 5 | design choice — revisit with extension officers |
| `OUTBREAK_MIN_REPORTS` | 3 | design choice |
| `OUTBREAK_WINDOW_DAYS` | 7 | design choice |
| favourable-weather bands per disease | — | **must come from cited KB sources** before enabling |

## v2 plan (LightGBM)
Features: cluster size, growth rate over 3/7 days, weather lags (humidity, rain, temperature), variety
susceptibility (from KB), crop stage from sowing date. Target: agronomist-confirmed outbreak within 14 days.
Validation: time-based split (train on earlier weeks, test on later). Needs ≥ one season of labels.
