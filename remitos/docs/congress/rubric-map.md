# Rubric Map — every judging line mapped to an artefact

> Purpose: make gaps visible. **An unmapped line is a gap, not an oversight.** This file
> is updated whenever a change affects a rubric line (see `CONTRIBUTING.md`).

---

## A. Idea to Unicorn judging framework (§11.1) — 5 × 20 = 100 points

### 1. Innovation & AI-Native Design (20)
*"Originality, creativity, and non-obvious, transformative application of AI"*

| Claim | Evidence |
|---|---|
| Routing decision as an unoccupied market position | `docs/research/data/03-competitive-landscape.md` §3.2 |
| Regulatory ceilings as optimiser constraints, not validations | [ADR 0007](../architecture/adr/0007-regulatory-limits-as-constraints.md) |
| GraphRAG for the network signature of hundi agent activity | [ADR 0005](../architecture/adr/0005-graphrag-for-entity-risk.md) |
| Legal split proposal — a genuinely new user outcome | `docs/product/user-journeys.md` J3 |
| Domain-pack architecture as a commercial moat | [ADR 0002](../architecture/adr/0002-domain-pack-architecture.md) |

### 2. Technical Excellence & Architecture (20)
*"Architecture quality, AI integration depth, robustness, and explainability of the intelligence core"*

| Claim | Evidence |
|---|---|
| C4 L1–L3, 14 bounded contexts | `docs/architecture/system-overview.md` |
| 12 ADRs with rejected alternatives stated | `docs/architecture/adr/` |
| Double-entry event-sourced ledger | [ADR 0009](../architecture/adr/0009-double-entry-event-sourced-ledger.md) |
| Cite-or-refuse RAG with claim verification | [ADR 0004](../architecture/adr/0004-rag-with-citation-enforcement.md) |
| Explainability: reason codes, SHAP, citations, evidence bundles | `docs/ai/eval-plan.md` §4 |
| Graceful degradation ladder | `docs/architecture/system-overview.md` |
| Saga orchestration with compensating transactions | [ADR 0003](../architecture/adr/0003-microservices-boundaries.md) |

### 3. Business Value & Commercial Viability (20)
*"Measurable economic value, clear value proposition, realistic path to a sustainable, monetizable business"*

| Claim | Evidence |
|---|---|
| Quantified opportunity: the 2.71 pp digital/non-digital cost gap | `docs/research/data/01-global-remittance-baseline.md` |
| Five revenue lines with an explicit prohibition on user-level data sales | `docs/product/prd.md` §6 |
| Unit-economics **model** with human-review cost modelled, not fabricated figures | `docs/product/prd.md` §6 |
| Four-stage regulatory path with durations | `docs/product/regulatory-path.md` §3 |
| Partnership dependency risks named, including the bKash tension | `docs/product/regulatory-path.md` §4 |

### 4. Global Scalability & Real-World Impact (20)
*"Capacity to scale to millions and international markets, plus jobs, productivity, exports, or societal benefit"*

| Claim | Evidence |
|---|---|
| Flutter across Android, iOS, Web from one codebase | [ADR 0001](../architecture/adr/0001-flutter-for-all-clients.md) |
| Independently scalable services; k8s overlays; HPA | `infra/k8s/` |
| Corridor expansion model, sending-side licensing acknowledged | `docs/product/regulatory-path.md` §3 |
| Domain-pack extensibility to four further verticals | [ADR 0002](../architecture/adr/0002-domain-pack-architecture.md) |
| Addressable impact: the ~49 % informal-channel pool | `docs/research/data/02-bangladesh-market-constraints.md` §2.4 |
| Reach to the ~69 m connections without data plans | [ADR 0008](../architecture/adr/0008-offline-first-and-ussd.md) |

### 5. Responsible AI, Data Sovereignty & Presentation (20)
*"Fairness, explainability, bias mitigation, privacy, governance and data ownership — communicated with clarity and confidence"*

| Claim | Evidence |
|---|---|
| 8 model cards with per-group fairness as **release gates** | `docs/ai/model-cards/` |
| Device tier identified as a wealth proxy and gated | `docs/ai/eval-plan.md` §3 |
| Enforced residency boundary: tokenisation + egress filter + CI check | [ADR 0011](../architecture/adr/0011-data-residency-boundary.md) |
| Human gates on every irreversible action | [ADR 0010](../architecture/adr/0010-human-in-the-loop-gates.md) |
| Blind re-adjudication to detect rubber-stamping | `docs/security/aml-kyc-policy.md` §6 |
| STRIDE threat model incl. AI-specific threats and residual risks | `docs/security/threat-model.md` |
| Bangla-first as an architectural decision | [ADR 0012](../architecture/adr/0012-bangla-first-not-translated.md) |

---

## B. Mandatory submission components (§9.1)

| Component | Artefact | Status |
|---|---|---|
| Problem Definition | Report §1–§7; `docs/product/prd.md` §1 | ✅ |
| AI Architecture | `docs/architecture/`, `docs/ai/` | ✅ |
| Data & Sovereignty Strategy | `docs/security/data-sovereignty.md`, ADR 0011 | ✅ |
| Demo (live or recorded) | `docs/congress/demo-script.md` | 📋 script ready, build pending |
| Scalability Roadmap | Report §19; `infra/` | ✅ |
| Ethical Safeguards | `docs/ai/eval-plan.md`, model cards, ADR 0010 | ✅ |

## C. Preliminary submission (§9.2) — due 31 Oct 2026

| Requirement | Artefact | Status |
|---|---|---|
| 3-minute structured video pitch | `docs/congress/video-pitch-script.md` | ✅ scripted to the 5 segments |
| Clear problem and user definition | `docs/product/personas.md` | ✅ |
| AI-native approach (LLM/RAG/Graph/ML) | All four present | ✅ |
| Basic system flow (input → AI → output) | `docs/architecture/data-flow.md` | ✅ |
| Initial demo / prototype / workflow | Pending Phase 2 build | 📋 |
| Bangla / localization consideration | ADR 0012 | ✅ |
| Defined potential impact (KPIs) | `docs/product/prd.md` §7 | ✅ |

## D. Final Unified Requirement (§14)

| Requirement | Where | Status |
|---|---|---|
| AI-native architecture (not surface AI) | 8 models + RAG + GraphRAG + 5 agents | ✅ |
| Full-stack integration | Flutter + 14 services + ML + n8n + infra | ✅ |
| **RAG + Graph-based reasoning** | ADR 0004, ADR 0005 | ✅ |
| Real-world data via scraping/parsing | n8n 02, 04, 07 | ✅ |
| Personalization engine | Recipient recommender; per-user baselines in risk models | ✅ |
| Bangla + localization capability | ADR 0012, enforced in CI | ✅ |
| Scalable, cloud-ready design | `infra/k8s/`, `infra/terraform/` | ✅ |

## E. Top 10 Mistakes (§13.4) — pre-empted

| # | Mistake | How this project avoids it |
|---|---|---|
| 1 | AI as a gimmick | The AI *is* the product: routing and compliance. Remove it and there is no business |
| 2 | No clear problem definition | Four sourced numbers, five personas, explicit KPIs |
| 3 | Weak architecture thinking | 12 ADRs, C4 to L3, 14 bounded contexts |
| 4 | Ignoring real data | Every figure cited in `docs/research/data/`; n8n ingests live sources |
| 5 | No personalization | Per-user baselines, recipient recommender, personal-interval churn definition |
| 6 | No Bangla / localization | ADR 0012 — Bangla-first, CI-enforced |
| 7 | Overbuilding, nothing complete | One core use case: the routing decision. Four packs are declared stubs, not half-features |
| 8 | No scalability thinking | k8s overlays, HPA, independent scaling, corridor expansion model |
| 9 | Poor demo and storytelling | `demo-script.md` follows Problem → Solution → Demo → AI → Impact |
| 10 | Not leveraging team diversity | Roles per §13.2; NRB role declared per §8 |
| **Bonus** | Not using modern AI tools | Claude Code, MCP, RAG, agents, n8n throughout |
