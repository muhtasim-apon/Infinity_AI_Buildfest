# .github — CI/CD and repository automation specification

**Status: specification only — create the workflow files from this when code exists.** Owner: Apon.
Kept here now: `CODEOWNERS`, PR template, issue template.

## 1. `workflows/quality-gates.yml` (on every PR and push to `main`)
| Job | Steps | Blocking? |
|---|---|---|
| web | `npm ci` → lint → typecheck → unit tests → `npm audit --audit-level=high` | after code freeze (M4) |
| bangla-completeness | every key in `en.json` must exist in `bn.json` | always |
| api | ruff → mypy → pytest unit + whitebox with branch coverage ≥ 80 % → Bandit → pip-audit | after M4 |
| contract | Schemathesis against the test API | after M4 |
| security | gitleaks secret scan; fail if `SERVICE_ROLE`, `SECRET_KEY` or `sb_secret_` appears in web source | always |
| ml | every referenced model has a card; RAG regression (citation coverage 1.00, banned leakage 0) | after M4 |
| docs | link check | always |

Before the code exists, jobs that cannot pass are marked "continue on error"; remove that at M4 (28 Oct).

## 2. `workflows/claude-security-review.yml` (checklist: Claude security review)
Uses the `anthropics/claude-code-security-review` GitHub Action on pull requests; it reviews only
changed files and comments findings on the PR. Needs repository secret `CLAUDE_API_KEY` (key enabled
for the Claude API and Claude Code). Permissions: `pull-requests: write`, `contents: read`. The action is
**not hardened against prompt injection** → run it only on trusted PRs and enable *"Require approval
for all external contributors"* in Settings → Actions. Locally, run `/security-review` in Claude Code
before opening a PR.

## 3. `workflows/heartbeat.yml` — after 31 Oct only (until then the UptimeRobot monitor on `/readyz` does this)
Daily cron (03:00 Asia/Dhaka) + manual run: `GET <API>/healthz` (120 s timeout, wakes the service),
then signed `POST <API>/v1/hooks/n8n/heartbeat` (HMAC over `timestamp.body`). Secrets: `API_BASE_URL`,
`N8N_WEBHOOK_SECRET`. Purpose: keep the free Supabase project from pausing. GitHub's scheduler is
best-effort (can run late) → not a keep-warm.

## 4. `dependabot.yml` (checklist: Update vulnerable packages)
Weekly updates for `npm` (`/apps/web`), `pip` (`/services/api`), `docker` (`/services/api`),
`github-actions` (`/`). Also enable **Dependabot alerts** and **secret scanning** in repository
Settings → Code security.

## 5. Branch protection (Settings → Branches → `main`)
Require PR, 1 approval from CODEOWNERS, status checks `bangla-completeness`, `security`, `docs`
(add the rest at M4), no force-push, no deletion.
