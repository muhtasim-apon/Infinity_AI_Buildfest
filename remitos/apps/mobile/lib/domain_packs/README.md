# Domain Packs

See [ADR 0002](../../../../docs/architecture/adr/0002-domain-pack-architecture.md).

A pack supplies exactly four things and may supply nothing else:
**config · schemas · prompts · models.**

The core imports nothing from a pack. A core change made to accommodate a pack requires
a new ADR — and if that happens twice for the same reason, the abstraction is wrong.

| Pack | Challenge area (FinSphere AI) | Status |
|---|---|---|
| `borderless_money/` | Cross-border payments and remittance intelligence | **ACTIVE** |
| `credit/` | CreditForAll — alternative-data credit scoring | Stub |
| `fraud/` | FraudShield — real-time transaction defence | Stub |
| `wealth/` | WealthPilot — AI advisory for everyday savers | Stub |
| `sme/` | SME Capital Engine — working-capital intelligence | Stub |

The stubs declare their extension points. They do not implement speculative features —
an abstraction validated against one real product beats four half-built ones.
