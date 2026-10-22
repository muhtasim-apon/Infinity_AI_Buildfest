"""i18n completeness and layout check (spec 15.9, 19.6 step 6, corner case CC-40). Exit 1 on a violation.

Rules over `frontend/src/i18n/bn.json` (source locale) and `en.json`:
  1. identical key sets (a key missing in either locale fails);
  2. every value is a non-empty string (no numbers, arrays, nulls, blanks);
  3. Bangla strings contain Bengali script (not copied English) except an explicit allow-list;
  4. Bangla sentences end with the danda, not a Latin full stop, and stay within 15 words;
  5. placeholders ({{name}}) match between the locales;
  6. farmer-facing Bangla never shows a raw percentage (spec 15.5.5);
  7. layout budgets: strings that must fit one line at 360 px and 130 % text size stay short.

`check()` is pure (dicts in, messages out) so it is unit-tested with bad inputs; the CLI is a thin wrapper.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "frontend" / "src" / "i18n"

#: Keys whose Bangla value legitimately contains Latin text (brand/standard names).
LATIN_ALLOWED = {"advice.basedOn"}

#: Layout budgets, in characters of the NFC string: (key regex, max length, why).
#: The bottom tab bar has five equal tabs at 360 px; at 130 % text each gets ~72 px, so those labels
#: must stay a single short word. Button-like keys must fit two wrapped lines at the same size.
LIMITS: list[tuple[re.Pattern[str], int, str]] = [
    (
        re.compile(r"^nav\.(home|scan|history|alerts|more)$"),
        9,
        "bottom tab label (5 tabs at 360 px)",
    ),
    (re.compile(r"^common\."), 30, "shared button / control label"),
    (re.compile(r"\.(primaryCta|secondaryCta|cta)$"), 30, "call-to-action button"),
    (re.compile(r"\.title$"), 60, "screen / card title"),
]

PLACEHOLDER = re.compile(r"{{\s*\w+\s*}}")
# The Bengali Unicode block is U+0980..U+09FF; Bengali digits are U+09E6..U+09EF.
_BN = chr(0x0980) + "-" + chr(0x09FF)
_BN_DIGITS = chr(0x09E6) + "-" + chr(0x09EF)
PERCENT_WORD = "শতাংশ"  # "percent"
BENGALI = re.compile("[" + _BN + "]")
LATIN_FULL_STOP_AFTER_BENGALI = re.compile("[" + _BN + "]" + re.escape(".") + "$")
PERCENT = re.compile("%|[" + _BN_DIGITS + "]+[ ]?" + PERCENT_WORD)
MAX_WORDS = 15


def flatten(node: object, prefix: str = "") -> dict[str, object]:
    """Flatten nested JSON into dotted keys; non-dict leaves keep their raw value for type checks."""
    if not isinstance(node, dict):
        return {prefix: node}
    out: dict[str, object] = {}
    for key, value in node.items():
        dotted = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            out.update(flatten(value, dotted))
        else:
            out[dotted] = value
    return out


def _placeholders(text: str) -> list[str]:
    return sorted(m.replace(" ", "") for m in PLACEHOLDER.findall(text))


def check(bn: dict[str, object], en: dict[str, object]) -> list[str]:
    """Return one message per violation (empty list = clean)."""
    problems: list[str] = []
    bn_flat, en_flat = flatten(bn), flatten(en)

    for key in sorted(set(bn_flat) - set(en_flat)):
        problems.append(f"{key}: missing in en.json")
    for key in sorted(set(en_flat) - set(bn_flat)):
        problems.append(f"{key}: missing in bn.json")

    for locale, flat in (("bn", bn_flat), ("en", en_flat)):
        for key, value in flat.items():
            if not isinstance(value, str):
                problems.append(
                    f"{key}: {locale} value must be a string, got {type(value).__name__}"
                )
            elif not value.strip():
                problems.append(f"{key}: {locale} value is empty")

    for key, value in bn_flat.items():
        if not isinstance(value, str) or not value.strip():
            continue
        text = unicodedata.normalize("NFC", value)
        if key not in LATIN_ALLOWED:
            if not BENGALI.search(text):
                problems.append(f"{key}: Bangla value has no Bengali characters")
            if LATIN_FULL_STOP_AFTER_BENGALI.search(text):
                problems.append(
                    f"{key}: Bangla sentence ends with a Latin full stop (use the danda)"
                )
        for sentence in re.split(r"[।?!]", text):
            words = len(sentence.split())
            if words > MAX_WORDS:
                problems.append(f"{key}: sentence has {words} words (max {MAX_WORDS})")
        if PERCENT.search(text):
            problems.append(f"{key}: farmer-facing Bangla must not show a raw percentage")
        for pattern, limit, why in LIMITS:
            if pattern.search(key) and len(text) > limit:
                problems.append(f"{key}: {len(text)} characters exceeds {limit} ({why})")

    for key in sorted(set(bn_flat) & set(en_flat)):
        b, e = bn_flat[key], en_flat[key]
        if isinstance(b, str) and isinstance(e, str) and _placeholders(b) != _placeholders(e):
            problems.append(f"{key}: placeholders differ between bn and en")
    return problems


def main() -> int:
    try:
        bn = json.loads((I18N / "bn.json").read_text(encoding="utf-8"))
        en = json.loads((I18N / "en.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"check_i18n: cannot read catalogues: {exc}")
        return 1
    problems = check(bn, en)
    if problems:
        print(f"check_i18n: {len(problems)} problem(s)")
        for message in problems:
            print(f"  {message}")
        return 1
    print(f"check_i18n: OK ({len(flatten(bn))} keys, bn and en identical)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
