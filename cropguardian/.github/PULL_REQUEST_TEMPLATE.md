## What and why

<!-- One paragraph. What changes, and what problem it solves. -->

## Definition of done

- [ ] Docstring states contract, inputs, outputs, failure modes and timeout budget
- [ ] Tests added under the matching `tests/<type>/` folder
- [ ] Bangla string in `bn.json` (and `en.json`)
- [ ] Any new statistic sourced in `docs/research/sources.md`
- [ ] Any new model has a card in `docs/ai/model-cards/`
- [ ] Any architectural choice has an ADR
- [ ] `docs/congress/rubric-map.md` updated if a rubric line is affected

## Checks specific to this codebase

- [ ] No service-role key or secret reachable from `apps/web/`
- [ ] New table has RLS enabled and a policy
- [ ] Uploads still pass the MIME / magic-byte / size / EXIF-strip pipeline
- [ ] Advice paths still refuse to answer without a citation
- [ ] Low-confidence predictions still abstain
- [ ] Works after a cold start (no reliance on local disk or in-memory state surviving)
- [ ] Synthetic data labelled synthetic on every surface

## Verification

<!-- How this was checked. If it was not run, say so plainly. -->
