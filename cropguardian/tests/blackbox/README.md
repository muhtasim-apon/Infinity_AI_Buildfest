# Blackbox tests

Owner: Apon. The API is tested only from the outside (inputs → outputs), per
[`services/api/SPEC.md`](../../services/api/SPEC.md) §4–5.

## Equivalence partitions & boundary values
| ID | Input | Valid | Invalid | Boundaries |
|---|---|---|---|---|
| BB1 | coarse lat / lon | 23.85 / 90.26 | 19.99, 93.01, 23.851 (too precise) | 20.00, 27.00, 88.00, 93.00 |
| BB2 | crop | rice | jute, empty | — |
| BB3 | sha256 | 64 hex | 63 chars, non-hex | 64 |
| BB4 | image size | 1 KB – 5 MB | 0 B, 5 MB + 1 B | 5 MB |
| BB5 | image type | JPEG, PNG, WebP | GIF, SVG, PDF, renamed HTML | — |
| BB6 | history `limit` | 1–50 | 0, 51, −1, "abc" | 1, 50 |
| BB7 | auth | valid farmer token | missing, expired, wrong audience, tampered | expiry ± 1 s |
| BB8 | role | farmer on farmer routes | farmer on `/v1/admin/*` | — |
| BB9 | same image twice | first 201 | — | second returns 200 with the same scan id |
| BB10 | all errors | — | — | `application/problem+json` with a `code` |

## Tools
- **Schemathesis** (property-based fuzzing from OpenAPI, run on staging where `/openapi.json` is enabled):
  `schemathesis run <staging>/openapi.json --checks all` — fails on any 5xx or schema mismatch.
- **Postman / Newman** collection: demo session → create scan → upload → analyze → history;
  `newman run cropguardian.postman_collection.json -e staging.env.json`.
- **Contract**: generated web API types compared with live OpenAPI on every PR.
