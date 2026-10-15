# Sequence diagrams

## 1. Scan → diagnosis → advice (happy path, warm server)
```mermaid
sequenceDiagram
  autonumber
  actor Farmer
  participant Web as Web (PWA)
  participant API as API (FastAPI)
  participant ST as Supabase Storage
  participant DB as Postgres+pgvector
  participant LLM as LLM
  Farmer->>Web: take photo
  Web->>Web: resize, strip EXIF, sha256
  Web->>API: POST /v1/scans (JWT, Idempotency-Key)
  API->>DB: insert scan(pending_upload)
  API-->>Web: {scan_id, signed upload_url}
  Web->>ST: PUT image
  Web->>API: POST /v1/scans/{id}/analyze
  API->>ST: get image
  API->>API: validate + ONNX infer + calibrate
  alt confidence >= threshold
    API->>DB: vector search kb_chunks
    API->>LLM: advice from chunks only (no PII)
    LLM-->>API: JSON advice + citations
    API->>API: validate citations, banned list
    API->>DB: insert diagnosis, advisory, citations, audit
    API-->>Web: diagnosis + advice (bn)
  else below threshold
    API->>DB: insert diagnosis(needs_review), audit
    API-->>Web: "not sure — sent to agronomist"
  end
```

## 2. Cold start (Render free, after 15 min idle)
```mermaid
sequenceDiagram
  participant Web
  participant Render as Render edge
  participant API
  Web->>Render: GET /healthz (on app open, pre-emptive)
  Render-->>Web: loading page / slow response (~1 min)
  Web->>Web: show "সার্ভার চালু হচ্ছে… / Waking the server" + keep photo in outbox
  Render->>API: boot container, load ONNX session
  API-->>Web: 200 healthz
  Web->>API: flush outbox (analyze)
```

## 3. Human review loop
```mermaid
sequenceDiagram
  actor Agro as Agronomist
  participant Web
  participant API
  participant DB
  Agro->>Web: open /app/review
  Web->>API: GET /v1/review/queue
  API->>DB: scans where status=needs_review (RLS: agronomist region)
  API-->>Web: queue
  Agro->>Web: confirm / correct label
  Web->>API: POST /v1/review/{scan_id}
  API->>DB: expert_reviews + feedback_labels + audit_log
  API-->>Web: farmer notified (in-app)
```

## 4. Outbreak alert
```mermaid
sequenceDiagram
  participant API
  participant DB
  participant OM as Open-Meteo
  actor Agro as Agronomist
  participant N8N as n8n
  actor Farmers
  API->>DB: count same-disease diagnoses within radius/window
  API->>OM: humidity/temperature forecast
  API->>DB: insert alert(draft, risk_level)
  Agro->>API: POST /v1/alerts/{id}/approve
  API->>N8N: webhook (HMAC, no PII)
  N8N->>DB: subscribers in radius (via API)
  N8N->>Farmers: Bangla SMS / Telegram / email
```

## 5. One-click demo
```mermaid
sequenceDiagram
  actor Judge
  participant Web
  participant API
  Judge->>Web: /demo-user  (or /demo-admin)
  Web->>API: POST /v1/demo/session {role}
  API->>API: issue short-lived JWT for seeded synthetic account (read-mostly, rate-limited)
  API-->>Web: token
  Web-->>Judge: lands on /app with SYNTHETIC banner
```
