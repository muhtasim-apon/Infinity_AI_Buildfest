# ADR 0008 — Offline-first client with a USSD/IVR fallback path

**Status:** Accepted · **Date:** 2026-09-12

## Context

BTRC data for June 2026 records **189.83 m active mobile subscribers** against
**120.84 m mobile-internet users**. Roughly **69 m connections have no data plan.**
Smartphone adoption reached 72.8 % in 2025 — which is the same statement as *more than a
quarter of users have no smartphone*.

These are not edge cases. They are disproportionately the rural, older, lower-income
recipients who depend most on remittance income, and they are precisely the population
the Congress's §13.4 warns teams about ignoring ("No Bangla / localization",
"works only on local demo").

A remittance product reachable only by a modern smartphone on a data plan excludes its
most dependent users by design.

## Decision

Two complementary mechanisms.

**1. Offline-first in the Flutter client.** The app is fully usable without connectivity
for everything except final settlement:

- Local-first state; the network is treated as an unreliable synchroniser, not a
  prerequisite.
- An **outbox queue** (`core/offline/`) persists user intent. Transfers composed offline
  are queued, signed, and submitted on reconnect with an idempotency key so a flaky
  network can never double-send.
- Last-known FX rates are cached with a visible staleness indicator and a hard refusal to
  quote a *binding* rate from stale data.
- Conflict resolution: server-authoritative for money, last-write-wins for preferences,
  CRDT for the recipient list (the only structure that genuinely merges).
- A **low-bandwidth mode** target of under 50 KB per screen: system fonts, no imagery,
  text-first layouts.

**2. USSD and IVR for feature phones.** A parallel channel through
`services/notification`, sharing the same backend contracts as the app:

- USSD menu for balance, last transfer status and payout confirmation.
- IVR in **Bangla**, menu-driven, for users who cannot read a USSD menu at all.
- SMS notifications in Bangla script with a transliterated fallback for handsets with no
  Bengali font support — a real and frequently overlooked device limitation.

## Consequences

**Positive** — the addressable recipient base widens by tens of millions; the product
works in a Congress demo hall with saturated wifi, which is not a trivial benefit;
offline-first is also simply better UX on good networks.

**Negative** — substantial engineering cost: the outbox, idempotency, conflict resolution
and staleness semantics are the hardest client work in the project. Two channels means
two test surfaces. USSD requires a telco aggregator relationship, which is listed as a
dependency in the risk register. Queued-transfer semantics must be explained honestly to
users — "sent" versus "queued" is a distinction that matters enormously when the money
is for a hospital.

**Rejected** — online-only (excludes the target user); SMS-only (no usable UX for
composing a transfer); a separate lightweight app (a second codebase, and the users who
need it most cannot install it).

## Related

ADR 0001 (Flutter), ADR 0012 (Bangla-first).
