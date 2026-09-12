/// BDT amount formatting — lakh/crore grouping and Bengali numerals.
///
/// STUB. Never compiled.
///
/// WHY THIS FILE EXISTS
/// --------------------
/// `intl`'s `NumberFormat` groups western-style: 120000 → "120,000".
/// Bangladesh groups South-Asian style: 120000 → "1,20,000".
///
/// On a money screen this is not cosmetic. A user scanning "120,000" against the
/// "1,20,000" they see everywhere else in their life hesitates — and hesitation on a
/// remittance confirmation screen is exactly where trust is lost. Getting the grouping
/// wrong is the single most visible way to signal that a product was not built for
/// Bangladesh.
///
/// The grouping rule: the last three digits group together, then every TWO digits
/// thereafter.
///
///   1000        →      1,000
///   100000      →    1,00,000        (one lakh)
///   10000000    → 1,00,00,000        (one crore)
///
/// Bengali numerals are user-selectable (ADR 0012). Many older users read ১২৩
/// fluently and Arabic numerals slowly, or not at all.
///
/// RULE FOR THE WHOLE CODEBASE: never call `NumberFormat.currency` on a BDT value.
/// Route every BDT amount through this formatter. A lint rule enforces it.
library;

/// Digit systems the user may select.
enum DigitSystem {
  /// 0123456789 — Arabic numerals.
  arabic,

  /// ০১২৩৪৫৬৭৮৯ — Bengali numerals.
  bengali,
}

/// Formats monetary values for Bangladeshi users.
///
/// All amounts are handled as integer **poisha** (1 BDT = 100 poisha). Floating point
/// never touches a monetary value anywhere in this system (ADR 0009).
abstract class BdtFormatter {
  /// Bengali digit glyphs, indexed 0-9.
  static const List<String> bengaliDigits = <String>[
    "০", "১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯",
  ];

  /// Formats [poisha] using South-Asian lakh/crore grouping.
  ///
  /// Returns e.g. "৳১,২০,০০০" for 12000000 poisha with [DigitSystem.bengali].
  ///
  /// TODO(l10n): implement.
  ///   1. Convert poisha → taka + remainder.
  ///   2. Group: last 3 digits, then pairs.
  ///   3. Map digits through [bengaliDigits] when requested.
  ///   4. Prefix ৳ (U+09F3). Note this is the Bengali rupee mark, NOT "Tk" — both
  ///      are used in Bangladesh, and the symbol is correct on a product surface.
  ///   5. Show poisha ONLY when non-zero. Remittance amounts are almost always whole
  ///      taka, and a trailing ".00" adds visual noise to the number that matters most.
  static String format(
    int poisha, {
    DigitSystem digits = DigitSystem.bengali,
    bool showSymbol = true,
  }) {
    throw UnimplementedError("Stub — see TODO above.");
  }

  /// Renders an amount as Bangla words, for TTS and IVR read-back.
  ///
  /// 45000 taka → "পঁয়তাল্লিশ হাজার টাকা"
  ///
  /// Used by the mandatory voice confirmation: any amount captured by voice is read
  /// back and confirmed before money moves (see the bangla-nlu model card). A misheard
  /// amount is a direct financial loss, and "hazar"/"lakh" are easy to confuse in
  /// speech.
  ///
  /// TODO(l10n): implement Bangla number-to-words, including the lakh/crore scale
  ///   words rather than thousands/millions.
  static String toBanglaWords(int poisha) {
    throw UnimplementedError("Stub — see TODO above.");
  }

  /// Parses user input that may mix digit systems and scale words.
  ///
  /// Must accept all of: "45000", "৪৫০০০", "45,000", "৪৫ হাজার", "1.2 lakh".
  /// Users type what they think in, and rejecting "৪৫ হাজার" because it is not
  /// numerals is a product failure, not a validation success.
  ///
  /// Returns poisha, or null if genuinely unparseable.
  ///
  /// TODO(l10n): implement tolerant parsing.
  static int? parse(String input) {
    throw UnimplementedError("Stub — see TODO above.");
  }
}
