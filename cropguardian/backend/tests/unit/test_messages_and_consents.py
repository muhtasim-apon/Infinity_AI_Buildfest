import re

import pytest

from app.core.consent_texts import (
    CURRENT_VERSION,
    PURPOSES,
    UnknownConsentError,
    current_texts,
    get_text,
)
from app.core.messages import (
    EMAIL_KINDS,
    MessageError,
    check_link,
    clean_text,
    render_email,
    render_sms_otp,
)

BENGALI = re.compile(r"[ঀ-৿]")
LINK = "https://app.example.org/verify?token=abc"


# --- consent texts ---------------------------------------------------------------------------------
def test_three_purposes_with_expected_defaults():
    texts = {t.purpose: t for t in current_texts()}
    assert set(texts) == set(PURPOSES) == {"service", "training_use", "push_alerts"}
    assert texts["service"].required is True
    assert texts["training_use"].required is False
    assert texts["push_alerts"].required is False
    # spec 16.17: training use is optional and DEFAULT OFF; nothing is pre-granted
    assert not any(t.default_granted for t in texts.values())


def test_every_text_has_bangla_source_and_english_mirror():
    for t in current_texts():
        for field in (t.title, t.body):
            assert BENGALI.search(field["bn"]), t.purpose
            assert field["en"].strip()
        # sentences end with the danda; titles are not sentences
        assert t.body["bn"].strip().endswith("।"), t.purpose


def test_optional_consents_say_they_can_be_withdrawn():
    for t in current_texts():
        if not t.required:
            assert "প্রত্যাহার" in t.body["bn"]
            assert "withdraw" in t.body["en"]


def test_consent_lookup_and_unknown_inputs():
    assert get_text("service").purpose == "service"
    for purpose, version in (("marketing", CURRENT_VERSION), ("service", "consent-v0"), ("", "")):
        with pytest.raises(UnknownConsentError):
            get_text(purpose, version)


# --- SMS -------------------------------------------------------------------------------------------
def test_sms_contains_the_code_and_a_safety_line():
    bn = render_sms_otp("123456", "bn")
    en = render_sms_otp("123456", "en")
    assert "123456" in bn
    assert "123456" in en
    assert BENGALI.search(bn)
    assert "কাউকে কোড বলবেন না" in bn
    assert "Do not share" in en
    assert len(bn) < 160  # fits a single SMS


@pytest.mark.parametrize("bad", ["12345", "1234567", "12345a", "১২৩৪৫৬", "", "123 456", "123456\n"])
def test_sms_refuses_anything_but_six_ascii_digits(bad):
    with pytest.raises(MessageError):
        render_sms_otp(bad)


def test_sms_unsupported_locale():
    with pytest.raises(MessageError):
        render_sms_otp("123456", "fr")


# --- email -----------------------------------------------------------------------------------------
CTX = {
    "verify": {"name": "রহিমা", "link": LINK},
    "reset": {"name": "রহিমা", "link": LINK},
    "invite": {"role_bn": "পর্যালোচক", "role_en": "a reviewer", "link": LINK},
    "new_device": {"name": "রহিমা", "when": "21 Oct 2026, 14:00", "device": "Chrome on Android"},
}


@pytest.mark.parametrize("kind", EMAIL_KINDS)
def test_every_email_is_bilingual_with_subject(kind):
    mail = render_email(kind, **CTX[kind])
    assert BENGALI.search(mail.text)
    assert re.search(r"[A-Za-z]{4,}", mail.text)
    assert " · " in mail.subject and BENGALI.search(mail.subject)
    assert BENGALI.search(mail.html)
    assert mail.text.endswith("\n")


@pytest.mark.security
def test_html_is_autoescaped_and_text_has_no_markup_injection():
    hostile = '<script>alert(1)</script> "><img src=x onerror=1>'
    mail = render_email("verify", name=hostile, link=LINK)
    assert "<script>" not in mail.html
    assert "&lt;script&gt;" in mail.html
    assert (
        "onerror" not in mail.html.replace("&#34;", "").replace("&gt;", "")
        or "<img" not in mail.html
    )


@pytest.mark.security
def test_newlines_in_fields_cannot_inject_lines_or_headers():
    mail = render_email(
        "new_device", name="Eve\r\nBcc: attacker@evil.test", when="now", device="x\ny"
    )
    assert "\r" not in mail.text
    assert "Bcc: attacker@evil.test" in mail.text  # kept as inert text on ONE line...
    assert not any(
        line.startswith("Bcc:") for line in mail.text.splitlines()
    )  # ...never a header/line start


@pytest.mark.security
@pytest.mark.parametrize(
    "link",
    [
        "http://app.example.org/x",
        "javascript:alert(1)",
        "https://user:pw@app.example.org/x",
        "https://",
        "//evil.example.org/x",
        'https://app.example.org/x"onmouseover="1',
        "https://app.example.org/x y",
        "https://app.example.org/<x>",
        "",
    ],
)
def test_unsafe_links_are_refused(link):
    with pytest.raises(MessageError):
        render_email("verify", name="x", link=link)


def test_http_localhost_only_when_explicitly_allowed():
    with pytest.raises(MessageError):
        check_link("http://localhost:5173/verify")
    assert check_link("http://localhost:5173/verify", allow_http_localhost=True)
    with pytest.raises(MessageError):
        check_link("http://evil.example.org/", allow_http_localhost=True)


def test_missing_variable_and_unknown_kind_fail_loudly():
    with pytest.raises(MessageError):
        render_email("verify", link=LINK)  # name missing -> StrictUndefined
    with pytest.raises(MessageError):
        render_email("newsletter", name="x")


def test_clean_text_normalises_and_bounds():
    assert clean_text("a" + chr(0) + "b" + chr(31) + "c" + chr(0x2028) + "d") == "a b c d"
    assert clean_text("  lots   of    space  ") == "lots of space"
    assert len(clean_text("x" * 1000)) == 120
    assert clean_text("ক্ষ") == "ক্ষ"
    assert clean_text(None) == "None"
