# Project skills (spec 0.4)

Installed at project level so every team member's Claude Code session uses the same versions.
Every third-party skill was read and scanned before install (rule 0.4.3). Pinned upstream commits:

| Skill | Source @ commit | Licence | Status |
|---|---|---|---|
| frontend-design | github.com/anthropics/skills @ `dbd4588f9e1033efb41dad4bef2f7947c8993d44` | Apache-2.0 | installed, unmodified |
| webapp-testing | same commit | Apache-2.0 | installed, unmodified. Note: `scripts/with_server.py` runs the commands you give it with `shell=True` - local use only, never in CI with untrusted input |
| skill-creator | same commit | Apache-2.0 | installed **minus** `eval-viewer/` (loads a remote script from cdn.sheetjs.com at runtime), `scripts/run_eval.py`, `scripts/run_loop.py`, `scripts/improve_description.py` (spawn processes and write into `.claude/commands`), `assets/eval_review.html`. SKILL.md still mentions them; do not run the eval/optimiser workflow |
| threejs-fundamentals, -react-three-fiber, -performance, -materials, -lighting, -geometry, -animation | github.com/CloudAI-X/threejs-skills @ `0e181866f095b5f06d005133876e926515390d95` | MIT (`threejs-LICENSE-MIT.txt`) | docs-only, scanned: no scripts, no injection-style text. They target React 19 / three r186; **spec 15.12 wins** (React 18, pinned three, no remote assets). Not installed: asset-pipeline (npx tooling), loaders, shaders, postprocessing, textures, interaction (not needed for the Sentinel Field hero) |
| cropguardian-safety | project skill (this repo) | project | created in Phase 0 from spec 0.2, 16.22, 19.8 |
| cropguardian-ui | project skill (this repo) | project | created in Phase 2 (17 Oct) from spec 15 |
| pdf, pptx | Anthropic-provided skills | **Proprietary** (LICENSE.txt forbids copying, redistribution and derivative works) | **not committed**. Use the copies provided by Claude (`anthropic-skills:pdf`, `anthropic-skills:pptx`) in Claude Code. Do not paste them into this repo |

Rules: `cropguardian-ui` wins over `frontend-design` where they disagree. Update third-party skills only
deliberately and repeat this review; record the new commit hash here and in `DECISIONS.md` (D-006).
