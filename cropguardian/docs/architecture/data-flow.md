# Data flow

Diagram: [`../diagrams/data-flow.mmd`](../diagrams/data-flow.mmd). Sequences:
[`sequence-diagrams.md`](sequence-diagrams.md).

## 1. Operational flow — one scan

| # | Step | Where | Data | Failure handling |
|---|---|---|---|---|
| 1 | Photo taken / chosen | browser | raw image | camera denied → file picker |
| 2 | Resize ≤ 1024 px, JPEG q≈0.8, strip EXIF, SHA-256, round location to 2 decimals | browser | ~150–300 KB JPEG | too dark/blurry → "retake" hint |
| 3 | Offline? → store in IndexedDB outbox | browser | blob + metadata | retried when online and `/healthz` = 200 |
| 4 | `POST /v1/scans` {crop, field_id, sha256, coarse lat/lon} | API | scan row `pending_upload` | same sha256 for same user → existing scan returned (idempotent) |
| 5 | PUT image to signed URL | private Storage `scans/{user}/{scan}.jpg` | image | URL expires after 5 min → request a new one |
| 6 | `POST /v1/scans/{id}/analyze` | API | — | 409 if not uploaded |
| 7 | Download, magic-byte check, decode, re-encode | API memory | tensor 224×224 | invalid → 422 problem+json |
| 8 | ONNX inference → temperature softmax → top-3 | API | probabilities | timeout 4 s → 503 + Retry-After |
| 9 | Threshold decision | API | `diagnosed` / `not_sure` | not sure → retake tips + local office card, no advice |
| 10 | Retrieve KB chunks (disease, crop, stage, Bangla) | pgvector | top-k chunks | score < minimum → static fallback card |
| 11 | LLM writes structured advice from chunks | LLM | JSON advice | timeout 20 s / invalid / uncited → fallback |
| 12 | Persist diagnosis, advisory, citations, audit event | Postgres | rows | one transaction; nothing partial is shown |
| 13 | Outbreak check | API | cluster count | threshold met, no alert in cooldown → **publish** labelled alert |
| 14 | Alert notice | API → n8n → team Telegram | alert summary (no personal data) | n8n retry ×3; in-app alert is the source of truth |
| 15 | Admin dismisses a wrong alert (optional) | API | status dismissed + reason | audited |

## 2. Model update flow
```
public datasets (D1, D2; D3 for out-of-distribution) ─▶ train on free GPU (Colab/Kaggle)
 ─▶ evaluation report ─▶ model card update ─▶ int8 ONNX to private `models` bucket
 ─▶ model_versions row ─▶ admin activates (audited) ─▶ API downloads at next boot (sha256 checked)
```
User photos are **not** used for training in this version.

## 3. Knowledge flow — RAG ingestion
```
DAE/BRRI/BARI PDF or web page ─▶ licence/permission recorded in kb_documents
 ─▶ text extraction (Bangla-aware) ─▶ chunk 300–500 tokens, overlap 50
 ─▶ metadata {crop, disease, stage, doc_id, page, edition_date}
 ─▶ embed (multilingual-e5) ─▶ kb_chunks (vector) ─▶ retrieval evaluation re-run
```

## 4. Data classification
| Class | Examples | Storage | Leaves our controlled systems? |
|---|---|---|---|
| Personal | email, display name | Supabase Auth / Postgres | **No** |
| Quasi-personal | coarse location (~1 km), field size | Postgres | only aggregated (alerts) |
| Imagery | leaf photos | Storage (private) | No (model runs in our API) |
| Derived | diagnosis, confidence | Postgres | disease name only, to the LLM |
| Public | KB guides | Postgres | yes (sent to the LLM as context) |

Hosting regions: [`../data/data-sovereignty.md`](../data/data-sovereignty.md).
