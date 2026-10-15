# Model card — Outbreak risk (rules v1 → ML v2)

**Status:** Rules v1 specified; ML v2 later · **Risk tier:** High (public alerts)
**Code:** `services/api/app/services/outbreak.py`, `ml/outbreak/`

## Intended use
Raise a **draft** alert when diagnoses of a notifiable disease cluster in space and time, with
weather that favours spread. An agronomist approves before anything is sent.

## Rules v1 (labelled "rule-based" in the UI)
```
cluster = diagnoses of disease d, not abstained, prob ≥ τ OR agronomist-confirmed,
          within OUTBREAK_RADIUS_KM (5) of a point, within OUTBREAK_WINDOW_DAYS (7)
if |cluster| ≥ OUTBREAK_MIN_REPORTS (3):
    weather_favourable = forecast humidity/rain/temperature in the disease's favourable band
                         (bands taken from cited KB sources, not invented)
    risk = high if (|cluster| ≥ 6 and weather_favourable) else medium if weather_favourable else low
    create alert(draft, risk, rule_version='rules-v1')
```
Constants live in config, are shown on `/admin`, and every change is audit-logged.

## ML v2 (when ≥ 1 season of confirmed outbreaks exists)
LightGBM on cluster size growth rate, weather lags, variety susceptibility, sowing-date stage →
probability of agronomist-confirmed outbreak within 14 days. Evaluated by precision of alerts,
lead time, false-alert rate (`statistics.md` §9).

## Limitations
Reporting bias: clusters reflect where app users are, not where disease is. Sparse users → missed
outbreaks. Alerts are never a substitute for DAE surveillance.
