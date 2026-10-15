# apps/web — Crop Guardian web app (React + Vite + TypeScript, PWA)

Owner: **Sara**. Status: **typed stubs — not installed or built.** The visual design to build
toward is the clickable prototype in [`../../prototype/`](../../prototype/).

```
src/
├── main.tsx            bootstrap: i18n, QueryClient, router, service worker registration
├── routes.tsx          all routes (Congress §10.8 pattern)
├── i18n/bn.json        SOURCE locale (ADR 0007)
├── i18n/en.json        same keys (CI gate)
├── lib/api.ts          the ONLY place that calls the API; timeouts, retries, waking state
├── lib/outbox.ts       IndexedDB offline queue (ADR 0009)
├── lib/image.ts        compression + EXIF strip + sha256 + coarse location
└── features/
    ├── scan/           camera/file input, quality hint, send
    ├── diagnosis/      result: top-3, band, heat-map, abstain state
    ├── advisory/       steps, dose, safety, citations, voice
    ├── history/        my scans
    ├── alerts/         alerts list + map, subscription
    ├── review/         agronomist queue
    ├── admin/          settings, models, KB, users
    ├── audit/          one-click report
    └── showcase/       /data /security /architecture /presentation /pitchdeck
```

## Routes
| Route | Who | Feature |
|---|---|---|
| `/` | all | landing → `/app` |
| `/app`, `/app/scan`, `/app/result/:id`, `/app/history`, `/app/alerts` | farmer | scan … alerts |
| `/app/review` | agronomist | review |
| `/demo-user`, `/demo-admin` | judges | one-click demo session |
| `/admin` | admin | admin |
| `/data`, `/security`, `/architecture`, `/presentation`, `/pitchdeck` | public | showcase |
| `/audit` | admin / demo | audit |

## Rules
- No secrets: only `VITE_SUPABASE_ANON_KEY` (CI fails on "SERVICE_ROLE" in `src/`).
- Never render LLM/KB text as HTML (`dangerouslySetInnerHTML` banned by lint rule).
- Every screen tested in `bn` and `en` at 360×740 (Playwright).
- Synthetic banner component on every screen while demo data is in use.
