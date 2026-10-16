# 02 — Daily digest

**Trigger:** Cron 08:00 Asia/Dhaka.
**Steps:** signed `GET /v1/admin/digest` → `{scans_24h, not_sure_rate, alerts_published_24h,
alerts_dismissed_24h, blocked_advisories, errors_24h, p95_latency, cold_starts}` → format in Bangla +
English → team Telegram channel.
**Rule:** these are operational counts, never presented as accuracy claims.
