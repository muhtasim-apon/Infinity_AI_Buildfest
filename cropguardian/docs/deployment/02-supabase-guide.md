# Supabase guide — database, vector search, storage, auth, security

Owner: **Apon** (Taeen backup). Order of work: [`00-zero-to-deploy.md`](00-zero-to-deploy.md) Phase 3.
Schema to implement: [`db/SCHEMA-SPEC.md`](../../db/SCHEMA-SPEC.md). Facts: `docs/research/sources.md`
[R2] pricing, [R5] keys, [R6] JWT signing keys, [R7] connections, [R8] phone login, [R10] CAPTCHA.

## 1. Free-plan facts that shape the setup
| Fact | What we do |
|---|---|
| Free projects **pause after 1 week of inactivity** [R2] | daily heartbeat (n8n workflow 04 + GitHub Actions fallback); restore steps in §9 |
| 500 MB database per project; 2 active free projects [R2] | images in Storage, never in the DB; second free project = staging |
| Direct DB host is **IPv6**; the shared **pooler is IPv4**; session port 5432, transaction port 6543 [R7] | Render uses the **pooler** string; transaction mode → asyncpg `statement_cache_size=0` |
| Legacy `anon` / `service_role` keys deprecated by end of 2026 → **publishable** (`sb_publishable_…`) and **secret** (`sb_secret_…`) keys [R5] | frontend = publishable key; API = secret key |
| User tokens verified with **JWKS** (asymmetric ES256/RS256), not a shared secret [R6] | API verifies against `…/auth/v1/.well-known/jwks.json` |
| Phone OTP needs a paid SMS provider [R8] | email OTP / magic link only |
| CAPTCHA: hCaptcha or **Cloudflare Turnstile** on sign-in, sign-up, password reset [R10] | Turnstile |
| No automatic backups on the free plan (verify on the pricing page) | manual weekly `pg_dump` (§8) |

## 2. Create the project
1. supabase.com → **New project** → organisation → name `cropguardian` → generate a strong database
   password (store it in a password manager — it is shown once).
2. **Region**: the closest to Bangladesh offered (South Asia/Mumbai or Southeast Asia/Singapore). Record
   it in [`data-sovereignty.md`](../data/data-sovereignty.md).
3. Optional: a second free project `cropguardian-staging` for tests and load runs.

## 3. Keys and connection strings (Project Settings)
| Item | Where | Goes to |
|---|---|---|
| Project URL | Settings → API Keys / **Connect** dialog | `SUPABASE_URL`, `VITE_SUPABASE_URL` |
| Publishable key `sb_publishable_…` | Settings → **API Keys** | `VITE_SUPABASE_PUBLISHABLE_KEY` (browser) |
| Secret key `sb_secret_…` | Settings → **API Keys** (create one per environment) | `SUPABASE_SECRET_KEY` (**API only**) |
| JWKS URL | `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json` | `SUPABASE_JWKS_URL` |
| Pooler connection string | **Connect** button → transaction or session pooler; replace `[YOUR-PASSWORD]` (percent-encode special characters) | `DATABASE_URL` |

Rules: the secret key **bypasses RLS** — it never appears in the frontend, the repository, logs or n8n.
If it leaks: create a new secret key, update Render, delete the old key.

## 4. Apply the schema
1. Write `db/migrations/0001_init.sql` (extensions `pgcrypto`, `vector`; enums; tables; indexes;
   `audit_append`) and `0002_rls.sql` from the spec.
2. Dashboard → **SQL Editor** → paste and run `0001`, then `0002`, then the synthetic seed.
   (Or with psql: `psql "<pooler session string>" -f db/migrations/0001_init.sql`.)
3. **Database → Extensions**: confirm `vector` is enabled.
4. Never edit an applied migration — add `0003_…`.

## 5. Row-Level Security (checklist: Row level security)
1. Every table: **RLS enabled** (Table editor shows "RLS enabled"). Policies exactly as the spec table.
2. Avoid the two pitfalls: a policy on `profiles` must not select from `profiles` (infinite recursion);
   role checks use the SECURITY DEFINER helper `app_role()`.
3. **Advisors → Security Advisor**: must show no errors (it flags tables without RLS, exposed
   functions, etc.). Also check **Performance Advisor**.
4. Test with the publishable key as two different users ([security-testing-guide §3](../testing/security-testing-guide.md)).

## 6. Storage (checklist: Private storage buckets)
1. **Storage → New bucket** `scans` — **Public: off**; file size limit 5 MB; allowed MIME types
   `image/jpeg, image/png, image/webp`.
2. Bucket `models` — **Public: off**; no browser access at all.
3. Uploads use **signed upload URLs** created by the API (5-minute expiry); downloads use short-lived
   signed URLs for the owner only. No storage policy grants public read.
4. Test: open an object URL without a token → must be denied.

## 7. Authentication
1. **Authentication → Sign In / Providers**: Email enabled; "Confirm email" on; phone disabled.
2. **URL Configuration**: Site URL = web app URL (U2); Redirect URLs = U2 and `http://localhost:5173/**`
   (and the custom domain later). Wrong values = magic links that land on the wrong site.
3. **Bot and Abuse Protection** → Enable CAPTCHA → provider **Cloudflare Turnstile** → paste the
   Turnstile **secret** key → save. The frontend passes the Turnstile token with sign-in/sign-up.
4. **Rate limits** (Authentication settings): keep the defaults strict for OTP/email sends.
5. Email delivery: the built-in email service is meant for testing and is heavily rate-limited (verify
   current limits in the dashboard). For real users, configure **custom SMTP** (Authentication → Emails →
   SMTP) with a transactional email provider.
6. Token lifetime: keep access tokens short (default 1 hour) with refresh-token rotation on.
7. **Demo users**: Authentication → Users → **Add user** → `demo-user@…` and `demo-admin@…` with
   strong random passwords, auto-confirm → copy their user ids into the synthetic seed (role `demo` /
   `admin`). The one-click demo endpoint issues sessions for these accounts server-side.

## 8. Backups & data export
- Weekly (Sunday) manual dump from a team laptop:
  `pg_dump "<pooler session string>" --no-owner --format=custom -f cropguardian-YYYYMMDD.dump`
  → store encrypted in team Drive. Restore drill once before 28 Oct.
- Storage: models are reproducible from the training notebooks; scans are user data — excluded from
  backups by design (retention 90 days).

## 9. Pause & restore (free plan)
Symptoms: API `/readyz` reports `db: down`; dashboard shows "Project paused". Fix: dashboard → project →
**Restore project**, wait until healthy, then restart the Render API. Prevention: n8n workflow 04 and the
GitHub heartbeat run daily; check the dashboard on the morning of every demo.

## 10. Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| API cannot connect, "network unreachable" | direct IPv6 host used from Render | use the **pooler** string from the Connect dialog |
| "prepared statement … already exists" | transaction pooler (6543) + asyncpg cache | `statement_cache_size=0`, or use the session pooler (5432) |
| "infinite recursion detected in policy" | policy on `profiles` selects `profiles` | use `app_role()` SECURITY DEFINER helper |
| 401 on every API call | wrong JWKS URL / project ref | check `SUPABASE_JWKS_URL`; tokens from another project are rejected |
| Magic link opens localhost in production | Site URL / Redirect URLs wrong | fix URL Configuration (§7.2) |
| Users get no OTP email | built-in email rate limit | custom SMTP (§7.5) |
| Database read-only | 500 MB limit reached | delete old synthetic rows, prune logs, VACUUM; move data out |
| Security Advisor warnings | table without RLS / exposed function | enable RLS + policies; revoke execute from `anon` where not needed |
