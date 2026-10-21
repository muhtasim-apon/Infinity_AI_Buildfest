import base64
import uuid
from datetime import UTC, datetime

import pytest

from app.core import csrf
from app.core.ids import uuid7
from app.core.redirects import safe_return_to
from app.core.security import (
    check_password,
    decrypt,
    encrypt,
    hash_password,
    hmac_hex,
    needs_rehash,
    new_otp,
    new_token,
    safe_equal,
    sha256_hex,
    verify_password,
)
from app.domain.phone import PhoneError, mask_phone, normalise_phone

KEY = "k" * 40


# --- uuid7 -------------------------------------------------------------------------------------
def test_uuid7_version_variant_and_ordering():
    first = uuid7(datetime(2026, 10, 18, tzinfo=UTC))
    later = uuid7(datetime(2026, 10, 19, tzinfo=UTC))
    assert first.version == 7 and later.version == 7
    assert first.variant == uuid.RFC_4122
    assert first < later
    assert uuid7() != uuid7()


def test_uuid7_rejects_naive_and_out_of_range():
    with pytest.raises(ValueError):
        uuid7(datetime(2026, 1, 1))
    with pytest.raises(ValueError):
        uuid7(datetime(1969, 1, 1, tzinfo=UTC))


# --- passwords ---------------------------------------------------------------------------------
@pytest.mark.security
def test_argon2id_hash_verify_and_wrong_password():
    h = hash_password("correct horse battery staple")
    assert h.startswith("$argon2id$") and "m=65536,t=3,p=2" in h
    assert verify_password(h, "correct horse battery staple")
    assert not verify_password(h, "wrong password here")
    assert not needs_rehash(h)


@pytest.mark.security
def test_unknown_account_and_garbage_hash_fail_closed():
    assert verify_password(None, "anything at all") is False  # dummy-hash path
    assert verify_password("not-a-hash", "anything at all") is False
    assert verify_password("", "x") is False


def test_old_parameters_need_rehash():
    from argon2 import PasswordHasher

    weak = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1).hash("pw")
    assert needs_rehash(weak)


@pytest.mark.parametrize(
    ("password", "level", "code"),
    [
        ("short1", "farmer", "too_short"),
        ("x" * 129, "farmer", "too_long"),
        ("password123", "farmer", "common"),
        ("PassWord123", "farmer", "common"),
        ("aaaaaaaa", "farmer", "weak"),
        ("elevenchars", "staff", "too_short"),
        ("aaaaaaaaaaaaaaaa", "staff", "weak"),
    ],
)
def test_password_policy_rejects(password, level, code):
    result = check_password(password, level)
    assert not result.ok and result.code == code


def test_password_policy_accepts_and_uses_user_inputs():
    assert check_password("river-lantern-orchard-47", "farmer").ok
    assert check_password("Tr0ub4dor&3-quietly-purple", "staff").ok
    # a password built from the user's own details is weak even when long
    assert check_password("rahima1990", "farmer").ok
    assert not check_password("rahima1990", "farmer", ["Rahima Begum", "1990"]).ok


# --- tokens, digests, encryption ---------------------------------------------------------------
def test_tokens_otps_digests():
    assert new_token() != new_token()
    assert len(new_token(32)) >= 43
    with pytest.raises(ValueError):
        new_token(8)
    otps = {new_otp() for _ in range(200)}
    assert all(len(o) == 6 and o.isascii() and o.isdigit() for o in otps)
    assert sha256_hex("a") == sha256_hex("a") != sha256_hex("b")
    assert hmac_hex(KEY, "ab", "c") != hmac_hex(KEY, "a", "bc")  # unambiguous framing
    assert safe_equal("abc", "abc") and not safe_equal("abc", "abd")


@pytest.mark.security
def test_encryption_roundtrip_purpose_binding_and_tamper():
    token = encrypt(KEY, "totp", "JBSWY3DPEHPK3PXP")
    assert "JBSWY3DP" not in token
    assert decrypt(KEY, "totp", token) == "JBSWY3DPEHPK3PXP"
    assert encrypt(KEY, "totp", "x") != encrypt(KEY, "totp", "x")  # fresh nonce
    with pytest.raises(ValueError):
        decrypt(KEY, "push", token)  # different purpose -> different key
    with pytest.raises(ValueError):
        decrypt("z" * 40, "totp", token)
    raw = bytearray(base64.urlsafe_b64decode(token))
    raw[-1] ^= 1
    with pytest.raises(ValueError):
        decrypt(KEY, "totp", base64.urlsafe_b64encode(bytes(raw)).decode())
    for junk in ("", "abc", "!!!", base64.urlsafe_b64encode(b"short").decode()):
        with pytest.raises(ValueError):
            decrypt(KEY, "totp", junk)
    with pytest.raises(ValueError):
        encrypt("short", "totp", "x")


# --- phone -------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "raw",
    [
        "01712345678",
        "+8801712345678",
        "8801712345678",
        "008801712345678",
        "০১৭১২৩৪৫৬৭৮",
        " +880 1712-345 678 ",
        "(017) 1234 5678",
    ],
)
def test_phone_normalises_to_e164(raw):
    assert normalise_phone(raw) == "+8801712345678"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "0171234567",
        "017123456789",
        "02012345678",
        "+8801212345678",
        "+441712345678",
        "abc",
        "01712345678; DROP TABLE",
        "0" * 41,
        "+৮৮০১৭১২৩৪৫৬৭৮x",
    ],
)
def test_phone_rejects_invalid(raw):
    with pytest.raises(PhoneError):
        normalise_phone(raw)


def test_phone_rejects_non_string_and_masks():
    with pytest.raises(PhoneError):
        normalise_phone(None)  # type: ignore[arg-type]
    assert mask_phone("+8801712345678") == "+880********78"
    assert mask_phone("+1234") == "*****"


# --- redirects ---------------------------------------------------------------------------------
@pytest.mark.security
@pytest.mark.parametrize(
    "bad",
    [
        "//evil.com",
        "https://evil.com",
        "/\\evil.com",
        "javascript:alert(1)",
        "evil.com",
        "",
        "/%2f%2fevil.com",
        "/%5cevil.com",
        "/%252f%252fevil.com",
        "/a\nb",
        "/a" + "x" * 600,
        "/\t/evil.com",
        "mailto:a@b.c",
        "///evil.com",
        "data:text/html,x",
    ],
)
def test_open_redirects_fall_back_to_default(bad):
    assert safe_return_to(bad) == "/"
    assert safe_return_to(bad, "/home") == "/home"


@pytest.mark.parametrize("good", ["/", "/scans/12", "/alerts?filter=open&page=2", "/a/b#frag"])
def test_good_paths_pass_through(good):
    assert safe_return_to(good) == good


def test_none_uses_default():
    assert safe_return_to(None, "/x") == "/x"


# --- csrf --------------------------------------------------------------------------------------
ALLOWED = ["https://app.example.org"]


def good_request(**over):
    token = csrf.make_token(KEY, "sess-secret")
    base = {
        "method": "POST",
        "secret_key": KEY,
        "binding": "sess-secret",
        "cookie_token": token,
        "header_token": token,
        "origin": "https://app.example.org",
        "referer": None,
        "allowed_origins": ALLOWED,
    }
    return {**base, **over}


@pytest.mark.security
def test_csrf_accepts_valid_and_safe_methods():
    assert csrf.check_request(**good_request()) == ""
    for method in ("GET", "HEAD", "OPTIONS"):
        req = good_request(method=method, header_token=None, origin=None)
        assert csrf.check_request(**req) == ""


@pytest.mark.security
@pytest.mark.parametrize(
    ("over", "reason"),
    [
        ({"origin": "https://evil.example"}, "origin"),
        ({"origin": "null"}, "origin"),
        ({"origin": None, "referer": None}, "origin"),
        ({"origin": None, "referer": "https://evil.example/x"}, "origin"),
        ({"origin": None, "referer": "not a url"}, "origin"),
        ({"header_token": None}, "mismatch"),
        ({"cookie_token": None}, "mismatch"),
        ({"header_token": "other.token"}, "mismatch"),
        ({"binding": "someone-elses-session"}, "invalid"),
        ({"secret_key": "z" * 40}, "invalid"),
    ],
)
def test_csrf_rejects(over, reason):
    assert csrf.check_request(**good_request(**over)) == reason


def test_csrf_referer_fallback_and_malformed_tokens():
    ok = good_request(origin=None, referer="https://app.example.org/page")
    assert csrf.check_request(**ok) == ""
    for bad in ("", "nodot", ".mac", "nonce."):
        assert not csrf.token_is_valid(KEY, "b", bad)
