# Challenges, obstacles & recovery playbook

Every challenge we expect — deployment on Render free, the free tiers around it, ML, data, AI,
team and demo-day — with **prevention**, **detection** and **recovery**. Owner in brackets.
Platform facts cite [R1] Render free docs and [R2] Supabase pricing (`docs/research/sources.md`).

## A. Render free tier

| # | Challenge | Why it happens | Prevention | Detection | Recovery |
|---|---|---|---|---|---|
| A1 | **Cold start ≈ 1 min** after 15 min idle [R1] | free services spin down | frontend is a static site (never sleeps) and shows "সার্ভার চালু হচ্ছে…"; pre-warm on app open (`GET /healthz`); n8n keep-warm ping every 10 min **during demo/judging windows** | n8n monitor measures first-byte time | user's photo waits in the offline outbox and auto-sends when `/healthz` = 200; client timeout 90 s with retry + jitter [Apon, Sara] |
| A2 | **750 instance-hours / month** per workspace [R1] | each awake service consumes hours | only **one** API service; static site uses no instance hours; keep-warm only in windows; staging in a separate workspace or on demand | Render dashboard usage; weekly check in stand-up | if hours run out all free services suspend until month reset → upgrade the API to the cheapest paid instance for that month, or redeploy from another workspace (blueprint makes it a 10-minute job) [Apon] |
| A3 | **Ephemeral filesystem**, no persistent disks [R1] | container is replaced on deploy/restart/spin-down | uploads go straight to Supabase Storage via signed URL; model baked into image or re-downloaded at boot; no SQLite, no local cache that matters | `test_stateless.py` (restart between upload and analyze) | nothing to recover by design; if a feature wrote locally → treat as bug [Apon] |
| A4 | **Single instance** only [R1] | free plan | async FastAPI; CPU inference in thread pool with semaphore; LLM calls async; cached advice | p95 latency monitor; k6 load test | queue requests (429 + `Retry-After` beyond capacity); demo with ≤ 20 concurrent users [Apon] |
| A5 | **Memory limits** (exact free RAM not published on the free page [R1]) | PyTorch / big models / many workers | no torch at runtime; ONNX int8; 1 worker; Pillow `MAX_IMAGE_PIXELS`; stream image bytes | OOM kills in logs; `/readyz` memory field | shrink model (MobileNetV3), FP16→int8, reduce threads; last resort: paid instance [Apon, Taeen] |
| A6 | **Render may restart** the service any time [R1] | platform maintenance | stateless API; idempotent writes (`Idempotency-Key`, unique `(user_id, sha256)`); health checks | restart events in logs | client retries are safe; no partial writes (transactions) [Apon] |
| A7 | **No cron / one-off jobs / shell** on free [R1] | plan limits | scheduled jobs run in n8n calling HMAC-protected endpoints | n8n execution log | run job manually by calling the endpoint from n8n "Execute" [Apon, Taeen] |
| A8 | Build failures / slow builds; build minutes count | heavy dependencies | slim image; pinned `requirements.txt`; multi-stage Docker; layer caching | Render build logs | rollback to previous deploy (one click) [Apon] |
| A9 | `$PORT` binding / health check misconfiguration | uvicorn on fixed port | `--port $PORT`; `/healthz` without DB dependency | deploy stuck "in progress" | fix CMD, redeploy [Apon] |
| A10 | Outbound SMTP ports 25/465/587 blocked [R1] | platform rule | send email through n8n / provider HTTP API, not SMTP from the API | failed sends | switch channel (Telegram/SMS HTTP API) [Apon] |
| A11 | Free Render Postgres **expires after 30 days** [R1] | plan rule | **not used** — Supabase instead (ADR 0003) | — | — |
| A12 | SPA deep links 404 on refresh | static hosting | rewrite `/* → /index.html` | E2E test opens `/audit` directly | add rewrite rule [Sara] |
| A13 | CORS errors between web and API | origin mismatch | explicit allow-list from env; preflight tested | browser console, E2E | fix `APP_BASE_URL` env and redeploy [Apon] |

## B. Supabase free tier
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| B1 | **Project paused after 1 week of inactivity** [R2] | n8n daily heartbeat query (`select 1`) via API `/readyz` | restore from Supabase dashboard (minutes); keep the restore step in the demo-day checklist |
| B2 | **500 MB database limit** [R2] | images never in DB; vectors 384-d; audit/log retention | prune logs; move thumbnails; if read-only mode → delete old synthetic rows |
| B3 | Connection limits | pooled connection string; pool size 5 | lower pool; retry with backoff |
| B4 | Storage growth | client compression; 90-day thumbnail policy | run retention job early |
| B5 | Key leakage (service-role key) | server-only; CI grep gate | rotate keys in Supabase, update Render env group, redeploy |

## C. ML & data
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| C1 | Small datasets (≈ 4 k images) | transfer learning; augmentations; CV | add our pilot photos; semi-supervised pseudo-labels reviewed by agronomist |
| C2 | Class confound by source dataset | confound probe; Grad-CAM review | background augmentation; collect classes in both sources |
| C3 | Lab → field domain shift | train on field data first | report honestly; abstention covers the gap |
| C4 | Over-confident wrong predictions | temperature scaling + τ + OOD guard | raise τ from `/admin` instantly |
| C5 | Quantisation hurts accuracy | parity gate | ship FP32 ONNX |
| C6 | Free GPU session limits (Colab/Kaggle timeouts) | checkpoint every epoch to Drive/Kaggle output; small models first | resume from checkpoint; split runs across team accounts |
| C7 | Dataset licence uncertainty (PlantVillage) | use only CC BY sets until confirmed | drop D4; no impact on main model |
| C8 | Data leakage between splits | pHash dedup; group split | rebuild split, re-run, report |

## D. AI integration (LLM / RAG)
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| D1 | LLM latency / timeouts | 20 s budget; cached advice per (disease, stage, KB version) | serve cached or static agronomist card |
| D2 | LLM rate limit / outage / quota | budget cap; provider-swappable adapter | switch `LLM_PROVIDER`; static cards |
| D3 | Hallucinated dose / product | RAG only; validator; banned list | block + escalate; fix KB |
| D4 | Poor Bangla output | Bangla source docs; style guide; native rater review | prompt revision; few-shot examples |
| D5 | Scarce Bangla KB documents | start collection day 1 (critical path) | translate English guides with human review, labelled as translated |
| D6 | Prompt injection | data-wrapping; red-team suite | patch prompt; add test case |

## E. Frontend / UX
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| E1 | Slow networks | compressed uploads; lazy routes; cached assets | offline outbox |
| E2 | Bangla font rendering / layout overflow | Noto Sans Bengali subset; both-locale screenshots in CI | fix CSS, add test |
| E3 | Camera permissions vary by browser | file-input fallback (`accept="image/*" capture`) | instruct user |
| E4 | iOS PWA limitations (background sync) | "send now" button | manual sync |

## F. Team & schedule
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| F1 | Scope creep | one core use case (rice, photo→advice); stretch list explicit | cut stretch items first (voice, detector) |
| F2 | Integration crunch at the end | vertical slice by 21 Oct; daily integration | freeze 28 Oct; only fixes after |
| F3 | Member unavailable (exams, illness) | pairing: Apon↔Taeen, Salwa↔Raisa, Sara↔Raisa | re-assign by RACI backup column |
| F4 | Merge conflicts | small PRs; CODEOWNERS | rebase daily |
| F5 | Missed deadline (31 Oct 12:00 BST) | internal deadline 29 Oct; 30–31 buffer | submit what works + honest roadmap |

## G. Demo day / judging
| # | Challenge | Prevention | Recovery |
|---|---|---|---|
| G1 | Venue internet fails | **recorded demo video**; phone hotspot | play video, walk through prototype offline (static files) |
| G2 | API asleep at pitch time | keep-warm 30 min before slot; open `/healthz` | outbox demo shows graceful wake |
| G3 | Supabase paused | heartbeat; checklist restores | restore (minutes) |
| G4 | LLM quota exhausted | budget alert; cached advice for demo diseases | cached cards |
| G5 | Judge enters unexpected photo | abstention handles it — a feature, not a failure | explain "not sure → agronomist" |
