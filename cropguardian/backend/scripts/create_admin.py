"""Create the first administrator (the owner runs this once; there is no public staff sign-up).

    docker compose exec api python scripts/create_admin.py --email you@example.org --name "Your Name"

The password is read from the CG_ADMIN_PASSWORD environment variable or prompted (never a flag, so it
stays out of shell history and process lists). Two-factor setup is forced at first sign-in: the QR
secret is shown by the app once, not printed here.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text

from app.core import security
from app.core.config import get_settings
from app.core.ids import uuid7
from app.db.session import make_engine, system_scope
from app.services import events

EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,189}\.[^@\s]{2,}$")


async def create(email: str, name: str, password: str) -> str:
    verdict = security.check_password(password, "staff", [name, email])
    if not verdict.ok:
        raise SystemExit(f"password refused ({verdict.code}): staff passwords need 12+ characters")
    engine = make_engine(get_settings())
    try:
        user_id = str(uuid7())
        async with system_scope(engine) as db:
            exists = (
                await db.execute(
                    text("SELECT 1 FROM users WHERE lower(email) = lower(:e)"), {"e": email}
                )
            ).first()
            if exists:
                raise SystemExit("an account with that email already exists")
            await db.execute(
                text(
                    "INSERT INTO users (id, tenant_id, role, email, display_name, locale, "
                    "password_hash, status, email_verified_at) VALUES (CAST(:id AS uuid), 'real', "
                    "'ADMIN', :e, :n, 'bn', :h, 'ACTIVE', now())"
                ),
                {
                    "id": user_id,
                    "e": email.lower(),
                    "n": name,
                    "h": security.hash_password(password),
                },
            )
            await events.record(
                db, action="admin.created_by_script", actor_role="SYSTEM", object_type="user",
                object_id=user_id,
            )  # fmt: skip
        return user_id
    finally:
        await engine.dispose()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--email", required=True)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()
    if not EMAIL.match(args.email):
        sys.stderr.write("invalid email address\n")
        return 2
    password = os.environ.get("CG_ADMIN_PASSWORD") or getpass.getpass("Admin password: ")
    user_id = asyncio.run(create(args.email.strip(), args.name.strip(), password))
    sys.stdout.write(
        f"created ADMIN {user_id}\n"
        "Sign in at /staff; you will be asked to set up two-factor authentication first.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
