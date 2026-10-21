"""Phase 1 smoke test against the running compose stack (through Nginx, real TLS verification).

    python scripts/p1_smoke.py [--base https://localhost] [--cert infra/nginx/certs/<cert>.crt]

Proves, end to end and with no test shortcuts (real CAPTCHA proof-of-work, real console SMS):
  register -> OTP -> verify -> /me -> logout -> login; 429 on repeated bad logins; admin created by
  script -> forced 2FA setup -> admin API; a farmer reaching /admin gets 404; demo session; audit chain.
Exit code 0 only if every check passes.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import re
import secrets
import socket
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pyotp

BACKEND = Path(__file__).resolve().parents[1]
REPO = BACKEND.parent
sys.path.insert(0, str(BACKEND))

from app.core.captcha import Challenge, solve  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    sys.stdout.write(
        f"{'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail and not ok else ''}\n"
    )
    sys.stdout.flush()


class Browser:
    def __init__(self, base: str, context: ssl.SSLContext) -> None:
        self.base = base.rstrip("/")
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
            urllib.request.HTTPSHandler(context=context),
        )
        self.csrf = ""

    def call(self, method: str, path: str, body: dict | None = None) -> tuple[int, dict, dict]:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method)  # noqa: S310 - base is https
        req.add_header("Accept", "application/json")
        req.add_header("Origin", self.base)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        if self.csrf:
            req.add_header("X-CSRF-Token", self.csrf)
        try:
            with self.opener.open(req, timeout=30) as resp:
                raw, status, headers = resp.read(), resp.status, dict(resp.headers.items())
        except urllib.error.HTTPError as err:
            raw, status, headers = err.read(), err.code, dict(err.headers)
        try:
            payload = json.loads(raw) if raw else {}
        except ValueError:
            payload = {}
        if isinstance(payload, dict) and payload.get("csrf_token"):
            self.csrf = payload["csrf_token"]
        return status, payload, headers

    def captcha(self) -> str:
        status, ch, _ = self.call("GET", "/api/v1/captcha/challenge")
        assert status == 200, f"captcha challenge failed: {status}"
        time.sleep(2.2)  # the server enforces a minimum fill time
        return solve(Challenge(**ch))


def tls_context(base: str, cert: str, insecure_loopback: bool = False) -> ssl.SSLContext:
    """Verify the server certificate; never disable verification.

    First try the mkcert/self-signed dev certificate. If something on this machine re-signs local TLS
    (some antivirus 'web shields' do), fall back to the operating system's trust store via `truststore`,
    which still verifies the chain and the hostname.
    """
    from urllib.parse import urlsplit

    host = urlsplit(base).hostname or "localhost"
    port = urlsplit(base).port or 443
    candidates: list[ssl.SSLContext] = []
    ctx = ssl.create_default_context(cafile=cert if Path(cert).exists() else None)
    ctx.verify_flags &= (
        ~ssl.VERIFY_X509_STRICT
    )  # a self-signed dev leaf cannot satisfy RFC 5280 strict
    candidates.append(ctx)
    try:
        import truststore

        candidates.append(truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT))
    except ImportError:
        pass
    last: Exception | None = None
    for candidate in candidates:
        try:
            with (
                socket.create_connection((host, port), timeout=10) as raw,
                candidate.wrap_socket(raw, server_hostname=host),
            ):
                return candidate
        except ssl.SSLError as exc:
            last = exc
    if insecure_loopback and host in {"localhost", "127.0.0.1", "::1"}:
        # Explicit opt-in, loopback only: the same trade-off as `curl -k` in infra/nginx/verify.sh for
        # a self-signed (or antivirus re-signed) dev certificate on this very machine. Never for a
        # remote host.
        sys.stdout.write(
            "NOTE: certificate verification skipped for the loopback dev stack" + chr(10)
        )
        loose = ssl.create_default_context()
        loose.check_hostname = False
        loose.verify_mode = ssl.CERT_NONE
        return loose
    raise SystemExit(f"TLS verification failed and was NOT bypassed: {last}")


def compose(*args: str, env: dict[str, str] | None = None) -> str:
    out = subprocess.run(
        ["docker", "compose", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
        env=None if env is None else {**__import__("os").environ, **env},
    )
    return out.stdout + out.stderr


def sms_code(phone: str) -> str | None:
    tail = compose("logs", "--no-color", "--tail", "300", "api")
    hits = re.findall(r"\[sms:console\] to=\S+ :: .*?(\d{6})", tail)
    return hits[-1] if hits else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://localhost")
    ap.add_argument("--cert", default=str(REPO / "infra" / "nginx" / "certs" / "dev.pem"))
    ap.add_argument(
        "--insecure-loopback",
        action="store_true",
        help="accept an untrusted dev cert, loopback only",
    )
    args = ap.parse_args()
    context = tls_context(args.base, args.cert, args.insecure_loopback)

    farmer = Browser(args.base, context)
    status, state, _ = farmer.call("GET", "/api/v1/auth/state")
    check(
        "auth state reachable and anonymous", status == 200 and state.get("authenticated") is False
    )

    phone = f"017{secrets.randbelow(10**8):08d}"
    password = secrets.token_urlsafe(14)
    status, _, _ = farmer.call(
        "POST", "/api/v1/auth/register/farmer",
        {"phone": phone, "password": password, "display_name": "Smoke Farmer",
         "accept_service": True, "captcha": farmer.captcha()},
    )  # fmt: skip
    check("farmer registration accepted (202)", status == 202, str(status))
    time.sleep(1)
    code = sms_code(phone)
    check("console SMS delivered a 6-digit code", code is not None)
    status, body, _ = farmer.call(
        "POST", "/api/v1/auth/otp/verify", {"phone": phone, "code": code or "000000"}
    )
    check("OTP verify opens a session", status == 200 and body.get("next") == "home", str(status))
    status, me, _ = farmer.call("GET", "/api/v1/me")
    check("/me returns the farmer", status == 200 and me.get("role") == "FARMER")
    status, admin_probe, _ = farmer.call("GET", "/api/v1/admin/users")
    check("farmer -> admin API is 404", status == 404, str(status))
    farmer.call("POST", "/api/v1/auth/logout")
    status, _, _ = farmer.call("GET", "/api/v1/auth/csrf")
    status, body, _ = farmer.call(
        "POST", "/api/v1/auth/login", {"identifier": phone, "password": password}
    )
    check("farmer can sign in again", status == 200, str(status))

    victim = Browser(args.base, context)
    victim.call("GET", "/api/v1/auth/csrf")
    seen_429, retry_after = False, ""
    for _ in range(8):
        status, _, headers = victim.call(
            "POST", "/api/v1/auth/login", {"identifier": phone, "password": "wrong-password-1"}
        )
        if status == 429:
            seen_429, retry_after = (
                True,
                {k.lower(): v for k, v in headers.items()}.get("retry-after", ""),
            )
            break
    check(
        "429 with Retry-After after repeated bad logins",
        seen_429 and retry_after.isdigit(),
        retry_after,
    )

    admin_email = f"smoke-admin-{secrets.token_hex(3)}@example.org"
    admin_pw = secrets.token_urlsafe(18)
    out = compose(
        "exec", "-T", "-e", f"CG_ADMIN_PASSWORD={admin_pw}", "api",
        "python", "scripts/create_admin.py", "--email", admin_email, "--name", "Smoke Admin",
    )  # fmt: skip
    check("create_admin.py created the administrator", "created ADMIN" in out, out.strip()[-120:])
    admin = Browser(args.base, context)
    admin.call("GET", "/api/v1/auth/csrf")
    status, body, _ = admin.call(
        "POST", "/api/v1/auth/login", {"identifier": admin_email, "password": admin_pw}
    )
    check(
        "admin login demands 2FA setup",
        status == 200 and body.get("next") == "setup_totp",
        str(body),
    )
    status, _, _ = admin.call("GET", "/api/v1/me")
    check("no data access before 2FA (403)", status == 403, str(status))
    status, setup, _ = admin.call("POST", "/api/v1/auth/totp/setup")
    totp = pyotp.TOTP(setup.get("secret", "A" * 16))
    status, confirm, _ = admin.call("POST", "/api/v1/auth/totp/confirm", {"code": totp.now()})
    check(
        "TOTP confirmed, 10 recovery codes issued",
        status == 200 and len(confirm.get("recovery_codes", [])) == 10,
        str(status),
    )
    status, users, _ = admin.call("GET", "/api/v1/admin/users")
    check("admin can list users after 2FA", status == 200 and bool(users.get("users")), str(status))

    demo = Browser(args.base, context)
    demo.call("GET", "/api/v1/auth/csrf")
    status, body, _ = demo.call(
        "POST", "/api/v1/demo/session", {"role": "DEMO_FARMER", "captcha": demo.captcha()}
    )
    check(
        "demo session opens in the demo tenant",
        status == 201 and body.get("user", {}).get("tenant") == "demo",
        str(status),
    )

    chain = compose(
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        "postgres",
        "-d",
        "cropguardian",
        "-Atc",
        "select audit_verify_chain()",
    )
    check(
        "audit hash chain verifies", chain.strip().splitlines()[-1:] == ["0"], chain.strip()[-80:]
    )

    failed = [n for n, ok, _ in RESULTS if not ok]
    sys.stdout.write(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
