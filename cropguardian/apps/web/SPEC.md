# Web app specification — `apps/web/` (React + Vite + TypeScript PWA)

**Status: specification only — no code yet.** Owner: **Sara**. Visual reference for every screen:
the clickable [`prototype/`](../../prototype/README.md). Bangla and English strings already exist in
[`i18n/bn.json`](i18n/bn.json) and [`i18n/en.json`](i18n/en.json) (move them to `src/i18n/` when the
project is scaffolded).

## 1. Scaffold (Gantt 18 Oct)
`npm create vite@latest web -- --template react-ts`, then add: react-router-dom, @tanstack/react-query,
i18next + react-i18next, @supabase/supabase-js, idb-keyval, vite-plugin-pwa, leaflet; dev: eslint +
typescript-eslint, vitest, @playwright/test, @axe-core/playwright. Commit `package-lock.json`
(Render runs `npm ci`, which needs it).

## 2. File tree to create
```
apps/web/
├── index.html               lang="bn", theme-color, title "ফসল রক্ষী — Crop Guardian"
├── vite.config.ts           react plugin + PWA manifest (lang bn, start_url /app, icons 192/512)
├── tsconfig.json            strict, noUncheckedIndexedAccess, noEmit
├── eslint.config.js         flat config; bans dangerouslySetInnerHTML; bans server-only env names
├── .env.example             VITE_* public variables only
└── src/
    ├── main.tsx             i18n (bn default) → QueryClient → router → SyntheticBanner
    ├── routes.tsx           routes table (§3), lazy-loaded pages
    ├── i18n/bn.json en.json
    ├── lib/api.ts           the ONLY module that calls the API (§4)
    ├── lib/outbox.ts        offline queue (§5)
    ├── lib/image.ts         compression + EXIF strip + sha256 + coarse location (§6)
    ├── lib/supabase.ts      supabase-js client with the PUBLISHABLE key only
    └── features/
        ├── scan/ HomePage ScanPage
        ├── diagnosis/ ResultPage NotSureCard
        ├── advisory/ AdvisoryCard
        ├── history/ HistoryPage
        ├── alerts/ AlertsPage
        ├── admin/ AdminPage (settings, models, KB, users, dismiss alert)
        ├── audit/ AuditPage
        └── showcase/ DemoEntry ShowcasePage (data, security, architecture, presentation, pitchdeck)
```

## 3. Routes
| Route | Who | Page | Prototype screen |
|---|---|---|---|
| `/` | all | redirect → `/app` | `index.html` |
| `/app`, `/app/scan`, `/app/result/:id`, `/app/history`, `/app/alerts` | farmer | scan → result → history → alerts | `app.html` |
| `/demo-user`, `/demo-admin` | judges | one-click demo (Turnstile widget, then token) | `demo-user.html`, `demo-admin.html` |
| `/admin` | admin | admin console — **lazy chunk loaded only after the API confirms role=admin** | `admin.html` |
| `/data` `/security` `/architecture` `/presentation` `/pitchdeck` | public | showcase | same names |
| `/audit` | admin, demo | one-click audit | `audit.html` |

"Hide admin pages properly": the admin chunk is not prefetched; the page renders nothing until
`GET /v1/admin/settings` succeeds; every admin action is authorised again by the API; admin routes send
`<meta name="robots" content="noindex">`.

## 4. `lib/api.ts` contract
- Base URL from `VITE_API_BASE_URL`; token from supabase-js session.
- **Cold start:** on app open call `GET /healthz`; while not 200 the UI shows "সার্ভার চালু হচ্ছে…".
  Timeout 90 s while waking, 30 s otherwise; retry ×3 with exponential backoff + jitter **only** for
  idempotent calls or calls carrying `Idempotency-Key`; respect `Retry-After` on 429.
- Errors (problem+json) map to i18n keys `error.<code>`.
- Functions: `warmUp`, `startDemo(role, captchaToken)`, `createScan`, `uploadToSignedUrl`,
  `analyzeScan`, `listScans`, `getAlerts`, `setAlertPreference`, admin calls, `getAuditReport`.

## 5. Offline outbox (ADR 0009)
IndexedDB item `{id (= Idempotency-Key), jpeg Blob, meta, attempts, createdAt}`; flush when online and
`/healthz` = 200; remove on success; backoff on failure; after 10 attempts mark "stuck" with a manual
retry button. Never sent anywhere except our API.

## 6. Image pipeline
Decode with EXIF orientation → long side ≤ 1024 px → `canvas.toBlob('image/jpeg', 0.8)` (re-encoding
drops EXIF/GPS) → SHA-256 → quality hints (dark: mean luminance < 50; blurry: low Laplacian variance) →
**coarse location rounded to 2 decimals on the device** before storing or sending.

## 7. Not-sure screen
When `status = not_sure`: show "নিশ্চিত নই / Not sure", **no disease named as the answer**, retake
tips (one leaf, daylight, close), "do not spray on a guess", and a static card "contact your local
agriculture office (Upazila Krishi Office)". Top-3 stays collapsed under "other possibilities".

## 8. Alerts screen
List + Leaflet map (OpenStreetMap tiles) of **published** alerts; every alert shows the label
"possible outbreak — unverified, rule-based", risk, area, report count, date. In-app only.

## 9. Rules (checked in review and CI)
- Only `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_API_BASE_URL`,
  `VITE_TURNSTILE_SITE_KEY` exist in the frontend. Everything `VITE_*` is public.
- LLM / KB text is rendered as plain text, never HTML.
- The UI never decides permissions — it only reflects what the API allowed.
- Every screen tested in `bn` and `en` at 360 × 740 (Playwright) and with axe-core.
- Synthetic banner on every screen while demo data is used.

## 10. Build & deploy
Build `npm ci && npm run build` → `dist/`; Render static site with SPA rewrite `/* → /index.html`
and security headers — see [`docs/deployment/01-render-guide.md`](../../docs/deployment/01-render-guide.md).
