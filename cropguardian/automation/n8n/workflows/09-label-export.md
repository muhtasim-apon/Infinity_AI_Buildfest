# 09 — Label export (data flywheel)

**Trigger:** Cron weekly (Saturday 22:00).
**Steps:** `POST /v1/hooks/n8n/export_labels` → API selects `feedback_labels` where `consent_training = true and exported = false`, verifies consent is still granted, writes a manifest (image path, label, review id) to Storage `exports/<date>.csv`, marks `exported = true`.
**Then:** Taeen pulls the manifest into the next training split (dedup against existing data first).
