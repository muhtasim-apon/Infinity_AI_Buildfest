/// RemitOS — application entry point.
///
/// STUB. This file has never been compiled or run. It declares the intended
/// composition root so the wiring is unambiguous when the team builds it.
///
/// Startup order matters and is deliberate:
///   1. Bindings         — Flutter must be ready before any plugin is touched.
///   2. Local store      — the app is local-first (ADR 0008); the DB opens before
///                         anything reads state, so a cold start with no network
///                         still renders real data rather than a spinner.
///   3. DI               — services registered after the store they depend on.
///   4. Locale           — resolved BEFORE the first frame. Bangla is the default
///                         (ADR 0012); we never flash an English frame first.
///   5. Outbox flush     — queued transfers are submitted opportunistically once
///                         connectivity is observed. Never blocks startup.
library;

import "package:flutter/material.dart";
import "package:flutter/services.dart";

// import "app.dart";
// import "di.dart";

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Portrait-only: the money-entry flow is designed for one-handed use and a
  // rotated split-proposal screen (J3) is unreadable at the sizes elder mode uses.
  await SystemChrome.setPreferredOrientations(<DeviceOrientation>[
    DeviceOrientation.portraitUp,
  ]);

  // TODO(core): await LocalStore.open();
  //   Opens the Drift database, runs migrations, and recovers any outbox entries
  //   left mid-flight by a previous kill. Recovery is idempotent by construction —
  //   every queued transfer carries an idempotency key, so a double-submit after a
  //   crash cannot double-send (ADR 0008).

  // TODO(di): await configureDependencies();

  // TODO(l10n): final locale = await LocaleResolver.resolve();
  //   Order of precedence: explicit user choice → device locale if bn → bn.
  //   Note the default: Bangla, not English, and not the device locale when the
  //   device is set to English but the user never chose (ADR 0012).

  // TODO(offline): OutboxFlusher.start();
  //   Listens to connectivity and drains the queue with backoff. Fire-and-forget:
  //   a user opening the app on a dead network must still reach a usable screen.

  // TODO(observability): await Observability.init();
  //   Sentry with a PII scrubber installed BEFORE the first event can be sent.
  //   See core/analytics/pii_scrubber.dart — amounts, phone numbers, NID patterns
  //   and recipient names are stripped in the beforeSend hook. The residency rule
  //   in ADR 0011 applies to crash telemetry exactly as it applies to prompts.

  // runApp(const RemitOsApp());
  runApp(const _StubApp());
}

/// Placeholder so the file reads as a complete program. Replaced by [RemitOsApp].
class _StubApp extends StatelessWidget {
  const _StubApp();

  @override
  Widget build(BuildContext context) => const MaterialApp(
        home: Scaffold(
          body: Center(
            child: Text(
              "RemitOS — architectural stub.\nNot a running application.",
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
}
