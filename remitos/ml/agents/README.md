# Agents

Implementation of `docs/ai/agent-design.md`.

| Agent | Authority | Role |
|---|---|---|
| `compliance_agent` | L1 draft | Investigates alerts, builds evidence bundles incl. contradictions |
| `routing_agent` | L2 reversible | Handles cases the optimiser cannot express; writes the Bangla rationale |
| `support_agent` | L0/L1 | Grounded Bangla answers; never speculates on compliance decisions |
| `research_agent` | L0 | Corridor and competitor monitoring, always attributed |
| `reconciliation_agent` | L1 draft | Ranks break hypotheses and proposes a correcting entry |

**L3 tools - moving funds, releasing a hold, overriding a BLOCK, changing a limit -
are absent from the registry entirely.** They are not present-but-refused; an agent
cannot see them (ADR 0010).

Every run is bounded by steps, tokens and wall-clock. Exhausting a budget escalates
with partial findings; it never fabricates a conclusion.

Stubs only.
