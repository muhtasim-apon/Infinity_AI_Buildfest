# Manual checklist: are Phase 0, 1 and 2 OK?

**A** = a command I (or CI) can run and that prints a verdict. **M** = you check it by hand.
Tick a box only when the result matches the "expected" text. Anything that does not match is a bug:
write down the page, what you did and what you saw, and send it over.

Where to look (see the README, "See it running"):

| Surface | URL | Notes |
|---|---|---|
| Local, production build | https://localhost | self-signed certificate: **Advanced -> Proceed to localhost**, or install mkcert and re-run `make certs` |
| Local, hot reload | http://localhost:5180 | `make dev` (needs the stack up for `/api`); **not** 5173, another project may own it |
| After changing the frontend | `make web` | nginx serves `frontend/dist` |
| Vercel (stop-gap prototype, synthetic data) | https://infinityaibuildfest-prototype-five.vercel.app | static clickable prototype; replaced by the real app in Phase 2 Block 4 |
| Hosted API | https://cropgurdian-backend.onrender.com | API only; `/` is a 404 by design |

## Phase 0 - Foundations
- [ ] **A** `make gate PHASE=0` ends with `PHASE 0 GATE: PASS` (needs `GITLEAKS_BIN`, `HOSTED_HEALTH_URL`, `make test-db`)
- [ ] **A** `docker compose ps`: api, nginx, postgres, redis, minio are up / healthy
- [ ] **M** https://localhost/health shows `{"status":"ok",...}`
- [ ] **M** https://localhost/health/ready shows `{"db":"ok","redis":"ok"}`
- [ ] **A** `make edge`: every check passes (HTTPS redirect, one CSP header, HSTS, TRACE blocked, 2 MB body gives 413)
- [ ] **M** https://localhost/docs and /openapi.json give 404 (hidden in production mode)
- [ ] **M** https://cropgurdian-backend.onrender.com/health gives 200 and /health/ready gives db + redis ok (the first request after idle can take about a minute)
- [ ] **M** Supabase: `alembic_version` is `0002` (`0003` after you run the 0003 SQL), 17 tables in `public`, forced RLS on 16, advisor lists only `vector` in `public`

## Phase 1 - Identity, sessions, tenancy
- [ ] **A** `make gate PHASE=1` ends with `PHASE 1 GATE: PASS`
- [ ] **M** `/demo`: choose **Farmer**, you land in the farmer area with the purple DEMO ribbon; repeat for **Reviewer** and **Admin**; "Exit demo" signs you out
- [ ] **M** `/register`: name, phone `01712345678`, a strong password, tick the required consent. The consent text must be readable before you can submit. The 6-digit code is in `docker compose logs api` (look for `[sms:console]`). Enter it: you are signed in
- [ ] **M** `/account/sessions` lists this device; "sign out everywhere" works
- [ ] **M** Wrong password 5 times: a lockout message with the time appears; the right password is refused until it expires
- [ ] **M** Forgot password: the message is the same for an unknown and a known phone
- [ ] **M** Signed out, `/admin` shows 404; as a farmer `/review` shows 403; signed out, `/app` (`/home` before the rename) sends you to `/login?return_to=...`
- [ ] **M** Staff: `docker compose exec api python scripts/create_admin.py --email you@example.com --name You`, sign in at `/staff`, enrol the authenticator, sign in with a code
- [ ] **M** Hosted (needs the Render env update and a restart): `/demo` works on the hosted URL and Supabase `users` has the 3 demo rows

## Phase 2 - Design system, shells, landing page
- [ ] **A** `make gate PHASE=2` ends with `PHASE 2 GATE: PASS` (budgets, axe, layout/shells E2E, visual, Lighthouse, stills manifest, no inline scripts/styles, `check_i18n`)
- [ ] **A** `npm --prefix frontend test` is green and `npm --prefix e2e test -- --project=w360 --project=w768 --project=w1366` is green
- [ ] **M** Landing `/` at 390x844 (phone or DevTools) and at 1366x768: hero, phone mock-up, the 3D scene fades in after the poster, all 12 sections, no sideways scrolling
- [ ] **M** Toggle **বাংলা / EN**, **dark mode** and **reduced motion** (DevTools -> Rendering): text, colours and animation change correctly; reduced motion shows the poster / static states
- [ ] **M** DevTools **Offline**: the offline page or banner appears; **Slow 3G**: the page stays usable; disable WebGL or throttle the CPU: poster only, no crash
- [ ] **M** Keyboard: Tab through every page. Skip link, visible focus ring, nothing traps you. Zoom to 200 percent: no clipped Bangla text
- [ ] **M** Farmer shell: bottom tabs with a raised scan button on a phone; a centred 480 px column on a desktop. Staff shell: sidebar, then rail, then drawer as the window narrows; Ctrl+K opens the command palette
- [ ] **M** `/dev/ui-kit` shows every component in both themes and both languages (dev build only; it is a 404 in the production build)
- [ ] **M** Browser console is clean on every page (no red errors) and the Network tab shows no third-party requests

## Vercel (public URL)
- [ ] **A** `curl -sI <url>/`: one CSP header, HSTS, nosniff, X-Frame-Options DENY
- [ ] **M** Open the URL logged out, on a phone over mobile data (not Wi-Fi): the page loads without a Vercel login screen
- [ ] **M** Lighthouse (Incognito, production URL): Performance 90+ desktop / 80+ mobile, Accessibility 95+, Best practices 95+, SEO 90+
- [ ] **M** `/api/health` through the Vercel rewrite returns 200 (real app only, from Phase 2 Block 4)
