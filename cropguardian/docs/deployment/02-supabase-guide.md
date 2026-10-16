# Supabase guide — database, photo storage, login

Owner: **Apon** (Taeen backup). Used by [00](00-zero-to-deploy.md) Step 4. Free project. What to build:
[`db/SCHEMA-SPEC.md`](../../db/SCHEMA-SPEC.md). Facts: [R2], [R5]–[R8], [R10] in [`sources.md`](../research/sources.md).

## Steps
**1. Create the project.** supabase.com → New project → name `cropguardian` → region **Singapore** (or
the closest to Bangladesh offered) → generate a strong database password and save it in the team
password manager.

**2. Copy 5 values** into the password manager:

| Value | Where in the dashboard | Goes to |
|---|---|---|
| Project URL | **Connect** button | API `SUPABASE_URL`, web `VITE_SUPABASE_URL` |
| Publishable key `sb_publishable_…` | Settings → **API Keys** | web `VITE_SUPABASE_PUBLISHABLE_KEY` |
| Secret key `sb_secret_…` | Settings → **API Keys** | API `SUPABASE_SECRET_KEY` only |
| JWKS URL | `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json` | API `SUPABASE_JWKS_URL` |
| **Pooler** connection string | **Connect** → *Transaction pooler* | API `DATABASE_URL` |

Use the **pooler** string, not the direct one: the direct host is IPv6-only [R7]. With the transaction
pooler the API must create its database pool with `statement_cache_size=0`. The secret key bypasses all
security rules — it only ever goes into Render.

**3. Create the schema.** Write `0001_init.sql`, `0002_rls.sql` and the seed from the spec → **SQL Editor**
→ run them in that order → **Advisors → Security Advisor** must show **no errors** (every table has
row-level security).

**4. Storage.** Storage → New bucket `scans` (**not public**, 5 MB limit, types `image/jpeg, image/png,
image/webp`) and `models` (**not public**).

**5. Login.**
- Authentication → Sign In / Providers: **Email** on, "Confirm email" on, phone off (phone needs a paid
  SMS provider [R8]).
- URL Configuration: Site URL = web app URL; Redirect URLs = web app URL and `http://localhost:5173/**`.
- Bot and Abuse Protection → **Enable CAPTCHA** → Cloudflare Turnstile → paste the Turnstile secret key [R10].

**6. Demo users.** Authentication → Users → Add user → `demo-user@…` and `demo-admin@…`, strong random
passwords, auto-confirm → put their ids into the seed (roles `demo` and `admin`) → run the seed again.

## Keep it running
- Free projects **pause after a week without activity** [R2]. The UptimeRobot monitor on `/readyz`
  queries the database every few minutes, which should count as activity — check the dashboard after the
  first week. If it paused: dashboard → **Restore project**, then restart the API.
- Free limit: 500 MB database [R2] — photos go to Storage, never into tables.
- Backup before demo day: `pg_dump "<pooler session string>" --format=custom -f cropguardian.dump` from a
  team laptop; keep it in team Drive.

## Problems
| Symptom | Fix |
|---|---|
| API cannot connect / "network unreachable" | you used the direct string — use the pooler string |
| "prepared statement already exists" | set `statement_cache_size=0` (transaction pooler) |
| "infinite recursion detected in policy" | role checks must use the `app_role()` helper ([spec §4](../../db/SCHEMA-SPEC.md)) |
| Every API call 401 | wrong `SUPABASE_JWKS_URL` / project |
| Login email opens localhost | fix Site URL / Redirect URLs (step 5) |
| No login email arrives | built-in email is rate-limited — wait, or add custom SMTP later |
