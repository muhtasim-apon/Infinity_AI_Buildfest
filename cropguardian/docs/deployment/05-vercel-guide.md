# Vercel guide — the 2 frontends, exact settings

Owner: **Apon** (prototype), **Sara** (web app). Used by [00](00-zero-to-deploy.md) Steps 3 and 6.
Free **Hobby** plan. The API is **not** on Vercel — it stays on Render ([01](01-render-guide.md)).

**Repository layout:** the project is inside a `cropguardian/` folder of `Infinity_AI_Buildfest`, so
every Root Directory starts with `cropguardian/`.

**Config is in the repo, not the dashboard:** routes and security headers live in
[`prototype/vercel.json`](../../prototype/vercel.json) and [`apps/web/vercel.json`](../../apps/web/vercel.json).
Vercel reads them on every deploy — nothing to type in the dashboard.

## 1. Prototype
vercel.com → sign in with GitHub → **Add New… → Project** → `Infinity_AI_Buildfest` → **Import**:

| Field | Value |
|---|---|
| Project Name | `cropguardian-prototype` |
| Framework Preset | **Other** |
| Root Directory | `cropguardian/prototype` (click **Edit**) |
| Build Command | override → leave empty |
| Output Directory | override → `.` |
| Install Command | override → leave empty |

**Deploy.** `cleanUrls` in `vercel.json` makes `/app` serve `app.html` (and the other 9 routes); links to
`*.html` redirect to the short URL. **Check:** `/`, `/app`, `/demo-user`, `/demo-admin`, `/admin`, `/data`,
`/security`, `/architecture`, `/presentation`, `/pitchdeck`, `/audit` open on a phone.

## 2. Web app (once `apps/web` has the Vite code)
**Add New → Project** → same repository:

| Field | Value |
|---|---|
| Project Name | `cropguardian-web` |
| Framework Preset | **Vite** |
| Root Directory | `cropguardian/apps/web` |
| Build / Output | defaults (`npm run build` / `dist`) |

**Environment Variables** (Production) — all **public**, they end up in the browser, so never a secret:

| Key | Value |
|---|---|
| `VITE_API_BASE_URL` | `https://cropgurdian-backend.onrender.com` |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | `sb_publishable_…` |
| `VITE_TURNSTILE_SITE_KEY` | Turnstile site key |

They are baked in at build time: after changing one, **Deployments → ⋯ → Redeploy**.
`vercel.json` already rewrites every path to `/index.html` (page refresh works) and sets the CSP.
If the API URL ever changes, update it in `VITE_API_BASE_URL` **and** in the CSP `connect-src` of
`apps/web/vercel.json`.

## 3. Connect the URLs (one time, after §2)
| Copy | Into |
|---|---|
| web URL (`https://cropguardian-web.vercel.app`) | Render API env `APP_BASE_URL` (CORS) → redeploy the API |
| web URL | Supabase → Authentication → URL Configuration → Site URL + Redirect URLs |
| web + prototype hostnames | Cloudflare Turnstile widget → Hostnames |
| web + prototype URLs | UptimeRobot monitors (uptime alerts only — Vercel doesn't sleep) |

## 4. Good to know
- **Hobby is for personal, non-commercial use** — fine for the hackathon; check Vercel's terms before
  any commercial launch.
- Every push to `main` deploys to production; other branches get a **preview URL**. Login and API calls
  fail on previews (their URL isn't in CORS or Supabase redirects) — expected, test on production.
- **Rollback:** project → **Deployments** → last good one → ⋯ → **Promote to Production** (no rebuild).
- Copy the exact URL Vercel shows (it may add a suffix if the name is taken) into the [00](00-zero-to-deploy.md) URL table.

## 5. Done checklist
- [ ] Prototype: all 11 routes open on a phone, on mobile data.
- [ ] Web: loads; refreshing `/audit` works; CAPTCHA shows on `/demo-user`; no CORS errors in the console.
- [ ] `curl.exe -I <url>` shows HSTS, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`
      (+ CSP on the web app); grade checked on securityheaders.com.
- [ ] Only `VITE_*` variables in Vercel — no secret in the dashboard, the bundle or build logs.
