# BRAC U Hackathon — International AI Builders Congress 2026

Working folder for the Congress submission.

| | |
|---|---|
| **Track** | Idea to Unicorn (team project, six-month journey) |
| **Domain** | FinSphere AI — Reimagining Global Financial Services |
| **Challenge area** | **Borderless Money** — cross-border payments and remittance intelligence |
| **Capabilities to demonstrate** | Compliance automation · Routing optimisation |
| **Winning signal** | Lower cost · Faster settlement |
| **Congress Day** | 26 December 2026, Daffodil International University, Ashulia, Dhaka |
| **Preliminary deadline** | **31 October 2026, 12:00 BST** |

---

## What is here

```
.
├── AI Builders Congress 2026 - Participants Guide.pdf    the source brief (30 pages)
└── remitos/                                              the project
    ├── docs/report/RemitOS-Borderless-Money-Report.pdf   ← THE REPORT (82 pages)
    └── …                                                 the production template
```

### 1. The report

**`remitos/docs/report/RemitOS-Borderless-Money-Report.pdf`** — 82 pages, 26 chapters,
4 appendices, 30 numbered sources.

It is written for a reader who knows nothing about cross-border payments and works up to
a full production architecture: what borderless money is · how money physically moves ·
the global statistics · Bangladesh's eleven constraints · how each is overcome · the
competitive landscape including *hundi* and the PayPal gap · an honest chapter on what
this project cannot do · rural usability · the technical architecture · AI/ML/RAG/agents ·
security and sovereignty · responsible AI · business model · roadmap · risk register.

Rebuild it with `python remitos/scripts/build_report.py`.

### 2. The production template

**`remitos/`** — a GitHub-style repository: Flutter (Android · iOS · Web), 14
microservices, 8 ML models, RAG with GraphRAG, 5 AI agents, 12 n8n workflows, Kubernetes
and Terraform, 12 ADRs, 8 model cards, threat model, evaluation plan.

> **Nothing in it has been compiled, installed, deployed or run.** Every source file is a
> typed, documented stub. It is the blueprint a team builds from across the six-month
> journey — not a running system.

Start at [`remitos/README.md`](remitos/README.md).

---

## The argument, in four numbers

| | |
|---|---|
| **6.36 %** | global average cost to send USD 200 (World Bank, Q3 2025) — against a UN target of 3 % |
| **2.71 pp** | the measured gap between non-digital (7.30 %) and digital (4.59 %) cost |
| **≈ 49 %** | estimated share of remittances to Bangladesh arriving through informal *hundi* |
| **USD 35.56 bn** | Bangladesh's FY 2025-26 formal inflow — 7th largest in the world |

Bangladesh does not have a remittance volume problem. It has a **routing, compliance and
trust** problem. Every rail already exists; what does not exist is a neutral party that
computes which rail, which FX window and which payout endpoint delivers the most taka,
soonest, within the law.

**RemitOS is that decision layer** — not another wallet.

---

## Switching to a different fintech vertical

The core is domain-agnostic. Each FinSphere challenge area is a swappable **domain pack**
supplying four things and nothing else: config, schemas, prompts, models.
`borderless_money` ships active; `credit`, `fraud`, `wealth` and `sme` ship as stubs with
their extension points declared. See
[ADR 0002](remitos/docs/architecture/adr/0002-domain-pack-architecture.md).

## Next steps

1. Fill the team roles in `remitos/CONTRIBUTING.md` and `remitos/.github/CODEOWNERS`
2. Secure the NRB advisor (Congress §8)
3. Work `remitos/docs/congress/submission-checklist.md` against the phase plan
4. Phase 3 validation — including rural recipient interviews — fills the blank
   unit-economics model in the PRD with measured numbers

Everything not yet measured is marked as such, deliberately: Congress §20.4 prohibits
fabricated results presented as real, and no accuracy, cost or performance figure is
claimed anywhere in this work.
