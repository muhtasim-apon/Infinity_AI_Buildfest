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
├── AI Builders Congress 2026 - Participants Guide.pdf     the source brief (30 pages)
└── cropguardian/                                          the repository TEMPLATE (docs + specs, no code)
    ├── prototype/index.html                               ← clickable prototype (open in a browser)
    ├── docs/system-design/SDD.md                          ← System Design Document
    ├── docs/deployment/                                   ← zero-to-deploy, Render, Supabase, platforms,
    │                                                        free-tier challenges & "Render turned us off" runbook
    ├── docs/security/security-checklist.md                ← the 19 security controls, each with its test
    ├── docs/plan/gantt.md                                 ← day-by-day plan 16–29 Oct, per member
    ├── services/api/SPEC.md · apps/web/SPEC.md · db/SCHEMA-SPEC.md   ← what to build
    └── docs/report/CropGuardian-System-Design-Report.pdf  ← the whole design as one PDF
```

`cropguardian/` is a **template**: specifications, guides and test-case tables — **no application
code**. The team writes the code piece by piece from the specs, following the Gantt. The prototype is
static HTML with **synthetic** data, labelled on every screen. Nothing has been trained or deployed and
no accuracy or impact figure is claimed (Congress §15, §20.4).

Scope decision: **no human-review features** in this version — uncertain photos get an honest "not
sure" with retake tips, and outbreak alerts are automatic, rule-based and labelled "unverified".

## Next steps
1. Read [`cropguardian/docs/deployment/00-zero-to-deploy.md`](cropguardian/docs/deployment/00-zero-to-deploy.md) at today's stand-up — Phase 0–2 and 8.1 (prototype live) today.
2. Push `cropguardian/` as the root of a new GitHub repository; replace CODEOWNERS handles.
3. Day-1 critical path: datasets (Taeen) and Bangla knowledge-base documents (Salwa).
4. Work the [security checklist](cropguardian/docs/security/security-checklist.md) and the [submission checklist](cropguardian/docs/congress/submission-checklist.md) toward 30 Oct.
