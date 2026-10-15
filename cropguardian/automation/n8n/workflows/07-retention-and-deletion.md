# 07 — Retention & deletion

**Trigger:** Cron nightly 02:00.
**Steps:** `POST /v1/hooks/n8n/retention` → API (1) downsizes originals older than 90 days to thumbnails unless labelled with training consent, (2) hard-deletes accounts flagged for deletion > 0 days ago (within the 7-day promise), Storage objects first, then rows, (3) writes audit rows with hashed user ids.
**Report:** counts only, to team Telegram.
