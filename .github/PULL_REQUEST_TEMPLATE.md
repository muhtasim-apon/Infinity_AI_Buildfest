## What and why

<!-- One paragraph. What changes, and what problem it solves. Phase and day (e.g. "P0 · 17 Oct"). -->

## Definition of done

- [ ] Docstring states contract, inputs, outputs, failure modes and timeout budget
- [ ] Tests added (including invalid input, boundaries, permission and failure modes) under the matching test folder
- [ ] `make gate PHASE=N` output pasted below (or the failing step and why)
- [ ] `/security-review` run on this diff; result saved to `docs/security-reviews/phase-NN.md`
- [ ] Bangla string in `bn.json` first, then `en.json`
- [ ] Any new statistic sourced in `docs/research/sources.md` (URL + access date); no metric without a script + split
- [ ] Any new model has a card in `docs/ai/model-cards/`
- [ ] Any architectural choice or spec deviation recorded in `DECISIONS.md`
- [ ] `PROGRESS.md` updated (DONE / PARTIAL / BLOCKED + reason)

## Checks specific to this codebase

- [ ] No secret, service-role key or `.env` value in the diff; nothing secret reachable from `frontend/`
- [ ] New table has `ENABLE` + `FORCE ROW LEVEL SECURITY`, a tenant-scoped policy, and an entry in `check_rls.py` scope
- [ ] Uploads still pass the magic-byte / size / re-encode / EXIF-strip pipeline
- [ ] Advice paths still refuse to answer without a citation; the validator rules still hold
- [ ] Low-confidence predictions still abstain
- [ ] Works after a cold start (no reliance on local disk or in-memory state surviving)
- [ ] Synthetic data is labelled SIMULATED / DEMO DATA on every surface and in `"synthetic": true` payloads
- [ ] Third-party skills / dependencies reviewed; versions pinned

## Verification

<!-- How this was checked. If it was not run, say so plainly. -->
