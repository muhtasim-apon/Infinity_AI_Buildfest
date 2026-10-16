# Free-tier problems and fixes

Only the problems that can actually hit us before 31 Oct. Facts: [R1] Render free, [R2] Supabase,
[R3] Render Docker, [R7] Supabase connections in [`sources.md`](../research/sources.md). Owner: **Apon**.

## A. Render
| # | Problem | Prevent | Fix |
|---|---|---|---|
| A1 | API sleeps after 15 min, first request takes ~1 min [R1] | UptimeRobot pings `/readyz` (00 Step 8); app shows "waking server" and keeps the photo in its offline outbox | wait for the wake-up; check the monitor is running |
| A2 | 750 free hours per month used up → **all free web services suspended** until next month [R1] | only one free web service (the API); frontends are on Vercel | upgrade only the API's instance type for the month, or recreate the API in a new Render workspace with the same settings |
| A3 | Bandwidth over the free amount → **all free services suspended** for the month [R1] | photos are compressed on the phone and uploaded straight to Supabase, not through Render | add a payment method (team decision) or wait for the reset; show the recorded demo |
| A4 | Build minutes used up → **new builds disabled** for the month; running sites keep working [R1] | merge to `main` in batches, not every small change | keep the last good deploy; **Rollback** needs no build |
| A5 | Suspension for unusually high outbound traffic to external DBs/APIs [R1] | cache advice; small DB pool; **no load tests against production** | move only the API to a paid instance to restore it |
| A6 | Render restarts the service at any time; disk is wiped [R1] | API keeps nothing on disk; model is re-downloaded at start | none needed — check `/readyz` |
| A7 | Secret leaked through Docker build [R3] | Dockerfile reads no secrets | rotate the key, redeploy |
| A9 | CORS error in the browser | `APP_BASE_URL` = exact Vercel web URL | fix the env var, redeploy |

## V. Vercel (prototype + web app)
| # | Problem | Prevent | Fix |
|---|---|---|---|
| V1 | Page refresh shows 404 | `cleanUrls` / SPA rewrite in `vercel.json` ([05](05-vercel-guide.md)) | check Root Directory points at the folder with `vercel.json` |
| V2 | Hobby plan is non-commercial only; usage limits | hackathon use only; photos go straight to Supabase, not through Vercel | after the hackathon: Pro plan, or move the static builds to a Render static site (Root Directory as in 05, rewrites by hand) |
| V3 | Login / API fails on a preview URL | test on the production URL | expected — previews aren't in CORS or Supabase redirects |
| V4 | Web app shows old API URL | `VITE_*` are baked in at build | change the env var → **Redeploy** |

## B. Supabase
| # | Problem | Prevent | Fix |
|---|---|---|---|
| B1 | Project paused after a week without activity [R2] | UptimeRobot on `/readyz` | dashboard → Restore, then restart the API |
| B2 | API cannot connect (IPv6) [R7] | use the pooler string | switch `DATABASE_URL` to the pooler |
| B3 | 500 MB database limit [R2] | photos in Storage only | delete old demo rows |
| B4 | Secret key leaked | only in Render; secret scanning on | create a new secret key, update Render, delete the old one |

## C. Everything else
| # | Problem | Fix |
|---|---|---|
| C1 | LLM slow, down or over budget | the API shows cached or static advice; raise the spend limit if needed |
| C2 | Colab/Kaggle session ends mid-training | resume from the last checkpoint |
| C3 | Venue internet fails on demo day | play the recorded demo video; open the prototype from the laptop |

## If Render switches a service off
1. Render → service → **Events** and the workspace **Usage** page: find which limit (A2–A5).
2. Share the **prototype** URL (on Vercel, unaffected) and the recorded video immediately.
3. Build minutes → **Rollback**. Hours / traffic → upgrade only the API for the month (team decision) or
   recreate it in a new workspace with the same settings — all data is in Supabase, nothing to migrate.
4. Update URLs if they changed (00 Step 6 table), then re-check from a phone.
