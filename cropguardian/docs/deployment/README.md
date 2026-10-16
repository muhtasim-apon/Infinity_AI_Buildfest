# Deployment — the minimum path

**One way to deploy, no alternatives.** Follow [`00-zero-to-deploy.md`](00-zero-to-deploy.md) step by step;
open the other files only when a step tells you to.

| File | Use it for |
|---|---|
| [00 Zero to deployment](00-zero-to-deploy.md) | the 9 steps, the day each is done, the 3 public URLs |
| [01 Render](01-render-guide.md) | creating the 3 Render services (exact settings) |
| [02 Supabase](02-supabase-guide.md) | database, storage, login |
| [03 Other platforms](03-other-platforms-guide.md) | GitHub, Anthropic key, CAPTCHA, keep-alive monitor, free GPU |
| [04 Free-tier problems](04-free-tier-challenges.md) | what breaks on free tiers and the fix |

## The stack (final — do not add more)
| Piece | Where | Cost |
|---|---|---|
| Prototype (static HTML) | Render static site | free |
| Web app (React build) | Render static site | free |
| API (FastAPI, Docker) | Render free web service | free |
| Database + photo storage + login | Supabase free project | free |
| Keep-alive + uptime alert | UptimeRobot | free |
| CAPTCHA | Cloudflare Turnstile | free |
| Advice LLM | Anthropic API | pay-per-use, spend cap set |
| Model training | Google Colab / Kaggle | free |

**Not before 31 Oct:** n8n workflows, custom domain, Render Blueprint, Sentry, Telegram bot, staging
environment, load tests, backup hosting. They are listed in [00 §"After 31 Oct"](00-zero-to-deploy.md#after-31-oct-only-if-time-allows).
