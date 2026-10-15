 Ready to code?

 Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Plan — Convert repo to "Crop Guardian" (AgriSphere AI) web-app template

 Context

 The repo currently holds remitos/, a docs-and-stubs template for a FinSphere / Borderless Money
 entry. The team (Apon, Taeen, Salwa, Raisa, Sara) is now entering Idea to Unicorn → AgriSphere AI →
 Crop Guardian ("early pest and disease detection from imagery"; capabilities: vision models +
 alerts + local-language UX; winning signal: loss reduction at field level). Preliminary deadline:
 31 Oct 2026, 12:00 BST (3-min video pitch + package, guide §9.2). Today is 16 Oct.

 Decisions confirmed with the user:
 - Challenge = Crop Guardian. Precision Farm documented only as a future domain pack.
 - Replace remitos/ with cropguardian/ (same professional structure, web-only — no Flutter/mobile).
 - Prototype = clickable static HTML UI + typed stubs. Nothing installed, deployed, or pushed.
   Changes stay local (no git push; commit only if the user asks).

 Guide rules that shape everything: no fabricated demos/results (§20.4) → all sample data labelled
 SYNTHETIC; Bangla-first (§9.2, §13.4 #6); every role owned by a named member (§13.2); judging = 5 × 20
 pts (§11.1); responsible AI + data sovereignty (§15); expose the §10.8 routes (/app, /demo-user,
 /demo-admin, /admin, /data, /security, /architecture, /presentation, /pitchdeck, /audit) — not
 mandatory for I2U but they map directly onto the rubric, so we adopt them.

 Recommended system (what the docs will specify)

 Layer: Frontend (Sara)
 Choice: React + Vite + TypeScript SPA, i18n bn default / en, PWA offline capture queue, image
 compression client-side
 Why: Render static site is free and does not spin down
 ────────────────────────────────────────
 Layer: Backend (Apon, Taeen)
 Choice: FastAPI (Python 3.12) in Docker on Render free web service
 Why: onnxruntime fits the small free instance
 ────────────────────────────────────────
 Layer: DB / storage / auth
 Choice: Supabase Postgres + pgvector + Storage + Auth (JWT, RLS)
 Why: Render free Postgres expires after 30 days (verified render.com/docs/free) — would die before 15
 Nov selection and 26 Dec finals
 ────────────────────────────────────────
 Layer: Vision ML (Apon, Taeen)
 Choice: Transfer learning, compare MobileNetV3-L, EfficientNetV2-B0, ConvNeXt-Tiny, DeiT-Small (ViT);
 winner exported ONNX int8; temperature-scaled confidence + abstain/"unsure → expert review" gate;
 Grad-CAM heatmap
 Why: small, explainable, CPU inference
 ────────────────────────────────────────
 Layer: Stretch vision
 Choice: YOLOv8n lesion detection → severity %; out-of-distribution "not a leaf" check
 Why:
 ────────────────────────────────────────
 Layer: Outbreak risk
 Choice: Open-Meteo weather + report clusters → rule baseline, then LightGBM; geo-cluster (DBSCAN)
 alerts
 Why: honest about small data
 ────────────────────────────────────────
 Layer: AI advisory (Salwa, Raisa)
 Choice: LLM agent (Claude claude-sonnet-5-5, provider-swappable) + RAG with citation enforcement over
 Bangla DAE/BRRI/BARI treatment guides in pgvector; Bangla voice in/out as stretch
 Why:
 ────────────────────────────────────────
 Layer: Automation
 Choice: n8n: outbreak alert fan-out, daily digest, drift monitor, keep-warm ping, synthetic uptime
 tests
 Why:

 Core flow: farmer photo → upload (signed URL) → validate → ONNX inference → calibrate/abstain →
 Grad-CAM → RAG advisory (cited, Bangla) → save diagnosis → geo-cluster → n8n alert → expert/admin
 review → feedback label → retraining set (data flywheel).

 Repo layout to create (cropguardian/)

 Mirror the remitos conventions (README per folder, ADRs, model cards, CLAUDE.md rules). Representative
 paths:
 - Root: README.md (rewritten for Crop Guardian),
   cropguardian/{README,CLAUDE,CONTRIBUTING,SECURITY,CODE_OF_CONDUCT}.md, LICENSE, .env.example,
   .gitignore, render.yaml, .github/{CODEOWNERS,workflows/quality-gates.yml,PULL_REQUEST_TEMPLATE.md,ISS
   UE_TEMPLATE/,dependabot.yml}
 - prototype/ — clickable static UI: index.html landing + one page per §10.8 route, app.html (scan →
   result → advisory → history → outbreak map), shared
   assets/{style.css,app.js,i18n.js,synthetic-data.js}; bn/en toggle, phone-width first, persistent
   "SYNTHETIC DEMO DATA" banner. Plain HTML/CSS/JS, no build, opens via file://.
 - apps/web/ — React/Vite stubs: package.json, src/{routes,features/{scan,diagnosis,advisory,history,ale
   rts,admin,audit},i18n/{bn,en}.json,lib/api.ts} (typed stubs only)
 - services/api/ — FastAPI stubs: app/{main.py,config.py,routers/{auth,scans,diagnoses,advisory,alerts,a
   dmin,audit,health}.py,schemas/,ml/inference.py,rag/,security/}, Dockerfile, requirements.txt
 - db/ — schema.sql (full DDL), migrations/0001_init.sql, rls_policies.sql, seed_synthetic.sql
 - ml/ — vision/{configs,train.md,export_onnx.md}, outbreak/, rag/, evaluation/, registry/README.md
 - automation/n8n/workflows/*.md (6–8 workflow specs)
 - tests/ — unit/ whitebox/ blackbox/ integration/ timeout/ concurrency/ security/ ml/ e2e/ manual/ n8n/
   each with README + stub test files and case tables
 - docs/ — see next section
 - scripts/build_report.py, scripts/chrome_pdf.py (reuse existing, retarget paths/titles)

 Then git rm -r remitos/ (confirmed by user).

 Documentation set (cropguardian/docs/)

 1. system-design/SDD.md — master System Design Document (problem, users, KPIs, requirements, NFRs,
    capacity estimates, architecture, every section below cross-linked).
 2. architecture/ — system-overview.md, data-flow.md, sequence-diagrams.md, deployment.md, ADRs
    0001–0010 (React SPA; FastAPI monolith-modular; Supabase over Render PG; ONNX on CPU; abstain +
    HITL; RAG citation enforcement; Bangla-first; n8n automation plane; offline-first PWA;
    data-sovereignty boundary). Mermaid .mmd in docs/diagrams/.
 3. data/ — erd.md + diagrams/erd.mmd; tables: users, farmer_profiles, farms, fields(geo), crops, scans,
    images, diagnoses, disease_catalog, treatments, advisories, citations, alerts, alert_subscriptions,
    expert_reviews, feedback_labels, model_versions, kb_documents, kb_chunks(vector), audit_log,
    consents. datasets.md (links + licences + split strategy), data-governance.md, data-sovereignty.md.
 4. ai/ — vision-model.md (algorithm comparison & selection logic), statistics.md (class balance,
    stratified k-fold, macro-F1, per-class recall, confusion matrix, ECE/calibration, bootstrap 95% CI,
    McNemar test between models, lab→field domain-shift test), rag-design.md, agent-design.md,
    eval-plan.md, model-cards/ (disease-classifier, lesion-detector, outbreak-risk, advisory-llm),
    responsible-ai.md (bias by crop/region/phone quality).
 5. security/ — threat-model.md (STRIDE), owasp-mapping.md (OWASP Top 10 + LLM Top 10: prompt injection,
    insecure upload, IDOR, rate limiting), audit-readiness.md, privacy.md (EXIF/GPS stripping, coarse
    geo, consent).
 6. deployment/ — render-guide.md and challenges-and-recovery.md: cold start ~1 min after 15 min idle →
    keep-warm ping + frontend "waking server" state + 60 s client timeout/retry; 750 instance-hrs/month
    (only one 24/7 service); ephemeral disk → model weights baked into image or pulled from Supabase
    Storage at boot, never local uploads; single instance → async job queue + idempotency keys; Render
    may restart → health checks, stateless API; free PG expiry → Supabase; memory → ONNX int8, lazy
    load, 1 worker; build minutes/bandwidth; Supabase free pauses after inactivity → n8n heartbeat; LLM
    rate limits/outage → cached advisories + rule-based fallback; CORS/secrets/env groups; rollback via
    Render deploy history. Plus team/process risks (dataset gaps, Bangla KB scarcity, low-light photos,
    demo-day internet → recorded backup video).
 7. testing/ — test-strategy.md with links (pytest, pytest-cov, Hypothesis, Schemathesis, Playwright,
    k6, Locust, OWASP ZAP, Bandit, pip-audit, npm audit, Postman/Newman, n8n): unit, whitebox (branch
    coverage targets), blackbox (equivalence/boundary on file type/size/resolution), integration,
    timeout (cold start, LLM 20 s budget, inference budget), concurrency (k6 50 VUs, duplicate upload
    race, idempotency), security, ML robustness (blur/brightness/rotation invariance), manual test-case
    sheets, n8n synthetic monitors.
 8. plan/ — gantt.md (day-by-day table + Mermaid gantt), raci.md, daily-standup-template.md.
 9. congress/ — rubric-map.md (each 20-pt component → evidence), submission-checklist.md,
    video-pitch-script.md (180 s per §9.2 segments), demo-script.md.
 10. product/ — prd.md, personas.md (smallholder rice farmer, SAAO extension officer, admin/agronomist),
     user-journeys.md.
 11. research/ — sources with URL + access date; any number not here is not used. Confirmed so far:
     RiceLeafBD (Mendeley kx9rx8p2mz, 1,555 field images, 4 classes), RiceLeafDisease-BD5 (Mendeley
     sjkptpgv79, 2,545 images, 5 classes), arXiv 2501.08912; PlantVillage & PlantDoc repos to be
     verified at write time.
 12. report/ — HTML parts → CropGuardian-System-Design-Report.pdf via build_report.py.

 Roles (declared in CONTRIBUTING + CODEOWNERS, §13.2)

 - Apon — Team Leader; backend, database, ML integration, deployment (Render/Supabase).
 - Taeen — Data Scientist / ML training; backend support; dataset & statistics.
 - Salwa — AI integration: RAG, knowledge base, LLM evaluation.
 - Raisa — AI integration: advisory agent, Bangla prompts/voice; Presentation lead (proposed — confirm).
 - Sara — Frontend / UI-UX lead (Bangla, mobile, low-bandwidth).
 - NRB advisor slot: TBD (marked open).

 Gantt 16–29 Oct (summary — full daily per-person table goes in docs/plan/gantt.md)

 Days: 16–17
 Apon: Repo, render.yaml, Supabase project, schema v1
 Taeen: Download/audit datasets, EDA, splits
 Salwa: Collect Bangla treatment docs
 Raisa: Persona interviews plan, prompt specs
 Sara: Wireframes, design tokens, bn/en
 ────────────────────────────────────────
 Days: 18–19
 Apon: FastAPI skeleton, auth, upload signed URLs
 Taeen: Baselines (MobileNetV3, EffNetV2) on Colab
 Salwa: Chunking + pgvector ingest
 Raisa: Advisory agent prompts + citation rule
 Sara: Scan + result screens
 ────────────────────────────────────────
 Days: 20–21
 Apon: Inference endpoint (ONNX), deploy v0 to Render
 Taeen: ConvNeXt/DeiT runs, calibration, Grad-CAM
 Salwa: Retrieval eval set
 Raisa: Bangla voice/UX copy, safety rules
 Sara: History, alerts, map screens
 ────────────────────────────────────────
 Days: 22–23
 Apon: Alerts + geo-cluster, n8n workflows
 Taeen: Stats report (CI, McNemar, domain shift), export ONNX int8
 Salwa: RAG ↔ API integration
 Raisa: Agent ↔ API integration
 Sara: Admin, data, security, audit pages
 ────────────────────────────────────────
 Days: 24–25
 Apon: Security hardening, rate limit, RLS
 Taeen: Robustness tests, model card
 Salwa: LLM eval + red-team (prompt injection)
 Raisa: Field-validation sessions
 Sara: E2E wiring, PWA offline
 ────────────────────────────────────────
 Days: 26–27
 Apon: Load/timeout/concurrency tests, cold-start fixes
 Taeen: Retrain with feedback set
 Salwa: Fallbacks, caching
 Raisa: Pitch script, slide deck
 Sara: Playwright tests, polish, accessibility
 ────────────────────────────────────────
 Days: 28–29
 Apon: Freeze, deploy final, runbook
 Taeen: Final metrics in docs
 Salwa: Docs
 Raisa: Record 3-min video
 Sara: Demo recording support
 ────────────────────────────────────────
 Days: 30–31 Oct = buffer + submit before 12:00 BST 31 Oct.
 Apon:
 Taeen:
 Salwa:
 Raisa:
 Sara:

 Implementation steps (after approval)

 1. Read remitos/scripts/build_report.py, chrome_pdf.py, quality-gates.yml, ADR + model-card format to
    reuse their conventions.
 2. Verify remaining dataset/tool links via WebFetch; record in docs/research/ with access dates.
 3. Create cropguardian/ tree (docs first, then db/services/ml/tests stubs, then prototype/).
 4. Build the clickable prototype pages.
 5. Write report HTML parts; run build_report.py to produce the PDF.
 6. git rm -r remitos/; rewrite root README.md.

 Verification

 - Open prototype/index.html in Chrome; click through every route, bn↔en toggle, 375 px width, synthetic
   banner present on every page.
 - grep -ri "remitos\|remittance\|FinSphere" in cropguardian/ returns nothing.
 - All Mermaid files render (check in a Mermaid previewer); internal Markdown links resolve (scripted
   link check).
 - Report PDF builds and opens; every statistic in docs traces to docs/research/.
 - git status shows only local changes; nothing pushed or deployed.
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌