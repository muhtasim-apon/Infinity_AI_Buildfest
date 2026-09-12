# Submission Checklist & Six-Month Plan

## Official timeline (§3) — authoritative dates, all 12:00 PM BST

| Date | Milestone | Our deliverable |
|---|---|---|
| 1 Jul 2026 | Registration opens | Team registered, roles assigned (§13.2), NRB advisor secured (§8) |
| 1 Aug 2026 | I2U preliminary submission opens | — |
| 15 Aug 2026 | Volunteer assignment | — |
| 1 Sep 2026 | Mentor assignment | Architecture review booked with mentor |
| **31 Oct 2026** | **I2U preliminary submission LAST DATE** | **3-min video + full package** |
| 15 Nov 2026 | I2U preliminary selection announced | — |
| 1–30 Nov 2026 | Phase 4 — hardening | Production build, scalability, ethics safeguards |
| 1–25 Dec 2026 | Phase 5 — finalise & rehearse | Deployed product, polished demo |
| **26 Dec 2026** | **Congress Day** | Live judging 11:00–13:00 or 14:00–15:00 |

## Phase plan mapped to Congress phases (§3)

| Phase | Window | Congress focus | Our deliverables |
|---|---|---|---|
| **0** Launch & Onboarding | Jul | Registration, team formation | Roles, NRB, domain locked: FinSphere → Borderless Money |
| **1** Learn & Design | Aug | AI-native foundations, architecture | ✅ **This repository** — 12 ADRs, C4, threat model, 8 model cards, master report |
| **2** Build & Prototype | Sep | AI core, knowledge layer, vertical slice | RAG over real circulars · routing engine v1 · Flutter J1 flow · working demo video |
| **3** Validate & Iterate | Oct | User testing, market validation, mentor/NRB review | 15+ user interviews incl. rural recipients · **real unit economics** · legal opinion on licensability · **submit by 31 Oct** |
| **4** Selection & Hardening | Nov | Productionise, secure, localise | k8s deploy · security review · full Bangla · IVR path live · fairness evaluation run |
| **5** Finalise & Rehearse | Dec | Deployment, demo rehearsal | Offline demo · fallback video · Q&A drilled · demo rehearsed 10+ times |
| **6** Congress | 26 Dec | Live judging, Opportunity Connect | Judged once, in assigned group |

## Preliminary submission package (due 31 Oct)

- [ ] 3-minute structured video pitch — script in `video-pitch-script.md`
- [ ] Problem Definition — report §1–7
- [ ] AI Architecture — `docs/architecture/`, `docs/ai/`
- [ ] Data & Sovereignty Strategy — `docs/security/data-sovereignty.md`
- [ ] Demo / prototype / workflow (early-stage acceptable per §9.2)
- [ ] Scalability Roadmap — report §19
- [ ] Ethical Safeguards — model cards, eval plan, ADR 0010
- [ ] Bangla / localization evidence — ADR 0012 + screen recording
- [ ] Defined KPIs — `docs/product/prd.md` §7
- [ ] Team roles declared (§13.2) with NRB contribution documented (§8)
- [ ] Code of Conduct agreement signed (§20)

## Congress Day readiness

- [ ] Demo runs **fully offline**
- [ ] Second device at demo state
- [ ] Offline fallback video on the machine
- [ ] Printed handout of the J3 split screen
- [ ] All synthetic data labelled on screen
- [ ] Bangla verified **on the projector**
- [ ] Five prepared Q&A answers drilled (`demo-script.md`)
- [ ] Team knows the four source numbers cold
- [ ] Presentation Lead owns timing; hard cut at 3:00

## Team composition targets (§13.3)

| Dimension | Requirement | Status |
|---|---|---|
| Technical capability | 2–3 members able to build full-stack AI | TBD |
| Business / domain | 1 member on users, value, adoption | TBD |
| Women participation | ≥ 1 female participant (bonus points) | TBD |
| Polytechnic / madrasah inclusion | Cross-institution where possible | TBD |
| NRB / diaspora | Assigned role in architecture, strategy or data | TBD |

## Standing risks to the submission itself

| Risk | Mitigation |
|---|---|
| Over-scoping and finishing nothing (§13.4 #7) | One core use case: the routing decision. Packs stay stubs until it is finished |
| Demo fails in the hall | Offline-first, second device, video, printed handout |
| Bangla breaks on unfamiliar hardware | Verified on projector in Phase 5, with subset fonts bundled |
| Models untrained by Congress Day | Stated plainly. An honest specification with an evaluation plan scores better than a fabricated accuracy figure, and §20.4 makes the alternative disqualifiable |
| Team member drops out | Every role has a named backup; no single point of knowledge |
