# Risk register

Likelihood (L) and impact (I): 1 low – 3 high. Score = L × I. Reviewed at every stand-up.
Detailed recoveries: `docs/deployment/challenges-and-recovery.md`.

| ID | Risk | L | I | Score | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| R1 | Bangla KB documents not obtainable/permitted in time | 2 | 3 | 6 | start day 1; fallback to agronomist-written cards; label translated text | Salwa | open |
| R2 | Model under-performs on field photos | 2 | 3 | 6 | abstention; honest reporting; collect own data | Taeen | open |
| R3 | API cold start during judging | 3 | 2 | 6 | keep-warm; waking UI; recorded video | Apon | open |
| R4 | Source-dataset confound inflates metrics | 2 | 3 | 6 | confound probe; Grad-CAM; report | Taeen | open |
| R5 | Integration slips past M2 | 2 | 3 | 6 | daily integration; cut list | Apon | open |
| R6 | LLM cost/quota exhausted | 1 | 2 | 2 | cap; cache; static cards | Raisa | open |
| R7 | Supabase project paused | 2 | 2 | 4 | heartbeat | Apon | open |
| R8 | Render hours exhausted | 1 | 3 | 3 | one service; windows only | Apon | open |
| R9 | No agronomist partner for review loop | 2 | 2 | 4 | university agronomy dept / DAE office outreach | Raisa | open |
| R10 | Team member unavailable | 2 | 2 | 4 | RACI backups; pairing | Apon | open |
| R11 | Unsafe advice shown | 1 | 3 | 3 | validator hard gates; red-team | Salwa | open |
| R12 | PlantVillage licence unclear | 2 | 1 | 2 | don't use until confirmed | Taeen | open |
| R13 | No NRB advisor recruited | 2 | 1 | 2 | outreach via mentors; documented as open | Apon | open |
