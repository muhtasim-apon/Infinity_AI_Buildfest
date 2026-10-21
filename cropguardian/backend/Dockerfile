# Crop Guardian API (spec 17.3, 16.18). Build context: this directory.
# No build ARGs and no secrets: Render passes env vars to `docker build` as build args.
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

FROM base AS deps
COPY requirements.txt .
# Optional files (the [x] glob makes COPY succeed when they are absent):
#   requirements.lock  hash-locked install (make lock)
#   wheelhouse/        wheels downloaded on the HOST (make wheelhouse). Used only on networks where TLS inside
#                      the build is intercepted. pip still installs normally otherwise; verification is never disabled.
COPY requirements.loc[k] ./
COPY wheelhous[e] ./wheelhouse/
RUN if [ -d wheelhouse ] && [ -n "$(ls -A wheelhouse 2>/dev/null)" ]; then \
      pip install --no-index --find-links wheelhouse -r requirements.txt; \
    elif [ -f requirements.lock ]; then pip install --require-hashes -r requirements.lock; \
    else pip install -r requirements.txt; fi

FROM base AS runtime
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini gunicorn.conf.py ./
RUN useradd --create-home --uid 10001 appuser
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status==200 else 1)"
# Render injects $PORT (gunicorn.conf.py reads it); workers default to 1 on the free instance.
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
