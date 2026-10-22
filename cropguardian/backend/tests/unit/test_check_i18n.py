"""check_i18n.py is a gate step (spec 19.6 step 6): prove it fails on each class of bad catalogue."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_i18n.py"
_spec = importlib.util.spec_from_file_location("check_i18n", SCRIPT)
assert _spec and _spec.loader
check_i18n = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_i18n)

E_ACUTE = "e" + chr(0x0301)  # "e" + combining acute accent: 2 code points, 1 character after NFC
GOOD_BN = {"nav": {"home": "হোম"}, "scan": {"title": "ছবি তুলুন", "hint": "কাছে আনুন।"}}
GOOD_EN = {"nav": {"home": "Home"}, "scan": {"title": "Take a photo", "hint": "Move closer."}}


def problems(bn: dict, en: dict) -> list[str]:
    return check_i18n.check(bn, en)


def test_a_clean_catalogue_has_no_problems() -> None:
    assert problems(GOOD_BN, GOOD_EN) == []


def test_the_real_catalogues_are_clean() -> None:
    i18n = Path(__file__).resolve().parents[3] / "frontend" / "src" / "i18n"
    bn = json.loads((i18n / "bn.json").read_text(encoding="utf-8"))
    en = json.loads((i18n / "en.json").read_text(encoding="utf-8"))
    assert problems(bn, en) == []


def test_a_key_missing_in_either_locale_fails() -> None:
    en_missing = {"nav": {"home": "Home"}, "scan": {"title": "Take a photo"}}
    assert any("scan.hint: missing in en.json" in p for p in problems(GOOD_BN, en_missing))
    bn_missing = {"nav": {"home": "হোম"}, "scan": {"title": "ছবি তুলুন"}}
    assert any("scan.hint: missing in bn.json" in p for p in problems(bn_missing, GOOD_EN))


@pytest.mark.parametrize("bad", ["", "   ", None, 3, ["x"], {"nested": ""}])
def test_values_must_be_non_empty_strings(bad: object) -> None:
    bn = {"nav": {"home": "হোম"}, "scan": {"title": bad}}
    en = {"nav": {"home": "Home"}, "scan": {"title": "x"}}
    assert problems(bn, en), f"{bad!r} should have been rejected"


def test_bangla_value_must_contain_bengali_script() -> None:
    out = problems({"scan": {"title": "Take a photo"}}, {"scan": {"title": "Take a photo"}})
    assert any("no Bengali characters" in p for p in out)


def test_the_latin_allow_list_is_honoured() -> None:
    bn = {"advice": {"basedOn": "Based on BRRI"}}
    assert problems(bn, {"advice": {"basedOn": "Based on BRRI"}}) == []


def test_a_latin_full_stop_after_bangla_fails() -> None:
    out = problems({"scan": {"hint": "কাছে আনুন."}}, {"scan": {"hint": "Move closer."}})
    assert any("danda" in p for p in out)


def test_a_bangla_sentence_over_fifteen_words_fails() -> None:
    long_sentence = " ".join(["শব্দ"] * 16) + "।"
    out = problems({"scan": {"hint": long_sentence}}, {"scan": {"hint": "x"}})
    assert any("16 words" in p for p in out)
    ok_sentence = " ".join(["শব্দ"] * 15) + "।"
    assert problems({"scan": {"hint": ok_sentence}}, {"scan": {"hint": "x"}}) == []


def test_placeholders_must_match_between_locales() -> None:
    out = problems({"e": {"retry": "{{seconds}} সেকেন্ড"}}, {"e": {"retry": "in {{secs}} s"}})
    assert any("placeholders differ" in p for p in out)
    assert (
        problems({"e": {"retry": "{{ seconds }} সেকেন্ড"}}, {"e": {"retry": "{{seconds}} s"}}) == []
    )


@pytest.mark.parametrize("text", ["৯০% নিশ্চিত", "৯০ শতাংশ নিশ্চিত"])
def test_farmer_copy_must_not_show_a_raw_percentage(text: str) -> None:
    out = problems({"result": {"band": text}}, {"result": {"band": "High"}})
    assert any("percentage" in p for p in out)


def test_bottom_tab_labels_must_fit_five_tabs_at_360px() -> None:
    long_label = "খুবই লম্বা ট্যাব"  # 15 characters
    out = problems({"nav": {"home": long_label}}, {"nav": {"home": "Home"}})
    assert any("bottom tab label" in p for p in out)


def test_layout_budgets_count_the_normalised_string_not_the_code_points() -> None:
    # "e" + combining acute is 2 code points but ONE character once normalised to NFC
    thirty = "অ" + E_ACUTE * 29  # 30 characters after NFC, 59 code points before it
    assert not any(
        "exceeds" in p for p in problems({"common": {"x": thirty}}, {"common": {"x": "x"}})
    )
    thirty_one = "অ" + E_ACUTE * 30
    assert any(
        "exceeds 30" in p for p in problems({"common": {"x": thirty_one}}, {"common": {"x": "x"}})
    )


def test_button_and_title_budgets() -> None:
    assert any(
        "shared button" in p
        for p in problems({"common": {"retry": "অ" * 31}}, {"common": {"retry": "x"}})
    )
    assert any(
        "screen / card title" in p
        for p in problems({"scan": {"title": "অ" * 61}}, {"scan": {"title": "x"}})
    )


def test_flatten_handles_non_dict_roots_without_crashing() -> None:
    assert check_i18n.flatten("text", "k") == {"k": "text"}
    assert check_i18n.flatten({"a": {"b": 1}}) == {"a.b": 1}
