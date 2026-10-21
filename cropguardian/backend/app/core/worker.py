"""Gunicorn worker class: Uvicorn worker with the access log explicitly OFF.

Why: uvicorn's access log prints the full request line including the query string. Tokens or other
secrets must never be logged (spec 0.2.11), and our structlog redaction does not see uvicorn's own
lines. Request logging is done by our middleware (path only, no query). `access_log=False` makes
this a deliberate setting instead of a side effect of gunicorn's `accesslog = None`.
"""

from uvicorn.workers import UvicornWorker


class CgUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "auto", "http": "auto", "access_log": False}  # noqa: RUF012
