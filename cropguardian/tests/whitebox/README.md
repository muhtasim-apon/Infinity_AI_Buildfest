# Whitebox tests — branch coverage of safety-critical modules

Owner: Apon (Salwa for the validator). Tool: pytest + pytest-cov `--cov-branch`, Hypothesis.
Gate: ≥ 80 % branch coverage overall; **100 %** on `decision.py` and `validator.py`.
Files to create: `test_decision.py`, `test_advisory_validator.py`, `test_upload_sanitiser.py`,
`test_outbreak_rules.py`, `test_webhook_sig.py`. Contracts: [`services/api/SPEC.md`](../../services/api/SPEC.md).

## Decision (abstain logic)
| ID | Case | Expected |
|---|---|---|
| WB-D1 | strong logits for blast, T = 1, τ = 0.70 | diagnosed, band high, top-1 = blast |
| WB-D2 | near-uniform logits | not sure, reason `low_confidence`, band low |
| WB-D3 | calibrated max prob exactly τ | **diagnosed** (inclusive boundary) |
| WB-D4 | any NaN / ±inf logit | not sure, reason `invalid_logits`, never raises |
| WB-D5 | energy score above OOD threshold with high softmax | not sure, reason `out_of_distribution` |
| WB-D6 | τ ≤ p < max(τ, 0.90) | band medium |
| WB-D7 (property) | random logits, T > 1 | max prob never exceeds the T = 1 value |
| WB-D8 (property) | logits in [−1e4, 1e4] | finite probabilities summing to 1 ± 1e-6 |

## Advice validator (V1–V6)
| ID | Fixture | Failed rules |
|---|---|---|
| WB-V1 | valid, cultural steps only | none |
| WB-V2 | valid, chemical dose verbatim in cited chunk | none |
| WB-V3 | invalid JSON | V1 |
| WB-V4 | no citations | V2 |
| WB-V5 | citation id not in retrieved set | V3 |
| WB-V6 | dose not found in any cited chunk | V4 |
| WB-V7 | dose matches only after Unicode NFC + whitespace normalisation | none |
| WB-V8 | banned ingredient (English / Bangla / mixed case) | V5 |
| WB-V9 | chemical present, safety line empty | V6 |
| WB-V10 | no citation **and** banned ingredient | V2, V5 (all reported) |
| WB-V11 | banned list not yet sourced + any chemical | blocked |

## Upload sanitiser
| ID | Input | Expected |
|---|---|---|
| WB-U1 | valid JPEG / PNG / WebP | clean RGB JPEG |
| WB-U2 | 0 bytes | 415 |
| WB-U3 | exactly 5 MB | accepted (inclusive) |
| WB-U4 | 5 MB + 1 byte | 413 |
| WB-U5 | HTML or SVG renamed to .jpg/.png | 415 (magic bytes) |
| WB-U6 | truncated JPEG | 422 |
| WB-U7 | decompression-bomb PNG header | 422, fast, no memory spike |
| WB-U8 | 32 px image | 422 (min side 64) |
| WB-U9 | JPEG with appended zip (polyglot) | accepted but re-encoded; zip gone |
| WB-U10 | JPEG with GPS EXIF | output has no EXIF block |
| WB-U11 | PNG with alpha / CMYK JPEG | RGB JPEG |

## Outbreak rules v1
| ID | Case | Expected |
|---|---|---|
| WB-O1 | 2 reports, min 3 | no alert |
| WB-O2 | 3 reports | one **published** alert with the "unverified, rule-based" label |
| WB-O3 | 4th report same area inside cooldown | same alert, count 4 (no duplicate) |
| WB-O4 | not-sure diagnoses | never counted |
| WB-O5 | point exactly on radius | included |
| WB-O6 | report older than window | excluded |
| WB-O7 | count ≥ 2×min and favourable weather | risk high |
| WB-O8 | weather unknown | risk low |
| WB-O9 | non-notifiable disease | no alert |
| WB-O10 | admin-dismissed alert, new reports inside cooldown | no re-publish until cooldown ends |

## Webhook signature
| ID | Case | Expected |
|---|---|---|
| WB-W1 | correct HMAC, ts = now | valid |
| WB-W2 | one hex char changed | invalid |
| WB-W3 | ts = now − 300 s / − 301 s | valid / invalid |
| WB-W4 | ts = now + 301 s | invalid |
| WB-W5 | same (ts, signature) replayed | second invalid |
| WB-W6 | compare function | constant-time compare used |
