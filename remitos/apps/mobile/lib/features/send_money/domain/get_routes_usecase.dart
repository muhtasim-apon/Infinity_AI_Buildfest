/// Use case: obtain ranked routes for a send request.
///
/// STUB. Never compiled. Pure domain.
///
/// This is the single most important call in the product. Everything else is
/// plumbing around the moment a user finds out what their money will actually do.
library;

// import "route_option.dart";

/// What the user asked for.
class SendRequest {
  const SendRequest({
    required this.amountPoisha,
    required this.sourceCurrency,
    required this.corridor,
    required this.recipientId,
    this.preferredEndpoint,
    this.isUrgent = false,
  });

  final int amountPoisha;

  /// ISO 4217 of the funding currency, e.g. "SAR", "AED", "MYR", "USD", "GBP".
  final String sourceCurrency;

  /// Corridor identifier, e.g. "SA-BD".
  final String corridor;

  final String recipientId;

  /// A stated preference, honoured where compliant — not an override of the law.
  final Object? preferredEndpoint;

  /// Set when the user flags an emergency.
  ///
  /// Has a specific, deliberate consequence: **FX timing advice is suppressed**
  /// entirely (see the fx-forecasting model card). A model that delays medicine money
  /// to capture thirty basis points has misunderstood what it is for.
  final bool isUrgent;
}

/// Ranks payout paths for a send request.
///
/// Implementations call `routing-engine` via the repository. The domain layer knows
/// nothing about transport.
abstract class GetRoutesUseCase {
  /// Returns a decision: routes, a required split, or honest infeasibility.
  ///
  /// Server-side sequence this triggers (see `docs/architecture/data-flow.md`):
  ///   1. generate candidate paths across every partner and endpoint
  ///   2. ML-predict landed cost and ETA per candidate
  ///   3. **filter by regulatory ceilings and partner liquidity** ← ADR 0007
  ///   4. optimise on landed amount, with ETA as a secondary objective
  ///   5. generate a Bangla rationale per surviving option
  ///
  /// Step 3 is the step every competitor performs *after* quoting, if at all.
  ///
  /// Failure handling — the network is assumed hostile (ADR 0008):
  ///   • Timeout          → cached routes with a visible staleness marker. A cached
  ///                        route is never presented as a *binding* quote.
  ///   • Offline          → last-known routes, clearly marked, and the transfer can be
  ///                        composed into the outbox but shows "queued", not "sent".
  ///   • Engine degraded  → static routing table per the degradation ladder, and the
  ///                        UI says the system is running on fallback rather than
  ///                        quietly serving worse answers at full confidence.
  ///
  /// TODO(routing): implement against RoutingRepository.
  Future<Object> call(SendRequest request);
}
