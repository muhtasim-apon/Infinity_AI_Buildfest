# Crop Guardian — ফসল রক্ষী

**Early pest and disease detection from a phone photo, with Bangla advice and outbreak alerts.**

| | |
|---|---|
| **Track** | Idea to Unicorn (team project) — International AI Builders Congress 2026 |
| **Domain** | AgriSphere AI — Agriculture, Food Security & Rural Prosperity |
| **Challenge area** | **Crop Guardian** — early pest and disease detection from imagery |
| **Capabilities to demonstrate** | Vision models · Alerts · Local-language UX (Participants Guide §6.4) |
| **Winning signal** | Loss reduction at the field level |
| **Product surface** | **Web app only** (mobile-first PWA) |
| **Preliminary deadline** | **31 October 2026, 12:00 BST** (3-minute video + package, §9.2) |
| **Congress Day** | 26 December 2026 · Daffodil International University, Ashulia |

> **Status — read this first.** The backend (FastAPI), the React frontend, the database migrations and
> the identity/session system exist, and the Phase 0 and Phase 1 gates pass; Phase 2 (design system, app
> shells, landing page) is in progress. See [`PROGRESS.md`](PROGRESS.md) for the live status and gate tables.
> The static clickable [`prototype/`](prototype/README.md) shows **synthetic** data and says so on every
> screen. Nothing has been trained; no accuracy or impact figure is claimed (Congress §15, §20.4).

### See it running (local)

| What | Command / URL |
|---|---|
| Start the stack | `make env certs up` (needs Docker), then `make migrate` once |
| Open the app | **https://localhost** (self-signed certificate: click *Advanced → Proceed*, or install [mkcert](https://github.com/FiloSottile/mkcert) and re-run `make certs` for a green lock) |
| Rebuild the frontend after a change | `make web` (nginx serves `frontend/dist`) |
| Hot-reload dev server | `make dev` → **http://localhost:5180** (proxies `/api` to the stack above) |
| Prove it works | `make gate PHASE=2` and the checklist in [`docs/testing/MANUAL_CHECKLIST_P0-P2.md`](docs/testing/MANUAL_CHECKLIST_P0-P2.md) |

Port note: the dev server deliberately does **not** use 5173, which other Vite projects on the same
machine usually hold; if you see a different app there, that is why.

---

## What Crop Guardian does

```
 farmer photographs a sick leaf (Bangla UI, works on a cheap phone, queues offline)
        │
        ▼
 vision model → disease + calibrated confidence + heat-map
        │            └── low confidence → "not sure": retake tips + local agriculture office card
        ▼
 advisory agent → what to do, in Bangla, citing the DAE / BRRI / BARI source
        │
        ▼
 diagnosis stored with coarse location → outbreak rules → automatic in-app alert
                                          (labelled "possible outbreak — unverified")
```

## Where to start

| You are… | Read |
|---|---|
| New to the project | [`docs/system-design/SDD.md`](docs/system-design/SDD.md) — the System Design Document |
| Deploying | [`docs/deployment/README.md`](docs/deployment/README.md) → [zero to deployment](docs/deployment/00-zero-to-deploy.md) (all URLs) |
| Securing & testing | [`docs/security/security-checklist.md`](docs/security/security-checklist.md) · [`docs/testing/security-testing-guide.md`](docs/testing/security-testing-guide.md) |
| Building the API / web / DB | [`services/api/SPEC.md`](services/api/SPEC.md) · [`apps/web/SPEC.md`](apps/web/SPEC.md) · [`db/SCHEMA-SPEC.md`](db/SCHEMA-SPEC.md) |
| On the team | [`docs/plan/gantt.md`](docs/plan/gantt.md) (16–29 Oct, per person, per day) · [`CLAUDE.md`](CLAUDE.md) |
| Judge / mentor | [`docs/congress/rubric-map.md`](docs/congress/rubric-map.md) and the [prototype](prototype/index.html) |
| Datasets & external resources | [`docs/research/external-resources.md`](docs/research/external-resources.md) |
| Expected impact (loss reduction) | [`docs/evaluation/field-loss-reduction.md`](docs/evaluation/field-loss-reduction.md) |

PDF of the whole design: [`docs/report/CropGuardian-System-Design-Report.pdf`](docs/report/CropGuardian-System-Design-Report.pdf).

## Repository map

```
cropguardian/
├── prototype/            clickable static UI (HTML/CSS/JS) — open index.html; first public URL
├── apps/web/             SPEC.md + i18n strings (bn/en) — React PWA to build
├── services/api/         SPEC.md — FastAPI service to build (17 endpoints)
├── db/                   SCHEMA-SPEC.md — tables, RLS, buckets, seed
├── ml/                   training spec, export, RAG ingestion, evaluation template, registry
├── automation/n8n/       workflow specs 01–08
├── tests/                test-case tables per type (unit … security, ml, e2e, manual, n8n)
├── docs/                 SDD, architecture + ADRs, data, AI, security, deployment guides,
│                         testing, plan (Gantt), congress, product, research, report (PDF)
├── .github/              CODEOWNERS, PR/issue templates, CI/CD spec (README)
└── .env.example          every environment variable, secret vs public
```

## Stack at a glance

| Layer | Choice | Decision record |
|---|---|---|
| Frontend | React + Vite + TS, PWA, Bangla default — Render static site | [ADR 0001](docs/architecture/adr/0001-react-spa-pwa.md) |
| Backend | FastAPI (Python 3.12), modular monolith, Docker — Render free web service | [ADR 0002](docs/architecture/adr/0002-fastapi-modular-monolith.md) |
| Data | Supabase Postgres + pgvector + private Storage + Auth (+ Turnstile CAPTCHA) | [ADR 0003](docs/architecture/adr/0003-supabase-not-render-postgres.md) |
| Vision | Transfer-learned CNN/ViT → ONNX int8 on CPU | [ADR 0004](docs/architecture/adr/0004-onnx-cpu-inference.md) |
| Safety | Calibrated confidence + honest "not sure" | [ADR 0005](docs/architecture/adr/0005-calibrated-abstain.md) |
| Advice | RAG with mandatory citations | [ADR 0006](docs/architecture/adr/0006-rag-citation-enforcement.md) |
| Automation | n8n (+ UptimeRobot / GitHub Actions fallbacks) | [ADR 0008](docs/architecture/adr/0008-n8n-automation-plane.md) |

## Team (Congress §13.2)

| Member | Role |
|---|---|
| **Apon** | Team Leader · Backend · Database · ML integration · Deployment · Security |
| **Taeen** | Data Scientist · model training & statistics · backend support |
| **Salwa** | AI integration — RAG, knowledge base, LLM evaluation & red-team |
| **Raisa** | AI integration — advisory agent, Bangla prompts & voice · Presentation lead *(to confirm)* |
| **Sara** | UI/UX & Frontend lead |
| *Open* | Virtual NRB / global advisor (§8) |

## Licence
MIT — see [`LICENSE`](LICENSE). Participants retain IP (Congress §20.7).
