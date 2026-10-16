# Free-tier challenges, obstacles & recovery playbook

Every way the free platforms can slow us down **or turn us off**, with cause → prevention → detection →
recovery → owner. Platform facts cite `docs/research/sources.md` ([R1] Render free, [R2] Supabase
pricing, [R3] Render Docker, [R4] Blueprint, [R7] Supabase connections, [R9] Render custom domains).
Section **H** is the runbook for "Render has switched our service off".

## A. Render free tier

| # | Challenge | Why it happens | Prevention | Detection | Recovery | Owner |
|---|---|---|---|---|---|---|
| A1 | **Cold start ≈ 1 min** after 15 min idle [R1] | free web services spin down | frontends are static sites (never sleep); app pre-warms with `GET /healthz` on open and shows "সার্ভার চালু হচ্ছে…"; keep-warm pings only during demo windows | UptimeRobot response time; n8n 05 first-byte time | photo waits in the offline outbox and sends when `/healthz` = 200; client timeout 90 s with retry + jitter | Apon, Sara |
| A2 | **750 instance-hours / month**; when used up **all free web services are suspended** until next month [R1] | each awake web service consumes hours | exactly one free web service (the API); keep-warm only in windows; staging API in a second workspace or run locally | Render dashboard usage + usage-alert emails; weekly check at stand-up | upgrade **only the API's** instance type for the rest of the month (upgrading the workspace does not lift free limits [R1]) or recreate it in a new workspace (§H) | Apon |
| A3 | **Bandwidth over the included amount** → with no payment method **all free services suspended** for the rest of the month [R1] | large images/assets, bots, heavy monitoring | client compresses photos to ≈ 150–300 KB; images go browser → Supabase directly (not through Render); cache static assets; CAPTCHA + rate limits stop bots | Render metrics (bandwidth); usage-alert emails | §H runbook; add a payment method to unlock if the team agrees | Apon |
| A4 | **Build pipeline minutes over** → **new builds disabled** for the rest of the month; running services keep their last build [R1] | many redeploys, slow Docker builds | batch merges to `main`; slim image; build only on `main`; no PR previews | Render usage page; failed deploy with "builds disabled" | keep running the last good build; use **Rollback** (no rebuild); fix-forward next month or in a new workspace | Apon |
| A5 | **Suspension for unusually high outbound traffic** (calls to external databases, APIs, object storage) [R1] | our API calls Supabase, the LLM and Open-Meteo | cache advice and weather; DB pool of 5; no load tests against production (staging only, short runs); monitors at 5–10 min, not seconds | service shows "suspended"; email from Render | moving the service to a paid instance type restores it [R1]; or §H | Apon |
| A6 | **Random restarts** — Render may restart a free service any time [R1] | platform maintenance | stateless API; idempotent writes (`Idempotency-Key`, unique `(user_id, sha256)`); one transaction per analysis; model re-downloaded and hash-checked at boot | restart events in logs | client retries are safe; nothing partial is stored | Apon |
| A7 | **Ephemeral filesystem**, no persistent disks [R1] | container replaced on deploy/restart/spin-down | uploads go straight to private Supabase Storage; nothing written locally that matters | integration test IT3 (restart between upload and analyze) | none needed by design; anything written locally is a bug | Apon |
| A8 | **Single instance** only [R1] | free plan | async FastAPI; inference in thread pool with semaphore 2; cached advice | p95 latency monitor | 429 + `Retry-After` when the queue is full | Apon |
| A9 | Memory limits (free RAM not published on the free page) | PyTorch, big models, many workers | no PyTorch at runtime; ONNX int8; 1 worker; pixel cap | OOM kills in logs; Render memory metric | smaller model (MobileNetV3), fewer threads; paid instance as last resort | Apon, Taeen |
| A10 | Outbound SMTP ports 25/465/587 blocked [R1] | platform rule | email only via Supabase Auth or provider HTTP APIs | failed sends | switch to an HTTP email API | Apon |
| A11 | Secrets leaking through Docker build args [R3] | Render passes env vars as build args | Dockerfile reads no ARGs and no secrets; model fetched at runtime | image history review | rotate the leaked key; rebuild | Apon |
| A12 | Blueprint rejected [R4] | `sync: false` inside an env group; `plan` on a static site; `render.yaml` not at the repo root | follow the Render guide §8 rules | Blueprint sync error | fix the file and resync | Apon |
| A13 | Free Render Postgres expires after 30 days, deleted after a 14-day grace [R1] | plan rule | **not used** — Supabase instead (ADR 0003) | — | — | — |
| A14 | SPA deep links 404 on refresh | static hosting | rewrite `/*` → `/index.html`; prototype route rewrites | E2E E6 | add the rewrite rule | Sara |
| A15 | CORS errors | origin mismatch after a URL change | `APP_BASE_URL` = exact web URL; URL plan updated everywhere | browser console, E2E | fix the env var, redeploy | Apon |
| A16 | `$PORT` / health-check misconfiguration | fixed port in the start command; health check touching the DB | bind `$PORT`; `/healthz` without DB | deploy stuck "in progress" | fix CMD / health path, redeploy | Apon |
| A17 | **Dependence on the `onrender.com` subdomain** | all shared links point at Render | custom domain early ([Render §10](01-render-guide.md)); share only custom-domain links | — | re-point DNS to a backup host (§H) | Apon |

## B. Supabase free tier
| # | Challenge | Prevention | Detection | Recovery | Owner |
|---|---|---|---|---|---|
| B1 | **Project paused after 1 week of inactivity** [R2] | daily heartbeat (n8n 04 + GitHub Actions) | `/readyz` db down; dashboard banner | **Restore project** in the dashboard, then restart the API | Apon |
| B2 | 500 MB database limit [R2] | images never in DB; 384-d vectors; log retention | dashboard usage | prune synthetic rows/logs, VACUUM; second free project for staging | Apon |
| B3 | Connection limits / IPv6 direct host [R7] | pooler string; pool size 5; `statement_cache_size=0` in transaction mode | connection errors in API logs | switch to session pooler; lower pool | Apon |
| B4 | Storage growth (1 GB free storage) | client compression; 90-day thumbnail policy | Storage usage | run retention workflow 07 early | Apon |
| B5 | Secret key leaked [R5] | server-only; CI grep; push protection | GitHub secret scanning alert | create a new secret key, update Render, delete the old one | Apon |
| B6 | Legacy keys deprecated by end of 2026 [R5] | use publishable/secret keys from day one | — | — | Apon |
| B7 | Built-in email rate limits | custom SMTP before real users | users report no OTP | configure custom SMTP | Apon |
| B8 | No automatic backups on free (verify) | weekly `pg_dump` | restore drill | restore from the latest dump into a new project | Apon |

## C. ML & data
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| C1 | Small datasets (≈ 4 k images) | transfer learning; augmentation; CV | add more public field datasets; stronger augmentation |
| C2 | Class confound by source dataset | confound probe; Grad-CAM check | background augmentation; report as limitation |
| C3 | Lab → field domain shift | train on field data first | report honestly; abstention covers the gap |
| C4 | Over-confident wrong predictions | temperature scaling + τ + OOD guard | raise τ from `/admin` instantly (audited) |
| C5 | Quantisation hurts accuracy | parity gate | ship FP32 ONNX |
| C6 | Free GPU session limits (Colab/Kaggle) | checkpoint every epoch; small models first | resume from checkpoint; split runs across accounts |
| C7 | Dataset licence uncertainty (PlantVillage) | use CC BY sets only until confirmed | drop D4 |
| C8 | Data leakage between splits | pHash dedup; group split | rebuild split, re-run, report |

## D. AI integration (LLM / RAG)
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| D1 | LLM latency / timeouts | 20 s budget; cached advice | serve cached or static card |
| D2 | LLM rate limit / outage / quota / spend cap reached | spend cap with alert; cache; swappable provider | switch `LLM_PROVIDER`; static cards |
| D3 | Hallucinated dose / product | RAG only; validator; banned list | block; fix KB |
| D4 | Poor Bangla output | Bangla source docs; style guide; native speakers rate output | prompt revision; few-shot examples |
| D5 | Scarce Bangla KB documents | start collection day 1 (critical path) | translate English guides, clearly labelled as translated |
| D6 | Prompt injection | data-wrapping; read-only tools; red-team | patch prompt; add test case |

## E. Other free services
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| E1 | n8n Cloud trial ends | plan the trial window to cover judging; export workflows as JSON | self-host n8n; GitHub Actions + UptimeRobot fallbacks |
| E2 | GitHub Actions cron runs late or is disabled after long repo inactivity | heartbeat is a fallback, not the keep-warm; keep committing | UptimeRobot / n8n for timing-critical pings |
| E3 | UptimeRobot / cron-job.org free intervals too slow to keep warm | 5–10 min interval is enough (spin-down after 15 min) | n8n keep-warm |
| E4 | Turnstile blocks real users | Managed mode; correct hostnames | temporarily disable CAPTCHA on demo route (rate limit stays) |
| E5 | Open-Meteo unavailable | 3 s timeout; cache 1 h | risk not raised; alerts still work from counts |

## F. Frontend / UX
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| F1 | Slow networks | compressed uploads; lazy routes; cached assets | offline outbox |
| F2 | Bangla font rendering / layout overflow | Noto Sans Bengali / Hind Siliguri; both-locale tests | fix CSS, add test |
| F3 | Camera permission differs per browser | file-input fallback | instruct user |
| F4 | iOS PWA limits (no background sync) | "send now" button | manual sync |

## G. Team, schedule, demo day
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| G1 | Scope creep | one core use case; explicit cut list | cut voice → map tiles → Grad-CAM gallery → extra model runs |
| G2 | Integration crunch | vertical slice by 21 Oct | freeze 28 Oct; only fixes after |
| G3 | Member unavailable | pairing Apon↔Taeen, Salwa↔Raisa, Sara↔Raisa | RACI backup column |
| G4 | Missed deadline (31 Oct 12:00 BST) | internal deadline 29 Oct | submit what works + honest roadmap |
| G5 | Venue internet fails | recorded demo video; phone hotspot | play video; prototype opens from local files |
| G6 | API asleep at pitch time | keep-warm 30 min before the slot | outbox demo shows a graceful wake |
| G7 | Judge uploads an unexpected photo | abstention handles it | show "not sure" as a safety feature |

## H. Runbook — "Render has turned our service off"
Use when a Render service shows **Suspended**, a URL returns an error page for more than a few minutes,
or Render emails a suspension / limit notice.

1. **Identify the cause (5 min)** — Render dashboard → service → Events + workspace **Usage**:
   instance hours (A2), bandwidth (A3), build minutes (A4), outbound traffic (A5), or an outage
   (check status.render.com).
2. **Keep the story alive immediately** — share the **prototype** (static; usually unaffected) and the
   recorded demo video; post a status note in the team channel.
3. **Restore on Render if allowed** —
   - build minutes exhausted → **Rollback** to the last good deploy (no build needed);
   - instance hours / outbound traffic → upgrade **only the API service's** instance type for the
     month (team decision; costs money), or wait for the monthly reset;
   - bandwidth → add a payment method to lift the suspension (team decision), or move hosting (step 4).
4. **Move to backup hosting (≈ 30–60 min)** — prepared in advance:
   - **Static sites (prototype, web app)**: publish the same files to **GitHub Pages** or **Cloudflare
     Pages** (both host static files from the repo; SPA rewrite: Cloudflare Pages `_redirects`, GitHub
     Pages `404.html` copy). Build the web app locally (`npm run build`) if Render builds are disabled.
   - **API**: recreate it from the Render Blueprint **in a second Render workspace** (fresh free
     allowance), or on another container host the team has evaluated beforehand. Same Docker image,
     same environment variables (from the password manager), same Supabase — **all state is in
     Supabase, so no data migration is needed**.
   - Verify the limits of any backup host yourselves before relying on it; record them in
     `docs/research/sources.md`.
5. **Re-point traffic** — with a custom domain: change the CNAME to the backup host (links stay the
   same). Without one: update the URL plan (CORS `APP_BASE_URL`, `VITE_API_BASE_URL` + rebuild, Supabase
   redirect URLs, Turnstile hostnames, CSP, monitors) and share the new links.
6. **Verify** — smoke test (n8n 05 or manual), E2E E1–E3 on the new URLs, `/readyz` 200, from a phone.
7. **Write it down** — incident register in [`audit-readiness.md`](../security/audit-readiness.md): what
   happened, impact, cause, fix, what changes to prevent it.

**Prepare before 28 Oct:** custom domain live · Blueprint file working · a GitHub Pages / Cloudflare
Pages copy of the prototype tested once · all env values in the team password manager · recorded demo
video saved in three places.
