"""Versioned consent texts (spec 16.17, 7.1 `consents.text_version`).

Single source of truth: the API serves these texts (GET /me/consents) and the database stores the
version the user agreed to, so a later wording change can never be mistaken for the old consent.
Bangla is the source text; wording is team-authored and NOT expert-reviewed (docs/BANGLA_STYLE.md).

To change a text: add a NEW version (never edit a published one) and bump CURRENT_VERSION.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Purpose = Literal["service", "training_use", "push_alerts"]
Locale = Literal["bn", "en"]

CURRENT_VERSION = "consent-v1"
PURPOSES: tuple[Purpose, ...] = ("service", "training_use", "push_alerts")


@dataclass(frozen=True)
class ConsentText:
    purpose: Purpose
    required: bool
    default_granted: bool
    title: dict[Locale, str]
    body: dict[Locale, str]


_V1: dict[Purpose, ConsentText] = {
    "service": ConsentText(
        purpose="service",
        required=True,
        default_granted=False,
        title={"bn": "সেবার জন্য প্রয়োজনীয় তথ্য", "en": "Information needed for the service"},
        body={
            "bn": (
                "ছবি ও এলাকার মোটামুটি তথ্য ব্যবহার করে আপনাকে রোগ শনাক্ত ও পরামর্শ দেওয়া হবে। "
                "এটি ছাড়া সেবা চলবে না।"
            ),
            "en": (
                "Your photos and approximate area are used to identify diseases and give advice. "
                "The service cannot run without this."
            ),
        },
    ),
    "training_use": ConsentText(
        purpose="training_use",
        required=False,
        default_granted=False,
        title={"bn": "মডেল উন্নত করতে ছবি ব্যবহার", "en": "Using photos to improve the model"},
        body={
            "bn": (
                "আমার ছবি ও পর্যালোচকের যাচাই করা ফল ভবিষ্যতে মডেল উন্নত করতে ব্যবহার করা যাবে। "
                "এটি ঐচ্ছিক। আপনি যেকোনো সময় সম্মতি প্রত্যাহার করতে পারবেন।"
            ),
            "en": (
                "My photos and the reviewer-checked results may be used to improve the model "
                "in future. "
                "This is optional. You can withdraw consent at any time."
            ),
        },
    ),
    "push_alerts": ConsentText(
        purpose="push_alerts",
        required=False,
        default_granted=False,
        title={"bn": "এলাকার সতর্কতার বিজ্ঞপ্তি", "en": "Notifications about alerts in your area"},
        body={
            "bn": (
                "আমার এলাকায় সতর্কতা এলে ফোনে বিজ্ঞপ্তি পেতে চাই। "
                "এটি ঐচ্ছিক। আপনি যেকোনো সময় সম্মতি প্রত্যাহার করতে পারবেন।"
            ),
            "en": (
                "I want phone notifications when an alert is issued for my area. "
                "This is optional. You can withdraw consent at any time."
            ),
        },
    ),
}

_BY_VERSION: dict[str, dict[Purpose, ConsentText]] = {CURRENT_VERSION: _V1}


class UnknownConsentError(ValueError):
    """Unknown purpose or version."""


def get_text(purpose: str, version: str = CURRENT_VERSION) -> ConsentText:
    try:
        return _BY_VERSION[version][purpose]  # type: ignore[index]
    except KeyError as exc:
        raise UnknownConsentError(f"unknown consent {purpose!r} / {version!r}") from exc


def current_texts() -> list[ConsentText]:
    return [_BY_VERSION[CURRENT_VERSION][p] for p in PURPOSES]
