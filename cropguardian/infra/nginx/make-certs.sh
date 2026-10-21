#!/usr/bin/env bash
# Dev TLS certificates for https://localhost. Prefers mkcert (browser-trusted); falls back to a
# self-signed cert generated in a throwaway container (browsers will warn; `curl -k` works).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p certs
if [ -f certs/dev.pem ] && [ -f certs/dev-key.pem ]; then echo "certs already exist"; exit 0; fi
if command -v mkcert >/dev/null 2>&1; then
  mkcert -install >/dev/null 2>&1 || true
  mkcert -cert-file certs/dev.pem -key-file certs/dev-key.pem localhost 127.0.0.1 ::1
  chmod 644 certs/dev-key.pem 2>/dev/null || true   # the unprivileged nginx user must read it (dev only)
else
  echo "mkcert not found: generating a self-signed certificate (install mkcert for a trusted one)"
  # chmod runs INSIDE the container: the key is created root-owned 0600, which nginx-unprivileged cannot read.
  MSYS_NO_PATHCONV=1 docker run --rm --entrypoint sh -v "$(cd certs && (pwd -W 2>/dev/null || pwd)):/certs" alpine/openssl -c \
    'openssl req -x509 -newkey rsa:2048 -nodes -days 365 -keyout /certs/dev-key.pem -out /certs/dev.pem \
       -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null \
     && chmod 644 /certs/dev-key.pem /certs/dev.pem'
fi
