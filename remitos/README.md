<div align="center">

# RemitOS

### The intelligence and orchestration layer for borderless money

**Idea to Unicorn · FinSphere AI · Borderless Money**
International AI Builders Congress 2026 · Daffodil International University · 26 December 2026

`Flutter` · `Python/FastAPI microservices` · `RAG + GraphRAG` · `Multi-agent AI` · `n8n` · `Kubernetes`

</div>

---

> **Repository status — read this first.**
> This is a **production-grade architectural template and documentation set**. Every
> source file is a typed, documented **stub**. Nothing in this repository has been
> compiled, installed, deployed or executed. It is the blueprint a team builds from
> across the Congress's six-month journey — not a running system. Any data shipped
> under `data/synthetic/` is explicitly synthetic and labelled as such.

---

## 1. The problem, in four numbers

| | |
|---|---|
| **6.36 %** | global average cost to send USD 200 (World Bank RPW, Q3 2025) — against an SDG target of **3 %** |
| **2.71 pp** | the gap between non-digital (7.30 %) and digital (4.59 %) remittance cost — the entire economic opportunity |
| **≈ 49 %** | estimated share of remittances to Bangladesh arriving through informal *hundi* channels |
| **USD 35.56 bn** | Bangladesh's FY 2025-26 formal remittance inflow, 7th largest in the world |

Bangladesh does not have a remittance *volume* problem. It has a **routing, compliance
and trust** problem. Full sourcing in [`docs/research/data/`](docs/research/data/).

## 2. What RemitOS is

RemitOS is **not another wallet**. bKash, Nagad, Rocket, the banks and the MTOs are
rails, and rails are not the gap. The gap is that **no neutral party computes the
routing decision**: which combination of corridor, rail, FX window and payout endpoint
delivers the most taka into a recipient's hands, fastest, within regulatory limits.

RemitOS is that decision layer:

```
              ┌─────────────────────────────────────────────┐
   Sender ───▶│  RemitOS — intelligence & orchestration      │───▶ Recipient
              │  routing · compliance · FX timing · payout   │
              └───────────────────┬─────────────────────────┘
                                  │ treats every rail as interchangeable
        ┌──────────┬──────────┬───┴──────┬──────────┬──────────┐
      bKash      Nagad      Rocket     Banks      MTOs      Agent cash
```

### The three AI capabilities that carry the product

1. **Routing optimisation** — ML-predicted landed cost and arrival time per rail, solved
   under regulatory constraints (Bangladesh Bank's Tk 30,000/day cash-out ceiling is a
   hard constraint in the optimiser, not an error message after the fact).
2. **Compliance automation** — RAG-grounded AML/KYC decisioning over Bangladesh Bank
   circulars, FATF guidance and sanctions lists, with every decision citing its source
   and escalating to a human at defined gates.
3. **Predictive FX timing** — forecasting the send window, expressed to the user as
   plain Bangla advice, not a chart.

## 3. Repository map

| Path | What lives there |
|---|---|
| [`docs/report/`](docs/report/) | The master report (HTML source → **PDF**) |
| [`docs/research/`](docs/research/) | Every statistic, with source URL and access date |
| [`docs/architecture/`](docs/architecture/) | C4 diagrams, ADRs, data flows |
| [`docs/ai/`](docs/ai/) | Model cards, RAG design, agent design, evaluation plan |
| [`docs/security/`](docs/security/) | Threat model, data sovereignty, AML/KYC policy |
| [`docs/product/`](docs/product/) | Personas, user journeys, PRD |
| [`docs/congress/`](docs/congress/) | Rubric map, submission checklist, pitch & demo scripts |
| [`apps/mobile/`](apps/mobile/) | Flutter — Android · iOS · Web from one codebase |
| [`services/`](services/) | 14 microservices |
| [`ml/`](ml/) | Pipelines, models, RAG, agents, evaluation |
| [`data/`](data/) | Schemas, contracts, lineage, dbt, synthetic generators |
| [`automation/n8n/`](automation/n8n/) | 12 workflow specifications |
| [`infra/`](infra/) | Docker · Kubernetes · Terraform · observability |

## 4. Domain-pack architecture — why this template outlives one idea

The core platform (identity, ledger, KYC, RAG, agents, automation, observability) knows
nothing about remittance. Each FinSphere vertical is a **swappable domain pack**:

```
domain_packs/
├── borderless_money/   ← active: cross-border payments & remittance intelligence
├── credit/             ← stub: CreditForAll — alternative-data credit scoring
├── fraud/              ← stub: FraudShield — real-time transaction defence
├── wealth/             ← stub: WealthPilot — AI advisory for everyday savers
└── sme/                ← stub: SME Capital Engine — working-capital intelligence
```

A pack supplies four things and nothing else: **config**, **schemas**, **prompts**,
**models**. Switching verticals is a pack swap, not a rewrite. See
[`docs/architecture/adr/0002-domain-pack-architecture.md`](docs/architecture/adr/0002-domain-pack-architecture.md).

## 5. Building the report PDF

```bash
python scripts/build_report.py      # docs/report/report.html → RemitOS-Borderless-Money-Report.pdf
```
Requires WeasyPrint. This is the only script intended to be run, and it only reads local
HTML and writes a PDF.

## 6. Congress alignment

[`docs/congress/rubric-map.md`](docs/congress/rubric-map.md) maps every line of the
100-point Idea to Unicorn rubric (§11.1), every mandatory submission component (§9.1)
and every item in the Final Unified Requirement (§14) to a concrete path in this
repository. Any unmapped line is treated as a gap.

## 7. Licence

MIT — see [LICENSE](LICENSE). Participants retain full IP ownership under Congress
§20.7; open-source publication is voluntary.

---

<div align="center">
<sub>Build Locally. Lead Globally.</sub>
</div>
