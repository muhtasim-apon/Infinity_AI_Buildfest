#!/usr/bin/env bash
# Edge verification (Phase 0 gate: "curl -k https://localhost/health -> 200 with headers").
# Usage: infra/nginx/verify.sh [https_base] [http_base]     defaults: https://localhost  http://localhost
# Exits non-zero on the first failed assertion. Dev certs are self-signed or mkcert, hence curl -k.
set -u
HTTPS="${1:-https://localhost}"
HTTP="${2:-http://localhost}"
fail=0
check() { # description, expected, actual
  if [ "$2" = "$3" ]; then echo "PASS  $1"; else echo "FAIL  $1 (expected '$2', got '$3')"; fail=1; fi
}
has_header() { # description, header name, body of headers
  if printf '%s' "$3" | tr -d '\r' | grep -qi "^$2:"; then echo "PASS  $1"; else echo "FAIL  $1 (missing $2)"; fail=1; fi
}
count_header() { # description, header, headers, expected count
  n=$(printf '%s' "$3" | tr -d '\r' | grep -ci "^$2:")
  check "$1" "$4" "$n"
}

check "HTTP redirects to HTTPS (301)" 301 "$(curl -s -m 10 -o /dev/null -w '%{http_code}' "$HTTP/health")"
H="$(curl -sk -m 10 -D - -o /dev/null "$HTTPS/health")"
check "GET /health over TLS is 200" 200 "$(curl -sk -m 10 -o /dev/null -w '%{http_code}' "$HTTPS/health")"
for h in Strict-Transport-Security Content-Security-Policy X-Content-Type-Options Referrer-Policy \
         Permissions-Policy Cross-Origin-Opener-Policy Cross-Origin-Resource-Policy X-Frame-Options X-Request-ID; do
  has_header "header $h present" "$h" "$H"
done
count_header "CSP appears exactly once (no duplicate from the API)" Content-Security-Policy "$H" 1
count_header "HSTS appears exactly once" Strict-Transport-Security "$H" 1
if printf '%s' "$H" | tr -d '\r' | grep -i '^content-security-policy:' | sed 's/wasm-unsafe-eval//g' | grep -Eq "unsafe-inline|unsafe-eval"; then
  echo "FAIL  CSP must not contain unsafe-inline / unsafe-eval"; fail=1
else echo "PASS  CSP has no unsafe-inline / unsafe-eval"; fi
if printf '%s' "$H" | tr -d '\r' | grep -i '^server:' | grep -Eq '[0-9]+\.[0-9]+'; then
  echo "FAIL  Server header leaks a version"; fail=1
else echo "PASS  Server header has no version"; fi
check "TRACE is blocked (405)" 405 "$(curl -sk -m 10 -X TRACE -o /dev/null -w '%{http_code}' "$HTTPS/health")"
for p in /metrics /health/ready /api/health/ready; do
  check "$p is not reachable from the edge (404)" 404 "$(curl -sk -m 10 -o /dev/null -w '%{http_code}' "$HTTPS$p")"
done
check "2 MB body is refused (413)" 413 "$(head -c 2000000 /dev/zero | curl -sk -m 20 -o /dev/null -w '%{http_code}' -X POST --data-binary @- "$HTTPS/api/anything")"
check "SPA fallback for client routes (200)" 200 "$(curl -sk -m 10 -o /dev/null -w '%{http_code}' "$HTTPS/some/client/route")"
IDX="$(curl -sk -m 10 -D - -o /dev/null "$HTTPS/")"
printf '%s' "$IDX" | tr -d '\r' | grep -qi '^cache-control: no-cache' && echo "PASS  index.html is not cached" || { echo "FAIL  index.html must be no-cache"; fail=1; }
ASSET="$(curl -sk -m 10 "$HTTPS/" | grep -o '/assets/[^"]*\.js' | head -1)"
if [ -n "$ASSET" ]; then
  AH="$(curl -sk -m 10 -D - -o /dev/null "$HTTPS$ASSET")"
  printf '%s' "$AH" | tr -d '\r' | grep -qi '^cache-control: public, max-age=31536000, immutable' && echo "PASS  hashed asset is immutable" || { echo "FAIL  hashed asset cache header"; fail=1; }
  has_header "asset also carries X-Frame-Options" X-Frame-Options "$AH"
else echo "FAIL  no hashed asset found in index.html (is frontend/dist built?)"; fail=1; fi
codes=""; for _ in 1 2 3 4 5 6 7 8 9 10; do codes="$codes $(curl -sk -m 10 -o /dev/null -w '%{http_code}' "$HTTPS/api/auth/login")"; done
case "$codes" in *429*) echo "PASS  auth rate limit returns 429 after the burst ($codes )";; *) echo "FAIL  no 429 from auth limit ($codes )"; fail=1;; esac
[ "$fail" = 0 ] && echo "EDGE CHECKS: PASS" || echo "EDGE CHECKS: FAIL"
exit "$fail"
