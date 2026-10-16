# 06 — Model drift monitor

**Trigger:** Cron weekly (Sunday 09:00).
**Steps:** API `GET /v1/admin/drift` → this week vs. previous 4 weeks: not-sure rate, predicted-class distribution (PSI), mean top-1 prob.
**Alert thresholds (initial, tune later):** PSI > 0.2, abstain rate change > 10 points, alert dismiss rate > 30 % → notify Taeen + Apon; suggests raising τ from `/admin` while investigating.
