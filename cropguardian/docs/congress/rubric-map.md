# Rubric map — Idea to Unicorn judging (S1 §11.1, 5 × 20 = 100)

Score bands: 0–5 weak · 6–10 moderate · 11–15 strong · 16–20 breakthrough (S1 §11.2).
For each component: what judges evaluate → our evidence → where to show it.

## 1. Innovation & AI-Native Design (20)
*Originality, creativity, non-obvious, transformative application of AI.*
| Evidence | Where |
|---|---|
| AI core is the product: vision → calibrated abstention → cited Bangla advice → outbreak alerts → data flywheel | `/architecture`, SDD §6–7 |
| "Knows when it doesn't know" — abstain + agronomist loop (most disease apps always answer) | result screen, ADR 0005 |
| Crowd-sourced early warning from individual diagnoses | `/app/alerts`, outbreak model card |
| Not a chatbot gimmick (S1 §13.4 #1) — the LLM only explains; the vision model diagnoses | agent-design |

## 2. Technical Excellence & Architecture (20)
*Architecture quality, AI integration depth, robustness, explainability.*
| Evidence | Where |
|---|---|
| Documented architecture, 10 ADRs, sequence diagrams, ERD | `docs/architecture/`, `/architecture` |
| Model comparison across 5 families with a pre-registered selection rule; statistics with CIs, McNemar, calibration | `docs/ai/vision-model.md`, `statistics.md` |
| RAG with citation enforcement + validator; bounded agent | `rag-design.md`, `agent-design.md` |
| Free-tier-aware engineering: stateless API, outbox, idempotency, cold-start handling | `challenges-and-recovery.md` |
| Test strategy: whitebox/blackbox/timeout/concurrency/security/ML/E2E/n8n | `docs/testing/`, `tests/` |

## 3. Business Value & Commercial Viability (20)
*Measurable economic value, value proposition, path to sustainable business.*
| Evidence | Where |
|---|---|
| Value: earlier correct action on disease; fewer wasted sprays (to be measured in pilot) | PRD §6 |
| Revenue model: free for farmers; B2B/B2G — extension services dashboard, agri-input companies (non-promotional, IPM-first), insurers (aggregate risk), NGOs | PRD §7 |
| KPIs defined; pilot protocol pre-registered | `eval-plan.md` §5 |

## 4. Global Scalability & Real-World Impact (20)
*Scale to millions and international markets; jobs, productivity, societal benefit.*
| Evidence | Where |
|---|---|
| Domain packs: more crops, Precision Farm, YieldMax | ADR 0010 |
| Portable: Docker API + Postgres → any cloud or in-country DC | data-sovereignty |
| Language packs (Bangla first; Hindi/Nepali/Swahili feasible) | ADR 0007 |
| Agriculture ≈ 45 % of employment in Bangladesh [S5] | SDD §1 |

## 5. Responsible AI, Data Sovereignty & Presentation (20)
*Fairness, explainability, bias mitigation, privacy, governance, data ownership; clarity.*
| Evidence | Where |
|---|---|
| Abstain, citations, heat-maps, per-slice evaluation | responsible-ai.md |
| Privacy: EXIF strip, coarse location, no PII to LLM, consent per purpose | privacy.md |
| Data ownership, no data sale, licences recorded | data-sovereignty.md, datasets.md |
| One-click `/audit` report | audit-readiness.md |
| Presentation follows Problem → Solution → Demo → AI → Impact (S1 §9.3, §13.4 #9) | video-pitch-script.md |

## Mandatory preliminary requirements (S1 §9.2) — checklist
- [ ] 3-minute structured video pitch → `video-pitch-script.md`
- [ ] Clear problem and user definition → SDD §1–2, personas
- [ ] AI-native approach (LLM / RAG / ML) → SDD §10
- [ ] Basic system flow (input → AI → output) → data-flow.md
- [ ] Initial demo / prototype / workflow → `prototype/`, live URL
- [ ] Bangla / localization → ADR 0007, prototype bn default
- [ ] Defined potential impact (KPIs) → SDD §4
