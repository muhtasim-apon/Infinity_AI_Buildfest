# n8n — the automation plane

> Governing decision: [ADR 0006](../../docs/architecture/adr/0006-n8n-as-automation-plane.md).
> n8n owns **integration and orchestration glue**. It owns **no business logic**.

## The line

| n8n owns | The application owns |
|---|---|
| Scheduled ingestion (sanctions, FX, circulars) | Routing decisions |
| Cross-system glue and notification fan-out | Compliance verdicts |
| Human-in-the-loop escalation routing | Ledger postings |
| Operational digests and alerting | Fraud scoring |
| Data-quality and drift triggers | **Anything that moves money** |
| Lifecycle and nurture sequences | Anything on the synchronous request path |

n8n calls application APIs. **The application never calls n8n synchronously in a
user-facing path** — a workflow engine must never be able to hold up a quote.

## Workflow catalogue

| # | Workflow | Trigger | Purpose | Human gate |
|---|---|---|---|---|
| 01 | `kyc_document_pipeline` | Webhook on upload | OCR → extract → quality check → verification queue | On low confidence |
| 02 | `sanctions_list_sync` | Cron, daily 02:00 BST | Fetch OFAC/UN/EU/UK-HMT, diff, re-screen the **whole book** | On any new hit |
| 03 | `fx_rate_ingestion` | Cron, every 15 min | Ingest rate feeds, validate, publish, alert on staleness | No |
| 04 | `corridor_cost_scraper` | Cron, weekly | Collect published competitor and benchmark pricing into `docs/research/data/` | No |
| 05 | `aml_alert_triage` | Event `compliance.decided` | Route to officer queue by risk and capacity, track SLA | **Yes — always** |
| 06 | `transaction_reconciliation` | Cron, daily 01:00 BST | Compare ledger to partner statements, open breaks | On unexplained break |
| 07 | `regulatory_circular_watcher` | Cron, 6-hourly | Detect new/amended Bangladesh Bank circulars → re-index RAG → **flag limit changes** | On a detected limit change |
| 08 | `customer_support_triage_bangla` | Webhook | Classify intent, route, draft a grounded Bangla reply | On send |
| 09 | `model_drift_monitor` | Cron, daily | PSI and performance checks; **trigger degradation** on concept drift | On step-down |
| 10 | `daily_ops_digest` | Cron, 08:00 BST | SLOs, volumes, queue depth, fairness metrics **per group** | No |
| 11 | `incident_escalation` | Alert webhook | Page on-call, open incident, assemble timeline | Yes |
| 12 | `onboarding_nurture_bangla` | Event `user.registered` | Staged Bangla onboarding incl. **scam-awareness education** | No |

## Two workflows that carry unusual weight

**02 — sanctions_list_sync.** It does not merely fetch a list. It **re-screens the
entire existing customer book** against the diff. A name added to OFAC today may match a
customer onboarded two years ago, and a system that only screens at transaction time
will not notice until they transact — which may be never.

**07 — regulatory_circular_watcher.** This is the mechanism that makes ADR 0007 work in
practice. When Bangladesh Bank changes an MFS ceiling, the workflow detects it, re-indexes
the RAG corpus, and **flags the limit change for human confirmation** before the new
value is written to configuration with an effective date. A limit change is a config
change, never a deploy — but it is also never applied without a human confirming the
system read the circular correctly.

## Conventions

1. **Every workflow ships with a `.md` spec** alongside its JSON. Workflow JSON diffs
   poorly in review; the spec is what actually gets reviewed. Spec states: trigger,
   nodes, external dependencies, failure mode, retry policy, human gate, and owner.
2. **Idempotency.** Every workflow is safe to re-run. Schedules fire twice more often
   than anyone expects — after an outage, after a clock change, after a manual retry.
3. **No secrets in the repo.** `credentials/` holds `.example` files only; real
   credentials live in sealed-secrets. n8n credentials are a high-value target: they hold
   API access to systems that touch money.
4. **Failure is loud.** A silently failing sanctions sync is a compliance breach that
   accrues daily. Every workflow has a dead-man's-switch alert — the absence of a
   success signal pages someone, because a workflow that stops running produces no error
   to notice.
5. **No PII leaves the boundary.** Workflows calling external services are subject to the
   same egress filter as application code (ADR 0011).

## Layout

```
automation/n8n/
├── workflows/      *.json exports + matching *.md specs
├── credentials/    *.example.json only — never real credentials
├── custom-nodes/   RemitOS-specific node stubs
└── README.md
```

Nothing here has been imported into an n8n instance or executed.
