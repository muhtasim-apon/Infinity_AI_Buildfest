"""Password hashing, tokens, HMAC, authenticated encryption and password policy (spec 16.4, 16.5).

- Argon2id (t=3, m=64 MiB, p=2) with transparent rehash when parameters change.
- Tokens come from `secrets`; only their SHA-256 is stored, so a database leak yields no token.
- Secrets at rest (TOTP seeds, push keys) use AES-256-GCM with a key derived by HKDF from SECRET_KEY
  and a per-purpose label, so one leaked key never opens another purpose.
- The common-password check is a small bundled list plus zxcvbn's own dictionaries. It is NOT a
  breached-password (HIBP) check and is described as "common passwords" everywhere.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from zxcvbn import zxcvbn

_HASHER = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=2)
# A real hash of a random value, so verifying an unknown account costs the same as a known one.
_DUMMY_HASH = _HASHER.hash(secrets.token_urlsafe(16))
COMMON_PASSWORDS_FILE = Path(__file__).resolve().parent.parent / "data" / "common_passwords.txt"

PolicyLevel = Literal["farmer", "staff"]
_POLICY = {"farmer": (8, 128, 2), "staff": (12, 128, 3)}  # (min length, max length, min zxcvbn)


# --- password hashing -----------------------------------------------------------------------------
def hash_password(password: str) -> str:
    return _HASHER.hash(password)


def verify_password(stored_hash: str | None, password: str) -> bool:
    """Constant-work verification: an unknown account (None) is checked against a dummy hash."""
    if stored_hash is None:
        _verify_quiet(_DUMMY_HASH, password)
        return False
    return _verify_quiet(stored_hash, password)


def _verify_quiet(stored_hash: str, password: str) -> bool:
    try:
        return _HASHER.verify(stored_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(stored_hash: str) -> bool:
    return _HASHER.check_needs_rehash(stored_hash)


# --- tokens and digests ---------------------------------------------------------------------------
def new_token(nbytes: int = 32) -> str:
    """URL-safe random token; 32 bytes = 256 bits."""
    if nbytes < 16:
        raise ValueError("token must carry at least 128 bits")
    return secrets.token_urlsafe(nbytes)


def new_otp() -> str:
    """Six ASCII digits, uniformly random."""
    return f"{secrets.randbelow(1_000_000):06d}"


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def hmac_hex(key: str, *parts: str) -> str:
    message = "\x1f".join(parts).encode()  # unit separator: ("ab","c") != ("a","bc")
    return hmac.new(key.encode(), message, hashlib.sha256).hexdigest()


def safe_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())


# --- authenticated encryption ---------------------------------------------------------------------
def _derive(secret_key: str, purpose: str) -> bytes:
    if len(secret_key) < 32:
        raise ValueError("SECRET_KEY too short for key derivation")
    return HKDF(
        algorithm=hashes.SHA256(), length=32, salt=None, info=f"cropguardian:{purpose}".encode()
    ).derive(secret_key.encode())


def encrypt(secret_key: str, purpose: str, plaintext: str) -> str:
    nonce = secrets.token_bytes(12)
    sealed = AESGCM(_derive(secret_key, purpose)).encrypt(
        nonce, plaintext.encode(), purpose.encode()
    )
    return base64.urlsafe_b64encode(nonce + sealed).decode()


def decrypt(secret_key: str, purpose: str, token: str) -> str:
    try:
        raw = base64.urlsafe_b64decode(token.encode())
        if len(raw) < 13 + 16:
            raise ValueError("ciphertext too short")
        return (
            AESGCM(_derive(secret_key, purpose))
            .decrypt(raw[:12], raw[12:], purpose.encode())
            .decode()
        )
    except (InvalidTag, ValueError) as exc:
        raise ValueError("cannot decrypt") from exc


# --- password policy ------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _common_passwords() -> frozenset[str]:
    lines = COMMON_PASSWORDS_FILE.read_text(encoding="utf-8").splitlines()
    return frozenset(x.strip().lower() for x in lines if x.strip() and not x.startswith("#"))


def _expand_inputs(values: list[str]) -> list[str]:
    """Names, phones and emails the password must not be built from (whole value and each word)."""
    out: list[str] = []
    for value in values:
        out.append(value)
        out.extend(w for w in re.split(r"[^0-9A-Za-zঀ-৿]+", value) if len(w) >= 3)
    return [x for x in out if x]


@dataclass(frozen=True)
class PolicyResult:
    ok: bool
    code: str = ""  # "", "too_short", "too_long", "common", "weak"


def check_password(
    password: str, level: PolicyLevel, user_inputs: list[str] | None = None
) -> PolicyResult:
    min_len, max_len, min_score = _POLICY[level]
    if len(password) < min_len:
        return PolicyResult(False, "too_short")
    if len(password) > max_len:
        return PolicyResult(False, "too_long")  # also bounds Argon2/zxcvbn cost
    if password.lower() in _common_passwords():
        return PolicyResult(False, "common")
    inputs = _expand_inputs(user_inputs or [])
    if zxcvbn(password, user_inputs=inputs)["score"] < min_score:
        return PolicyResult(False, "weak")
    return PolicyResult(True)
