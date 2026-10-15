// k6 load test — scan flow against STAGING only (never production with real users).
// Run: k6 run -e BASE=https://cropguardian-api-staging.onrender.com tests/concurrency/k6/scan_flow.js
// Not yet executed. Thresholds are the targets in docs/ai/eval-plan.md §2.
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "2m", target: 20 }, // ramp
    { duration: "5m", target: 20 }, // hold
    { duration: "1m", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],
    "http_req_duration{name:analyze_cached}": ["p(95)<5000"],
  },
};

const BASE = __ENV.BASE;

export function setup() {
  // warm the instance first so the test measures steady state, not the cold start
  http.get(`${BASE}/healthz`, { timeout: "120s" });
}

export default function () {
  const session = http.post(`${BASE}/v1/demo/session`, JSON.stringify({ role: "user" }), {
    headers: { "Content-Type": "application/json" },
  });
  check(session, { "demo session 200": (r) => r.status === 200 });
  // TODO(apon): create scan with a fixture sha256 → PUT fixture image → analyze (tag name: analyze_cached)
  sleep(1);
}
