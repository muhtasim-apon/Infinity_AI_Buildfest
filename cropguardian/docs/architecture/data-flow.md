# Data flow

Diagram: [`../diagrams/data-flow.mmd`](../diagrams/data-flow.mmd). Sequences:
[`sequence-diagrams.md`](sequence-diagrams.md).

## 1. Operational flow — one scan

| # | Step | Where | Data | Failure handling |
|---|---|---|---|---|
| 1 | Photo taken / chosen | browser | raw image | camera denied → file picker |
| 2 | Resize ≤ 1024 px, JPEG q≈0.8, strip EXIF, SHA-256 | browser | ~150–300 KB JPEG | too dark/blurry heuristic → "retake" hint |
| 3 | Offline? → store in IndexedDB outbox | browser | blob + metadata | retried by background sync |
| 4 | `POST /v1/scans` {crop, field_id, sha256, coarse lat/lon} | API | scan row `pending_upload` | duplicate sha256 for same user → return existing scan (idempotent) |
| 5 | PUT image to signed URL | Supabase Storage `scans/{user}/{scan}.jpg` | image | URL expires 5 min → request new |
| 6 | `POST /v1/scans/{id}/analyze` | API | — | 409 if not uploaded |
| 7 | Download, magic-byte check, decode, re-encode | API memory | tensor 224×224 | invalid → 422 problem+json |
| 8 | ONNX inference → temperature softmax → top-3 | API | probs | timeout 4 s → 503 + retry-after |
| 9 | Threshold decision | API | `diagnosed` / `needs_review` | — |
| 10 | Retrieve KB chunks (disease, crop, stage, lang=bn) | pgvector | top-k chunks | score < min → no advice, escalate |
| 11 | LLM generates structured advice from chunks | LLM | JSON advice | timeout 20 s / invalid / uncited → fallback text + escalate |
| 12 | Persist diagnosis, advisory, citations, audit event | Postgres | rows | transaction; on failure nothing partial is shown |
| 13 | Outbreak check | API | cluster count | threshold crossed → `alerts` draft |
| 14 | Agronomist approves alert | API → n8n | alert payload (no PII) | n8n retry ×3, dead-letter |
| 15 | Notify subscribers | n8n → SMS/email/Telegram | Bangla message | per-channel fallback |

## 2. Learning flow — data flywheel
```
needs_review scan ─▶ agronomist label ─▶ feedback_labels ─▶ weekly export (n8n)
     ─▶ dedup + consent check ─▶ ml/vision training set vN+1 ─▶ train ─▶ evaluate
     ─▶ model card update ─▶ admin promotes in model_versions ─▶ API loads at next boot
```
Only images whose owner consented to `training_use` are exported (`consents` table).

## 3. Knowledge flow — RAG ingestion
```
DAE/BRRI/BARI PDF or web page ─▶ licence/permission recorded in kb_documents
 ─▶ text extraction (Bangla-aware) ─▶ chunk 300–500 tokens, overlap 50
 ─▶ metadata {crop, disease, stage, doc_id, page, edition_date}
 ─▶ embed (multilingual-e5) ─▶ kb_chunks (vector) ─▶ retrieval eval set re-run
```

## 4. Data classification
| Class | Examples | Storage | Leaves Bangladesh-controlled systems? |
|---|---|---|---|
| Personal | phone, name, exact GPS | Postgres (restricted columns) | **No** |
| Quasi-personal | coarse location (~1 km), field size | Postgres | Only aggregated |
| Imagery | leaf photos | Storage (private) | No (model runs in our API) |
| Derived | diagnosis, confidence | Postgres | Disease name only, to LLM |
| Public | KB guides | Postgres | Yes (sent to LLM as context) |

See [`../data/data-sovereignty.md`](../data/data-sovereignty.md) for hosting-region decisions.
