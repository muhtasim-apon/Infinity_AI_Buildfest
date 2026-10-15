# Crop Guardian — ফসল রক্ষী

**Early pest and disease detection from a phone photo, with Bangla advice and outbreak alerts.**

| | |
|---|---|
| **Track** | Idea to Unicorn (team project) — International AI Builders Congress 2026 |
| **Domain** | AgriSphere AI — Agriculture, Food Security & Rural Prosperity |
| **Challenge area** | **Crop Guardian** — early pest and disease detection from imagery |
| **Capabilities to demonstrate** | Vision models · Alerts · Local-language UX (Participants Guide §6.4) |
| **Winning signal** | Loss reduction at the field level |
| **Product surface** | **Web app only** (mobile-first responsive PWA). No native app. |
| **Preliminary deadline** | **31 October 2026, 12:00 BST** (3-minute video + package, §9.2) |
| **Congress Day** | 26 December 2026 · Daffodil International University, Ashulia |

> **Status — read this first.** This repository is an architectural **template and clickable
> prototype**. Nothing has been installed, trained, deployed or run. Source files are typed,
> documented stubs. The prototype in [`prototype/`](prototype/) renders **synthetic** data
> and says so on every screen. No accuracy, loss-reduction or performance figure is claimed
> anywhere, because none has been measured (Congress §15, §20.4).

---

## What Crop Guardian does

```
 farmer photographs a sick leaf (Bangla UI, works on a cheap phone, queues offline)
        │
        ▼
 vision model → disease + confidence + heat-map of the lesion
        │            └── low confidence? → "not sure" → routed to a human agronomist
        ▼
 RAG advisory agent → what to do, in Bangla, citing the DAE / BRRI / BARI source
        │
        ▼
 diagnosis stored with coarse location → outbreak clustering → alert to nearby farmers
        │
        ▼
 agronomist confirms or corrects → labelled image → next training round (data flywheel)
```

## Where to start

| You are… | Read |
|---|---|
| New to the project | [`docs/system-design/SDD.md`](docs/system-design/SDD.md) — the master System Design Document |
| Judge / mentor | [`docs/congress/rubric-map.md`](docs/congress/rubric-map.md) then open [`prototype/index.html`](prototype/index.html) |
| On the team | [`docs/plan/gantt.md`](docs/plan/gantt.md) (16–29 Oct, per person, per day) and [`CLAUDE.md`](CLAUDE.md) |
| Deploying | [`docs/deployment/render-guide.md`](docs/deployment/render-guide.md) and [`docs/deployment/challenges-and-recovery.md`](docs/deployment/challenges-and-recovery.md) |
| Testing | [`docs/testing/test-strategy.md`](docs/testing/test-strategy.md) and [`tests/`](tests/) |

The full design is also rendered as a PDF report:
`docs/report/CropGuardian-System-Design-Report.pdf` (rebuild with `python scripts/build_report.py`).

## Repository map

```
cropguardian/
├── prototype/            clickable static UI — open index.html, no build, no server
├── apps/web/             React + Vite + TypeScript SPA (typed stubs)
├── services/api/         FastAPI backend (typed stubs) — deploys to Render
├── db/                   PostgreSQL schema, RLS policies, migrations, synthetic seed
├── ml/                   vision training/export, outbreak risk, RAG, evaluation, registry
├── automation/n8n/       workflow specifications (alerts, digest, drift, keep-warm, monitors)
├── tests/                unit · whitebox · blackbox · integration · timeout · concurrency
│                         · security · ml · e2e · manual · n8n
├── docs/                 SDD, architecture + ADRs, data, AI, security, deployment,
│                         testing, plan (Gantt), congress, product, research, report
├── scripts/              build_report.py — the only executable script
└── render.yaml           Render blueprint (static site + API web service)
```

## Stack at a glance

| Layer | Choice | Decision record |
|---|---|---|
| Frontend | React + Vite + TS, PWA, Bangla default | [ADR 0001](docs/architecture/adr/0001-react-spa-pwa.md) |
| Backend | FastAPI (Python 3.12), modular monolith, Docker on Render free | [ADR 0002](docs/architecture/adr/0002-fastapi-modular-monolith.md) |
| Data | Supabase Postgres + pgvector + Storage + Auth | [ADR 0003](docs/architecture/adr/0003-supabase-not-render-postgres.md) |
| Vision | Transfer-learned CNN/ViT → ONNX int8 on CPU | [ADR 0004](docs/architecture/adr/0004-onnx-cpu-inference.md) |
| Safety | Calibrated confidence + abstain + human review | [ADR 0005](docs/architecture/adr/0005-abstain-and-human-review.md) |
| Advice | RAG with mandatory citations | [ADR 0006](docs/architecture/adr/0006-rag-citation-enforcement.md) |
| Automation | n8n | [ADR 0008](docs/architecture/adr/0008-n8n-automation-plane.md) |

## Team (Congress §13.2 — every role owned by a named member)

| Member | Role |
|---|---|
| **Apon** | Team Leader · Backend · Database · ML integration · Deployment |
| **Taeen** | Data Scientist · model training & statistics · backend support |
| **Salwa** | AI integration — RAG, knowledge base, LLM evaluation |
| **Raisa** | AI integration — advisory agent, Bangla prompts & voice · Presentation lead *(to confirm)* |
| **Sara** | UI/UX & Frontend lead |
| *Open* | Virtual NRB / global advisor (§8) |

## Licence
MIT — see [`LICENSE`](LICENSE). Participants retain IP (Congress §20.7).
