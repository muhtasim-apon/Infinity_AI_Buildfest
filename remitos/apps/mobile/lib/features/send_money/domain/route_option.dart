/// Domain entities for the routing decision — the core of the product.
///
/// STUB. Never compiled. Pure domain: imports nothing from data or presentation.
///
/// DESIGN NOTE — WHY [landedAmountPoisha] IS THE HEADLINE FIELD
/// -----------------------------------------------------------
/// Every competing product leads with the *fee*. A fee is the wrong number: it is not
/// what the sender optimises for, and it hides the exchange-rate margin, which is
/// usually the larger cost. Our sender persona (P1) does this arithmetic himself,
/// badly, across three providers, every month.
///
/// So the model puts landed amount first and treats fee as a subordinate detail. This
/// ordering is a product decision encoded in the type, not a UI preference — a widget
/// cannot accidentally lead with the fee if the entity does not make that easy.
library;

/// Where the money comes out at the recipient's end.
enum PayoutEndpoint {
  /// bKash, Nagad, Rocket wallet.
  mfsWallet,

  /// Scheduled bank account, typically via Binimoy/NPSB.
  bankAccount,

  /// Physical cash at an agent point — the path with the tightest ceilings and the
  /// widest rural reach.
  agentCash,

  /// Doorstep delivery, where a partner offers it.
  homeDelivery,
}

/// Why a route ranked where it did. Surfaced to the user in Bangla and written to the
/// audit log. Never a bare score.
enum RouteReasonCode {
  lowestCost,
  fastest,
  onlyCompliantPath,
  partnerDegraded,
  limitConstrained,
  recipientPreference,
  fxWindowFavourable,
  liquidityConstrained,
}

/// One leg of a payout. A route has one leg normally, or several when regulatory
/// ceilings force a split (ADR 0007).
class PayoutLeg {
  const PayoutLeg({
    required this.endpoint,
    required this.amountPoisha,
    required this.estimatedArrival,
    required this.partnerId,
    this.constraintNote,
  });

  final PayoutEndpoint endpoint;
  final int amountPoisha;
  final DateTime estimatedArrival;
  final String partnerId;

  /// Human-readable, Bangla-ready explanation of the ceiling that shaped this leg.
  /// e.g. "এজেন্ট থেকে দিনে সর্বোচ্চ ৳৩০,০০০".
  ///
  /// Non-null whenever this leg exists *because* of a limit rather than a preference.
  final String? constraintNote;
}

/// A candidate way to deliver money, as ranked by the routing engine.
class RouteOption {
  const RouteOption({
    required this.id,
    required this.legs,
    required this.landedAmountPoisha,
    required this.totalCostPoisha,
    required this.fxRate,
    required this.estimatedArrival,
    required this.arrivalWindow,
    required this.reasonCodes,
    required this.rationaleBn,
    required this.rationaleEn,
    this.incentiveEligible = false,
    this.isProvisionalEstimate = false,
  });

  final String id;

  /// One leg normally; several when a limit forced a legal split.
  final List<PayoutLeg> legs;

  /// **The headline number.** What actually reaches the recipient, in poisha.
  final int landedAmountPoisha;

  /// Everything the sender gives up: fees plus FX margin. Subordinate to landed amount
  /// in every surface.
  final int totalCostPoisha;

  final double fxRate;
  final DateTime estimatedArrival;

  /// Uncertainty, shown rather than hidden. A point ETA the product cannot honour is
  /// worse than an honest window — and FR-14 holds us publicly accountable for it in
  /// transfer history.
  final Duration arrivalWindow;

  final List<RouteReasonCode> reasonCodes;

  /// One line, generated in Bangla — not generated in English and translated
  /// (ADR 0012). Translating a generated explanation reliably loses the explanation.
  final String rationaleBn;
  final String rationaleEn;

  /// Whether this path carries the government remittance incentive. P1 does not
  /// reliably know which channels qualify, so the product states it.
  final bool incentiveEligible;

  /// True when the cost model had no history for this corridor/partner and fell back
  /// to published rates. The UI must say so rather than present a false point estimate
  /// (see the corridor-cost-predictor model card).
  final bool isProvisionalEstimate;

  /// True when regulatory ceilings forced more than one leg.
  bool get isSplit => legs.length > 1;
}

/// The engine's answer to a quote request.
///
/// Note the three-way outcome. [infeasible] exists because the honest answer is
/// sometimes "this cannot be delivered as requested" — said BEFORE the sender pays,
/// not discovered by the recipient at an agent counter (ADR 0007, journey J3).
sealed class RouteDecision {
  const RouteDecision();
}

/// One or more compliant routes, best first.
class RoutesAvailable extends RouteDecision {
  const RoutesAvailable({required this.options, required this.recommended});

  final List<RouteOption> options;

  /// The engine's pick. The user may always choose another; we rank, we do not decide.
  final RouteOption recommended;
}

/// No single endpoint can take the full amount legally, but a split can.
class SplitRequired extends RouteDecision {
  const SplitRequired({required this.proposal, required this.explanationBn});

  final RouteOption proposal;

  /// Why the split exists, in plain Bangla, with the specific limit named. Must be
  /// spoken-capable for low-literacy users (journey J2).
  final String explanationBn;
}

/// Cannot be delivered as requested. Alternatives are offered.
class Infeasible extends RouteDecision {
  const Infeasible({
    required this.reasonBn,
    required this.reasonEn,
    required this.suggestions,
  });

  final String reasonBn;
  final String reasonEn;

  /// e.g. "send a smaller amount today", "add a bank account", "collect over two days".
  /// An infeasible answer without a next step is a dead end, not an explanation.
  final List<String> suggestions;
}
