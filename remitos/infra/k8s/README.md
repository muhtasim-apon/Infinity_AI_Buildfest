# Kubernetes

```
k8s/
├── base/                 deployments, services, HPA, network policies
└── overlays/
    ├── dev/  staging/  prod/
```

Each service has its own HPA - the load profiles genuinely differ (ADR 0003).
Network policies are default-deny. The graph database is reachable only from
`fraud` and `rag-service`: it is a map of who pays whom.

Never applied.
