# 08 — Demo reset

**Trigger:** Cron nightly 01:00 + manual button before judging.
**Steps:** `POST /v1/hooks/n8n/reset_demo` → API deletes rows owned by demo accounts and re-seeds the **synthetic** history (fixtures), so judges always see a clean, labelled demo.
