# 06 — Model drift monitor

**Trigger:** Cron weekly (Sunday 09:00).
**Steps:** API `GET /v1/admin/drift` → this week vs. previous 4 weeks: abstain rate, predicted-class distribution (PSI), mean top-1 prob, agronomist disagreement rate on reviewed cases.
**Alert thresholds (initial, tune later):** PSI > 0.2, abstain rate change > 10 points, disagreement > 20 % → notify Taeen + Apon; suggests raising τ from `/admin` while investigating.
