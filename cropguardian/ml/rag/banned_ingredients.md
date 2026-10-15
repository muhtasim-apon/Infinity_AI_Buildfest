# Banned / restricted pesticide active ingredients

**Status: to source.** The validator (rule V5) needs an official Bangladesh list of banned and restricted
active ingredients (Bangla and English names). Record the source URL, issuing authority and date in
`docs/research/sources.md`, then encode the list in `services/api/app/rag/banned.txt` (one name per line).

Until sourced, the validator blocks **all** chemical recommendations (`chemical` must be null) — advice is
limited to cultural/IPM steps. This is the safe default.
