# Shared Packages

| Package | Contents |
|---|---|
| `api-contracts/` | OpenAPI specifications - the ONLY sanctioned way services talk synchronously |
| `events/` | Async event schemas, versioned and registered |
| `sdk-dart/` | Generated Dart client for the Flutter app |
| `sdk-python/` | Generated Python client for services and ML |

SDKs are **generated** from the contracts, never hand-written. A hand-written client
drifts from the contract silently, and the drift is discovered in production.

No service reads another service database (ADR 0003). If a service needs data it does
not own, it calls a contract or consumes an event.

Stubs only.
