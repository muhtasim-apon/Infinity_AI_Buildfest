# Data sovereignty

Congress §15 requires "data-sovereignty awareness — respect for governance, compliance, and ownership".

## Principles
1. **Farmers own their photos and records.** Licence to us is limited to providing the service,
   and — only with separate opt-in — to improving the model.
2. **Personal data does not leave our controlled systems.** The LLM receives disease name, crop,
   growth stage and public KB text; never phone, name, exact location or images.
3. **Inference stays in our API.** Images are not sent to third-party vision APIs.
4. **Aggregates are shared, individuals are not.** Outbreak alerts carry disease + area + risk only.
5. **No sale of data.** Any future data partnership (e.g. DAE) is aggregate-only and documented.

## Hosting regions (honest statement)
| Component | Region | Note |
|---|---|---|
| Supabase (DB, Storage, Auth) | nearest available region to Bangladesh (choose at project creation; record here) | no Bangladesh region exists on these free tiers |
| Render (API, web) | choose Singapore if offered for the service | stateless — holds no data at rest |
| LLM provider | provider's region | receives no personal data (principle 2) |

Production path: if a government partner requires in-country hosting, the Docker API and a
self-hosted Postgres/pgvector + MinIO can move to a Bangladeshi data centre without code
changes (only connection strings) — this portability is a design goal.

## Applicable law to track
Bangladesh's data-protection framework (personal data protection ordinance/act — confirm the
current instrument and its status before submission and cite it in `docs/research/sources.md`).
Until confirmed, we apply GDPR-style principles: purpose limitation, minimisation, consent,
access, deletion.
