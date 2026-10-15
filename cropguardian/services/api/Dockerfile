# Crop Guardian API — Render free web service
# NOTE: never built. See docs/deployment/render-guide.md.

FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Model baked into the image (default, ADR 0004). Render's filesystem is ephemeral,
# so anything written at runtime is lost on restart — the image is the only durable copy.
ARG MODEL_URL=""
RUN mkdir -p /app/models && if [ -n "$MODEL_URL" ]; then \
      python -c "import urllib.request,sys; urllib.request.urlretrieve(sys.argv[1], '/app/models/classifier.int8.onnx')" "$MODEL_URL"; \
    fi

RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser

# Render injects $PORT. One worker: memory headroom for the ONNX session (ADR 0002).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --proxy-headers"]
