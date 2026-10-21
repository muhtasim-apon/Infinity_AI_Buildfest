"""Gunicorn settings (spec 17.3 timeouts). Env: PORT (Render), WEB_CONCURRENCY (default 1)."""

import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
worker_class = "app.core.worker.CgUvicornWorker"  # access log off: no query strings in logs
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
timeout = 30
graceful_timeout = 20
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
forwarded_allow_ips = os.environ.get("TRUSTED_PROXY_IPS", "127.0.0.1")
accesslog = None  # structlog handles request logging; avoids logging query strings with tokens
errorlog = "-"
