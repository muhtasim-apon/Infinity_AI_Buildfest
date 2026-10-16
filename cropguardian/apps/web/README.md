# apps/web — Crop Guardian web app (React + Vite + TypeScript, PWA)

**Template folder — no code yet.** Everything to build is specified in **[`SPEC.md`](SPEC.md)**:
scaffold commands, file tree, routes, API client contract (cold start and retries), offline outbox,
image pipeline, the "not sure" screen, alerts, admin page protection, lint and CI rules.

Owner: **Sara**. Visual reference for every screen: the clickable [`prototype/`](../../prototype/README.md).
Ready-made Bangla and English strings: [`i18n/bn.json`](i18n/bn.json), [`i18n/en.json`](i18n/en.json)
(Bangla is the source locale — every key exists in both).

## Build order (Gantt)
| Day | What |
|---|---|
| 18 Oct | scaffold, routes, i18n wiring, synthetic banner |
| 19–21 Oct | scan screen, image pipeline, outbox, result + not-sure screens, waking-server state |
| 22–23 Oct | advice card with citations + voice, history, alerts list + map |
| 24–25 Oct | admin (lazy, role-gated), data / security / architecture / audit / presentation / pitch pages |
| 26–27 Oct | Playwright E2E (bn + en, phone size), accessibility, PWA polish |

## Run locally (once the code exists)
See [`docs/deployment/00-zero-to-deploy.md`](../../docs/deployment/00-zero-to-deploy.md) Step 6.
