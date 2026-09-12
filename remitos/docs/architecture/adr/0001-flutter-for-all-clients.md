# ADR 0001 — Flutter for Android, iOS and Web from one codebase

**Status:** Accepted · **Date:** 2026-09-12 · **Deciders:** Team Leader, UI/UX Lead, Backend Lead

## Context

The Congress requires a product that is *globally scalable* and demonstrably
production-minded (§11.1, Global Scalability & Real-World Impact). The user base splits
into two populations with almost nothing in common:

- **Senders** abroad — modern smartphones, good connectivity, iOS-heavy in Gulf states
  and the US/UK, Android-heavy in Malaysia and Singapore.
- **Recipients** in Bangladesh — Android-dominant, wide device-age spread, and a large
  segment on mobile connections with no data plan at all (BTRC June 2026: 189.83 m mobile
  subscribers against 120.84 m mobile-internet users — roughly **69 m connections without
  data**).

A five-person student team cannot maintain separate native iOS, native Android and web
codebases across a six-month journey and still build an AI core.

## Decision

Use **Flutter** as the single client framework, targeting Android, iOS and Web from one
`apps/mobile/` codebase, with platform-conditional implementations behind interfaces.

The feature-phone population is **not** served by shrinking the app. It is served by a
separate USSD/IVR path (see ADR 0008) that shares the same backend contracts.

## Consequences

**Positive**

- One codebase, one design system, one test suite across three targets.
- Flutter's rendering model means a Bangla-first typographic system behaves identically
  on every platform — a real problem with platform-native text rendering of Bengali
  conjuncts.
- Web target satisfies the Congress requirement for a publicly reachable application
  without a second build pipeline.
- Hot reload materially shortens the Phase 2–3 iteration loop.

**Negative**

- Flutter Web initial bundle is heavy. Mitigated by deferred loading per feature and a
  dedicated low-bandwidth route that serves a minimal shell (see `design_system/modes/`).
- Platform-specific integrations (biometrics, secure enclave, SMS retrieval) need
  channel code — accepted, isolated in `core/`.
- Smaller hiring pool for Flutter than for React Native in Bangladesh — accepted for a
  Congress team; flagged as a scale-up risk in the risk register.

**Rejected alternatives**

| Option | Why not |
|---|---|
| React Native | Web story is weaker; Bengali text rendering inconsistencies across platforms |
| Native iOS + Android + React web | Three codebases; not survivable for a 5-person team |
| PWA only | Cannot access secure enclave for key storage; poor offline UX on low-end Android |

## Related

ADR 0008 (offline-first and USSD), ADR 0012 (Bangla-first).
