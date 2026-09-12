## What and why

<!-- One paragraph. What changes, and what problem it solves. -->

## Definition of done

- [ ] Stubs carry a docstring stating contract, inputs, outputs and failure modes
- [ ] Any new statistic is sourced in `docs/research/data/` with a URL and access date
- [ ] Any new model has a card in `docs/ai/model-cards/`
- [ ] Any architectural choice has an ADR (and rejected alternatives are stated)
- [ ] Bangla strings added to `app_bn.arb` alongside English
- [ ] `docs/congress/rubric-map.md` updated if this affects a rubric line

## Checks specific to this codebase

- [ ] No PII in prompt templates, fixtures or logs (ADR 0011)
- [ ] No regulatory limit hard-coded — config with an effective date (ADR 0007)
- [ ] No agent granted an L3 tool (ADR 0010)
- [ ] Money handled as integer poisha; no floating point (ADR 0009)
- [ ] BDT amounts formatted through `BdtFormatter`, not `NumberFormat.currency`
- [ ] Any synthetic data is labelled synthetic on every surface that renders it

## Verification

<!-- How this was checked. If it was not run, say so plainly. -->
