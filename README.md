# BRAC U Hackathon — International AI Builders Congress 2026

Working folder for the Congress submission.

| | |
|---|---|
| **Track** | Idea to Unicorn (team project) |
| **Domain** | AgriSphere AI — Agriculture, Food Security & Rural Prosperity |
| **Challenge area** | **Crop Guardian** — early pest and disease detection from imagery |
| **Capabilities to demonstrate** | Vision models · Alerts · Local-language UX |
| **Winning signal** | Loss reduction at the field level |
| **Product** | Web application only (mobile-first PWA) |
| **Team** | Apon (lead · backend · DB · ML integration · deploy) · Taeen (ML & data) · Salwa (AI — RAG) · Raisa (AI — agent & Bangla · presentation) · Sara (frontend) |
| **Preliminary deadline** | **31 October 2026, 12:00 BST** |
| **Congress Day** | 26 December 2026, Daffodil International University, Ashulia, Dhaka |

---

## What is here

```
.
├── AI Builders Congress 2026 - Participants Guide.pdf   the source brief (30 pages)
└── cropguardian/                                        the project template
    ├── prototype/index.html                             ← CLICKABLE PROTOTYPE (open in a browser)
    ├── docs/system-design/SDD.md                        ← THE SYSTEM DESIGN DOCUMENT
    ├── docs/report/CropGuardian-System-Design-Report.pdf ← the same design as a 67-page PDF
    ├── docs/plan/gantt.md                               ← day-by-day plan, 16–29 Oct, per member
    └── …                                                docs, schema, API/web stubs, ML, tests, n8n
```

### 1. The clickable prototype
Open **`cropguardian/prototype/index.html`** — no install, no server. Bangla by default (English
toggle), phone-first, dark mode. Every Congress §10.8 route has a page: `/app`, `/demo-user`,
`/demo-admin`, `/admin`, `/data`, `/security`, `/architecture`, `/presentation`, `/pitchdeck`, `/audit`.

### 2. The design
Architecture & ADRs · ER model & SQL schema with RLS · data flow & sequence diagrams · vision-model
selection & statistics · RAG with citation enforcement · advisory agent · security (STRIDE, OWASP,
OWASP LLM) · Render free-tier deployment with a full **challenges & recovery playbook** · test strategy
(unit, whitebox, blackbox, integration, timeout, concurrency, security, ML, E2E, manual, n8n) ·
rubric map · video-pitch script. Index: [`cropguardian/docs/README.md`](cropguardian/docs/README.md).

### 3. The template
`cropguardian/` is a GitHub-ready repository: React/Vite web stubs, FastAPI stubs, PostgreSQL schema,
ML configs, n8n workflow specs, test stubs, CI quality gates, `render.yaml`.

> **Nothing has been installed, trained, deployed or run.** Source files are typed, documented stubs;
> the prototype uses synthetic data and says so on every screen. No accuracy or impact figure is
> claimed anywhere (Congress §15, §20.4).

## Next steps
1. Read the [Gantt](cropguardian/docs/plan/gantt.md) at today's stand-up; confirm Raisa as presentation lead.
2. Replace the handles in `cropguardian/.github/CODEOWNERS`; create the GitHub repo from `cropguardian/`.
3. Day-1 critical path: datasets (Taeen) and Bangla knowledge-base documents (Salwa).
4. Work [`submission-checklist.md`](cropguardian/docs/congress/submission-checklist.md) toward 30 Oct.

Rebuild the PDF: `python cropguardian/scripts/build_report.py`.
