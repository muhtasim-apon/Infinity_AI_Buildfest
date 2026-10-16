# Sequence diagrams

## 1. Scan → diagnosis → advice (warm server)
```mermaid
sequenceDiagram
  autonumber
  actor Farmer
  participant Web as Web (PWA)
  participant API as API (FastAPI)
  participant ST as Supabase Storage (private)
  participant DB as Postgres+pgvector
  participant LLM as LLM
  Farmer->>Web: take photo
  Web->>Web: resize, strip EXIF, sha256, round location
  Web->>API: POST /v1/scans (JWT, Idempotency-Key)
  API->>DB: insert scan(pending_upload)
  API-->>Web: {scan_id, signed upload_url (5 min)}
  Web->>ST: PUT image
  Web->>API: POST /v1/scans/{id}/analyze
  API->>ST: get image (secret key)
  API->>API: sanitise + ONNX infer + calibrate
  alt confidence >= τ
    API->>DB: hybrid search kb_chunks
    API->>LLM: advice from sources only (no personal data)
    LLM-->>API: JSON advice + citations
    API->>API: validator V1–V6
    API->>DB: diagnosis + advisory + citations + audit (one transaction)
    API-->>Web: diagnosis + cited Bangla advice
  else below τ or out-of-distribution
    API->>DB: diagnosis(not_sure) + audit
    API-->>Web: "not sure" + retake tips + local office card
  end
```

## 2. Cold start (Render free, after 15 min idle)
```mermaid
sequenceDiagram
  participant Web
  participant Render as Render edge
  participant API
  Web->>Render: GET /healthz (on app open)
  Render-->>Web: slow (~1 min while the instance boots)
  Web->>Web: show "সার্ভার চালু হচ্ছে…" — photo kept in outbox
  Render->>API: boot container, download model from private bucket, verify hash
  API-->>Web: 200 healthz
  Web->>API: flush outbox (analyze)
```

## 3. Automatic outbreak alert
```mermaid
sequenceDiagram
  participant API
  participant DB
  participant OM as Open-Meteo
  participant N8N as n8n
  actor Farmers
  actor Admin
  API->>DB: count same-disease diagnoses within radius/window (not-sure excluded)
  API->>DB: any alert for this disease/area inside cooldown?
  API->>OM: humidity / rain / temperature forecast (3 s timeout)
  API->>DB: insert alert(published, risk, rules-v1, "unverified" label) + audit
  API->>N8N: signed webhook "alert published" (no personal data)
  N8N->>N8N: post notice to team Telegram channel
  Farmers->>API: GET /v1/alerts (in-app)
  opt alert looks wrong or abusive
    Admin->>API: POST /v1/alerts/{id}/dismiss (reason) — audited
  end
```

## 4. One-click demo (with CAPTCHA)
```mermaid
sequenceDiagram
  actor Judge
  participant Web
  participant TS as Cloudflare Turnstile
  participant API
  Judge->>Web: /demo-user (or /demo-admin)
  Web->>TS: widget challenge
  TS-->>Web: token
  Web->>API: POST /v1/demo/session {role} + CF-Turnstile-Response
  API->>TS: verify token (server-side)
  API-->>Web: 30-min token for a synthetic demo account (rate-limited)
  Web-->>Judge: /app with SYNTHETIC banner
```

## 5. Admin action (audited)
```mermaid
sequenceDiagram
  actor Admin
  participant Web
  participant API
  participant DB
  Admin->>Web: change τ + reason
  Web->>API: PUT /v1/admin/settings (JWT)
  API->>DB: read profiles.role (server-side check, never the UI)
  API->>DB: update app_settings + audit_append(admin.settings.update, reason)
  API-->>Web: 200 (new values)
```
