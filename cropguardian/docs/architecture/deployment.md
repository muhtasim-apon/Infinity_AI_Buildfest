# Deployment architecture

Diagram: [`../diagrams/deployment.mmd`](../diagrams/deployment.mmd). Step-by-step:
[`../deployment/01-render-guide.md`](../deployment/01-render-guide.md).

| Component | Host | Plan | Sleeps? | State |
|---|---|---|---|---|
| Web (React build) | Render static site | free | No | none |
| API (FastAPI, Docker) | Render web service | free | **Yes, after 15 min idle** [R1] | none — stateless |
| Postgres + pgvector | Supabase | free | **Paused after 1 week inactivity** [R2] | all relational + vector data |
| Object storage | Supabase Storage | free | with project | images, ONNX weights |
| Auth | Supabase Auth | free | with project | users |
| n8n | n8n Cloud trial or self-hosted (team laptop / free VM) | — | depends | workflows |
| LLM | Anthropic API (or Gemini) | pay-as-you-go / free tier | — | none |
| Weather | Open-Meteo | free, non-commercial | — | none |

## Environments
| Env | Purpose | Data |
|---|---|---|
| local | development | local Postgres or a dev Supabase project, synthetic seed |
| staging | PR previews off; one Render service `cropguardian-api-staging` only when hours allow | synthetic |
| production / demo | judges, pilot | synthetic demo accounts + consented pilot data |

Hours budget: the 750 free instance-hours per workspace [R1] cover **one** API kept warm
24/7 (31 × 24 = 744 h). Staging therefore runs only on demand, or in a second workspace.

## Release flow
`main` → Render auto-deploy → `/readyz` health check → smoke test (n8n monitor) → done.
Rollback: Render dashboard → previous deploy → "Rollback" (no rebuild needed).
