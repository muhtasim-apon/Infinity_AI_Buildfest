# 02 — Daily digest

**Trigger:** Cron 08:00 Asia/Dhaka.
**Steps:** API `GET /v1/admin/digest` (HMAC) → `{scans_24h, abstain_rate, review_queue_size, oldest_review_age_h, drafts_pending, blocked_advisories, errors_24h, p95_latency}` → format Bangla + English → team Telegram group; agronomists get their upazila's queue size only.
**Rule:** numbers are counts from the system, never presented as accuracy claims.
