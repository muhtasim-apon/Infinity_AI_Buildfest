/// Outbox queue — durable user intent across a hostile network (ADR 0008).
///
/// STUB. Never compiled.
///
/// THE PROBLEM
/// -----------
/// A user composes a transfer on a train, in a village, or in a labour camp with two
/// bars of signal. The request may:
///   • never leave the device,
///   • leave and the response be lost,
///   • leave twice because the user tapped again when nothing happened.
///
/// The third case is the dangerous one. Sending a family's rent twice is worse than
/// not sending it at all.
///
/// THE CONTRACT
/// ------------
///   1. Intent is persisted locally BEFORE any network attempt.
///   2. Every entry carries a client-generated idempotency key, created once and
///      never regenerated on retry. The server deduplicates on it.
///   3. Retries use exponential backoff with jitter.
///   4. The UI shows "queued", never "sent", until the server confirms. This
///      distinction is not pedantry — a user whose mother needs medicine must know
///      whether the money is moving or waiting.
///   5. Entries expire. A transfer queued four days ago against a rate quoted then is
///      no longer valid, and silently executing it at today's rate would be
///      indefensible. Expiry surfaces to the user for re-confirmation.
library;

// import "package:drift/drift.dart";

/// Lifecycle of a queued intent.
///
/// [queued] and [sent] are deliberately distinct, and both are surfaced to the user.
enum OutboxStatus {
  /// Persisted locally; not yet attempted or not yet acknowledged.
  queued,

  /// In flight right now.
  inFlight,

  /// Server acknowledged receipt. Money is moving.
  sent,

  /// Terminal failure after the retry budget. Needs user action.
  failed,

  /// Quote or authorisation aged out. Needs re-confirmation, never silent execution.
  expired,
}

/// One durable unit of user intent.
class OutboxEntry {
  const OutboxEntry({
    required this.id,
    required this.idempotencyKey,
    required this.endpoint,
    required this.payload,
    required this.createdAt,
    required this.expiresAt,
    this.status = OutboxStatus.queued,
    this.attempts = 0,
    this.lastError,
  });

  final String id;

  /// Generated ONCE at creation. Never regenerated on retry — regenerating it is
  /// exactly how a retry becomes a double-send.
  final String idempotencyKey;

  final String endpoint;
  final Map<String, dynamic> payload;
  final DateTime createdAt;

  /// Typically quote validity. Past this the entry must not execute silently.
  final DateTime expiresAt;

  final OutboxStatus status;
  final int attempts;
  final String? lastError;
}

/// Durable queue of user intent.
///
/// Backed by Drift so entries survive process death, OS kill and reboot. An in-memory
/// queue would lose exactly the transfers composed in the conditions this exists for.
abstract class OutboxQueue {
  /// Persists [entry] and returns once it is durably written.
  ///
  /// MUST complete before the UI reports success of any kind to the user.
  Future<void> enqueue(OutboxEntry entry);

  /// Attempts to drain the queue once. Safe to call concurrently; implementations
  /// must guard against two flushes racing the same entry.
  ///
  /// TODO(offline): backoff schedule — 1s, 4s, 15s, 60s, 5m, 30m, then failed.
  ///   Jitter is required: without it, an entire village reconnecting to the same
  ///   tower after an outage retries in lockstep and we DDoS ourselves.
  Future<void> flush();

  /// Watches entries so the UI can show honest per-item state.
  Stream<List<OutboxEntry>> watch();

  /// Marks entries past [expiresAt] as [OutboxStatus.expired] and notifies the user.
  ///
  /// TODO(offline): run on app foreground and on a periodic timer.
  Future<void> expireStale();

  /// User-initiated cancel. Only valid while [OutboxStatus.queued] — once in flight
  /// or sent, cancellation is a server-side reversal, not a local delete.
  Future<void> cancel(String id);
}

/// Conflict policy when local and server state disagree after reconnect.
///
/// Deliberately not uniform — the correct policy differs by data class:
///
///   • **Money** — server is always authoritative. There is no merge semantic for a
///     balance, and a client that believes otherwise will eventually invent funds.
///   • **Preferences** — last-write-wins by timestamp. Cheap, and the blast radius of
///     being wrong is a language toggle.
///   • **Recipient list** — CRDT (add-wins set). This is the only structure here that
///     genuinely merges: a recipient added offline on a phone and another added on
///     web must both survive. Deletion is a tombstone, so a stale device cannot
///     resurrect a removed recipient.
enum ConflictPolicy { serverAuthoritative, lastWriteWins, crdtMerge }
