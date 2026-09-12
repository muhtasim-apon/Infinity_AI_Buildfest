# Infrastructure

| Path | Contents |
|---|---|
| `docker/` | `docker-compose.yml` for the full local stack |
| `k8s/base/` + `k8s/overlays/` | Deployments, services, HPA, network policies; dev/staging/prod overlays |
| `terraform/` | Modules and per-environment stacks |
| `observability/` | Prometheus, Grafana dashboards, OTel collector, Loki |
| `security/` | OPA policies, sealed-secrets, Trivy configuration |

**Nothing here has been applied, planned, built or deployed.**

## Deliberate choices

**Independent scaling is the point of the service split** (ADR 0003). Each service has
its own HPA because the load profiles genuinely differ: routing-engine is CPU-bound and
bursty, ledger is write-heavy and must never lose data, rag-service is embedding-bound.
A shared scaling policy would be the worst of every world.

**Network policies are default-deny.** A service may reach only what it is declared to
need. The graph database is the most sensitive store in the system - it is a map of
who pays whom - and is reachable only from `fraud` and `rag-service`.

**Residency is an infrastructure constraint, not a code one** (ADR 0011). Node pools
holding class C1 to C4 data are pinned to in-country regions, and the Terraform module
refuses to place them elsewhere. Enforcing residency only in application code leaves it
one misconfigured deployment away from breaking.

**DR is in-country.** Geographically separated capacity inside Bangladesh, not a
cheaper region abroad. RPO 0 / RTO 15 min for the ledger.
