# Blackbox tests

- `test_scans_contract.py` — equivalence partitions and boundary values (pytest + httpx).
- **Schemathesis** (property-based fuzzing from OpenAPI):
  `schemathesis run http://localhost:8000/openapi.json --checks all --hypothesis-max-examples 200`
  Fails on any 5xx, schema-nonconforming response, or undocumented status code.
- **Postman/Newman** collection `postman/cropguardian.postman_collection.json` (to export from Postman):
  demo session → create scan → upload → analyze → history; run with
  `newman run postman/cropguardian.postman_collection.json -e postman/staging.env.json`.
- `contract/` — compares generated `apps/web/src/lib/api-types.ts` with the live OpenAPI; diff = fail.
