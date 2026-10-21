"""Alembic environment. Uses MIGRATION_DATABASE_URL (owner/migrator role), not the runtime URL.

Migrations are plain SQL via op.execute (reviewable, and the schema uses features SQLAlchemy models
do not express: RLS, triggers, extensions). `alembic check` drift detection is therefore N/A until
models exist (Phase 1); the gate records that note.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def _url() -> str:
    url = os.environ.get("MIGRATION_DATABASE_URL", "")
    if not url:
        sys.exit("MIGRATION_DATABASE_URL is required")
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


def run_migrations_offline() -> None:
    context.configure(url=_url(), literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
