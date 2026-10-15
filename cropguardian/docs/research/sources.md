# Sources

**Rule (CLAUDE.md #2):** a number may appear anywhere in `docs/` only if it is listed here with
a URL and access date. Third-party figures are quoted as *their* claim, never as ours.

All entries accessed **2026-10-16** unless stated.

## Congress
| ID | Source | What we use it for |
|---|---|---|
| S1 | *International AI Builders Congress 2026 — Participants Guide* (repo root PDF, 30 pp.) | Challenge definition (§6.4), submission (§9), judging rubric (§11), roles (§13), ethics (§15, §20) |

## Problem context — Bangladesh agriculture
| ID | Source | Claim (as stated by the source) |
|---|---|---|
| S2 | Mongabay, F. Parvin, "Prevention is best defense against Bangladesh crop diseases, researchers say", 15 Jan 2024 — https://news.mongabay.com/2024/01/prevention-is-best-defense-against-bangladesh-crop-diseases-researchers-say/ | State research institutes say five major diseases (rice blast, rice tungro, wheat blast, jute stem rot, powdery mildew) **could cause up to 62 % annual yield loss if outbreaks occur frequently**; government target to cut this to 5 % via early warning, resistant varieties and rotation. BRRI (Bangladesh Rice Journal, 2021) gives a generalised **1.0 %** average annual national rice loss from insect pests. The article does not explain how 62 % was computed — we quote it only as a *worst-case outbreak claim*. |
| S3 | The Business Standard, "Blast attack: Rice yield dropped by 80%" — https://www.tbsnews.net/node/624442 | BRRI reported up to **80 %** yield loss *in some places* from blast on BRRI dhan28 in one boro season — a local outbreak figure, not national. |
| S4 | BRRI-linked review, Bangladesh Rice Journal — https://banglajol.info/index.php/BRJ/article/view/55176/38810 | States there is **no precise, updated national yield-loss figure for rice diseases** — which is itself the argument for field-level detection data. |
| S5 | Bangladesh Bureau of Statistics, Labour Force Survey 2022, via CEIC — https://www.ceicdata.com/en/bangladesh/labour-force-survey-employment-and-employment-rate ; The Daily Star reporting (45.33 %) | Agriculture's share of employment ≈ **45.4 %** in 2022 (largest employing sector). |

## Datasets (licences verified on the dataset page)
| ID | Dataset | Size / classes | Licence |
|---|---|---|---|
| D1 | **RiceLeafBD** — https://data.mendeley.com/datasets/kx9rx8p2mz (v1, published 7 Nov 2025) | 1,555 field RGB images, Sylhet & Dhaka; Healthy 252, Bacterial Leaf Blight 417, Brown Spot 356, Tungro 530 | CC BY 4.0 |
| D2 | **RiceLeafDisease-BD5** — https://data.mendeley.com/datasets/sjkptpgv79 (v2, DOI 10.17632/sjkptpgv79.2, published 28 Jul 2026) | 2,545 field images, Savar (Dhaka), Oct–Nov 2024; Blast 339, Narrow Brown Spot 329, Sheath Blight 454, Tungro 500, Normal 923 | CC BY 4.0 |
| D3 | **PlantDoc** — https://github.com/pratikkayal/PlantDoc-Dataset ; Singh et al., CoDS-COMAD 2020, doi:10.1145/3371158.3371196 | 2,598 in-the-wild images, 13 species, up to 17 disease classes | CC BY 4.0 |
| D4 | **PlantVillage** — https://github.com/spMohanty/PlantVillage-Dataset ; Mohanty, Hughes & Salathé, *Frontiers in Plant Science* 7 (2016), doi:10.3389/fpls.2016.01419 | 54,306 lab-background leaf images, 14 crops, 26 diseases | **Not stated on the repo page — confirm before use**; used for pre-training only if licence confirmed |
| P1 | Paper on D1 — arXiv 2501.08912, https://arxiv.org/abs/2501.08912 | The authors report 91.5 % accuracy with EfficientNet-V2 on their data. **Their number, their split — not ours.** Useful only as a sanity reference. |

## Platform limits
| ID | Source | Facts used |
|---|---|---|
| R1 | Render — Deploy for Free, https://render.com/docs/free | Free web services spin down after 15 min without inbound traffic; spin-up ≈ 1 min; 750 free instance hours per workspace per month; ephemeral filesystem, no persistent disks; single instance; Render may restart any time; free Postgres: 1 GB, **expires 30 days after creation**, 14-day grace then deletion, no backups. |
| R2 | Supabase pricing, https://supabase.com/pricing (as reported in search results; re-check on the page before submission) | Free projects **paused after 1 week of inactivity**; 500 MB database per project; 2 active free projects. |

## Tools referenced (no statistics taken from these)
pytest https://docs.pytest.org · pytest-cov https://pytest-cov.readthedocs.io · Hypothesis https://hypothesis.readthedocs.io ·
Schemathesis https://schemathesis.readthedocs.io · Playwright https://playwright.dev · k6 https://k6.io/docs ·
Locust https://locust.io · OWASP ZAP https://www.zaproxy.org · Bandit https://bandit.readthedocs.io ·
pip-audit https://pypi.org/project/pip-audit · Postman/Newman https://learning.postman.com/docs/collections/using-newman-cli ·
n8n https://docs.n8n.io · ONNX Runtime https://onnxruntime.ai · Open-Meteo https://open-meteo.com ·
Supabase https://supabase.com/docs · Render https://render.com/docs · OWASP Top 10 https://owasp.org/Top10 ·
OWASP Top 10 for LLM Applications https://genai.owasp.org

## To source before use (do not cite until filled)
- DAE / BRRI / BARI disease & treatment guides for the knowledge base — URL, licence/permission, edition date.
- Banned pesticide list (Bangladesh) — official source for the KB exclusion rule.
- Smartphone / mobile-internet penetration among farmers — for the access argument.
