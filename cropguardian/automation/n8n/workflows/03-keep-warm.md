# 03 — Keep-warm (Render cold start, challenge A1)

**Trigger:** Cron every 10 min, **only inside configured windows** (judging slots, demos, pilot hours).
**Steps:** `GET https://cropgurdian-backend.onrender.com/healthz` (timeout 90 s) → record first-byte time → if > 20 s, log "cold start" event.
**Budget note:** keeping one service warm 24/7 ≈ 744 h/month, inside 750 free instance-hours [R1]; keep-warm on a *second* service would exceed it — never add one.
**Off switch:** a single n8n variable `KEEP_WARM_ENABLED`.
