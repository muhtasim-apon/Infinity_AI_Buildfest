# 04 — Supabase heartbeat (challenge B1)

**Trigger:** Cron daily 03:00 Asia/Dhaka.
**Steps:** `POST /v1/hooks/n8n/heartbeat` (HMAC) → API runs `select 1` and a tiny write to a heartbeat row → 200.
**Why:** free Supabase projects pause after 1 week of inactivity [R2]. On failure → team Telegram with the restore checklist link (`docs/deployment/04-free-tier-challenges.md` B1).
