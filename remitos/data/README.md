# Data

| Path | Contents |
|---|---|
| `schemas/` | JSON Schema, Avro and protobuf contracts; the event registry |
| `contracts/` | Data contracts between producing and consuming services |
| `lineage/` | Field-level lineage from source to warehouse mart |
| `dictionaries/` | Data dictionary **including the reviewed Bangla financial glossary** |
| `synthetic/` | Generator specs for demo data - **labelled synthetic everywhere it renders** |
| `dbt/` | Warehouse transformations, staging and marts |

## Rules

1. **Every event is versioned and registered.** Schema changes are additive; a breaking
   change is a new version, never an edit.
2. **Every event carries `correlation_id`**, tying a user tap to every downstream
   consequence. This is what makes the audit reconstruction in
   `docs/security/audit-readiness.md` possible at all.
3. **Money is integer poisha with an explicit currency.** No floating point, anywhere.
4. **Synthetic data is labelled synthetic on every surface that renders it.** Congress
   section 20.4 prohibits fabricated results presented as real, and the label is how
   that rule is kept rather than merely agreed to.
5. **The Bangla glossary is reviewed by native speakers, not by a model.** Literal
   translation of financial vocabulary produces English-in-Bengali-script that nobody
   actually says (ADR 0012).
