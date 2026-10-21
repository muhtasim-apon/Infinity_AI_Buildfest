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

## Impact & loss evidence (used in docs/evaluation/field-loss-reduction.md)
| ID | Source | Claim (as stated by the source) |
|---|---|---|
| S6 | Savary, S. et al. (2019). The global burden of pathogens and pests on major food crops. *Nature Ecology & Evolution* 3, 430–439. https://doi.org/10.1038/s41559-018-0793-y | Global rice yield loss to pathogens and pests **30.0 % (24.6–40.9 %)**; expert survey (~1,000 responses, 219 experts, 67 countries); major rice causes incl. sheath blight, stem borers, blast, brown spot, bacterial blight, leaf folder, brown planthopper. |
| S7 | FAO (2021), scientific review on climate change and plant pests — https://sfcs.fao.org/newsroom/detail/Climate-change-fans-spread-of-pests-and-threatens-plants-and-crops-new-FAO-study/en | **Up to 40 %** of global crop production lost to pests each year ("up to" figure). |
| S8 | Fabregas, R., Kremer, M., Schilbach, F. (2019). Realizing the potential of digital development: the case of agricultural advice. *Science* 366(6471), eaay3038. https://doi.org/10.1126/science.aay3038 | Meta-analyses: digital agricultural information increased yields by **4 %** and the odds of adopting recommended inputs by **22 %** (sub-Saharan Africa and India). |
| S9 | Beach, R.H., Milliken, C., Franzen, K., Lapidus, D. (2025). Meta-analysis of the impacts of digital information interventions on agricultural development. *Global Food Security* 45, 100866. https://doi.org/10.1016/j.gfs.2025.100866 | 20 studies / 35 estimates: yield **+6 % (95 % CI +2 to +9 %)**, income +6 % (95 % CI +2 to +9 %), fertilizer adoption +23 % (95 % CI +6 to +40 %). |
| S10 | Rajendran, G., Islam, R. (2017). Plant clinics in Bangladesh: are farmers losing less and feeding more? CABI Case Study 19. https://www.gov.uk/dfid-research-outputs/plant-clinics-in-bangladesh-are-farmers-losing-less-and-feeding-more | Observational: regular plant-clinic users identified and managed crop problems better and **reported** higher yields and profits; 30 clinics in 10 districts; not causal. |
| S11 | Mrisho et al. (2020), PlantVillage Nuru diagnostic study (East Africa) — full reference to add | Nuru identified cassava disease symptoms more accurately than extension agents or farmers; **74–88 %** accuracy when six leaves per plant were examined. |
| — | Literature search 2026-10-16 (web) | No randomized evaluation of image-based crop-disease apps (e.g. Plantix, PlantVillage Nuru) on yield found; Nuru has adoption studies (e.g. 45 % adoption among 152 respondents, Côte d'Ivoire, *Frontiers in Agronomy* 2024). |

## Datasets (licences verified on the dataset page)
| ID | Dataset | Size / classes | Licence |
|---|---|---|---|
| D1 | **RiceLeafBD** — https://data.mendeley.com/datasets/kx9rx8p2mz (v1, published 7 Nov 2025) | 1,555 field RGB images, Sylhet & Dhaka; Healthy 252, Bacterial Leaf Blight 417, Brown Spot 356, Tungro 530 | CC BY 4.0 |
| D2 | **RiceLeafDisease-BD5** — https://data.mendeley.com/datasets/sjkptpgv79 (v2, DOI 10.17632/sjkptpgv79.2, published 28 Jul 2026) | 2,545 field images, Savar (Dhaka), Oct–Nov 2024; Blast 339, Narrow Brown Spot 329, Sheath Blight 454, Tungro 500, Normal 923 | CC BY 4.0 |
| D3 | **PlantDoc** — https://github.com/pratikkayal/PlantDoc-Dataset ; Singh et al., CoDS-COMAD 2020, doi:10.1145/3371158.3371196 | 2,598 in-the-wild images, 13 species, up to 17 disease classes | CC BY 4.0 |
| D4 | **PlantVillage** — https://github.com/spMohanty/PlantVillage-Dataset ; Mohanty, Hughes & Salathé, *Frontiers in Plant Science* 7 (2016), doi:10.3389/fpls.2016.01419 | 54,306 lab-background leaf images, 14 crops, 26 diseases | **Not stated on the repo page — confirm before use**; used for pre-training only if licence confirmed |
| D5 | **Dhan-Shomadhan** — https://data.mendeley.com/datasets/znsxdctwtt (v1, DOI 10.17632/znsxdctwtt.1, 6 Apr 2021, Daffodil International University) | 1,106 images, field and white background; Brown Spot, Leaf Scald, Rice Blast, Rice Tungro, Sheath Blight | CC BY 4.0 |
| D6 | **Paddy Doctor** — https://ieee-dataport.org/node/10108 ; https://paddydoc.github.io ; DOI 10.21227/hz4v-af08 | 16,225 field images (India), 13 classes (12 diseases + healthy); Kaggle competition subset 10,407 images | **not stated** — benchmark only until confirmed |
| D7 | **Rice Leaf Disease Image Samples** (Sethy et al.) — https://data.mendeley.com/datasets/fwcj7stb8r (v2, 18 Jul 2024, Sambalpur University) | 5,932 images; Bacterial Blight, Blast, Brown Spot, Tungro | CC BY 4.0 |
| D8 | **RiceSeg-5932** — https://data.mendeley.com/datasets/92jc6w6mcy | pixel masks for D7 images | verify |
| D9 | **Rice Leaf Disease Dataset** (Chaudhari) — https://data.mendeley.com/datasets/z4hx2v3ywc (v2, 18 Jan 2024) | 242 mobile field images; "Rice Blast" named | CC BY 4.0 |
| P1 | Paper on D1 — arXiv 2501.08912, https://arxiv.org/abs/2501.08912 | The authors report 91.5 % accuracy with EfficientNet-V2 on their data. **Their number, their split — not ours.** Useful only as a sanity reference. |

## Data services (terms read 2026-10-16)
| ID | Source | Facts used |
|---|---|---|
| R12 | Open-Meteo terms — https://open-meteo.com/en/terms | free API for **non-commercial use only**; < 10,000 calls/day, 5,000/hour, 600/minute; data CC BY 4.0 |
| R13 | GADM licence — https://gadm.org/license.html | free for academic and non-commercial use; redistribution and commercial use need permission |
| R14 | geoBoundaries — https://www.geoboundaries.org | CC BY 4.0; most commercial use allowed; visible "geoBoundaries" credit required |

## Platform limits
| ID | Source | Facts used |
|---|---|---|
| R1 | Render — Deploy for Free, https://render.com/docs/free | Free web services spin down after 15 min without inbound traffic; spin-up ≈ 1 min; 750 free instance hours per workspace per month; ephemeral filesystem, no persistent disks; single instance; Render may restart any time; free Postgres: 1 GB, **expires 30 days after creation**, 14-day grace then deletion, no backups. **Suspensions:** when the 750 h are used up, all free web services are suspended until the next month; bandwidth over the included amount without a payment method → all free services suspended for the rest of the month; build-minute overrun → new builds disabled for the month (running services keep their last build); Render may suspend a free web service with unusually high outbound traffic (e.g. calls to external databases, APIs, object storage) — moving it to a paid instance restores it; upgrading the workspace plan does not lift free limits; usage-alert emails are sent. |
| R2 | Supabase pricing, https://supabase.com/pricing (as reported in search results; re-check on the page before submission) | Free projects **paused after 1 week of inactivity**; 500 MB database per project; 2 active free projects. |

| R3 | Render — Docker, https://render.com/docs/docker | Service env vars are automatically passed to `docker build` as build args (so never read secrets in a Dockerfile); Dockerfile path configurable; `.dockerignore` respected. |
| R4 | Render — Blueprint spec, https://render.com/docs/blueprint-spec | Static sites: `runtime: static`, `buildCommand`, `staticPublishPath`; no `plan`; `routes`/`headers` optional; `rootDir` supported; blueprint defaults to repo-root `render.yaml`; **env var groups cannot use `sync: false`**. |
| R5 | Supabase — API keys, https://supabase.com/docs/guides/api/api-keys | Legacy `anon`/`service_role` keys deprecated by end of 2026; replacements: publishable (`sb_publishable_…`) and secret (`sb_secret_…`) keys, under Settings → API Keys. |
| R6 | Supabase — JWT signing keys, https://supabase.com/docs/guides/auth/signing-keys | Verify user tokens via JWKS `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json`; ES256 recommended, RS256 supported; HS256 shared secret not recommended for production. |
| R7 | Supabase — Connecting to Postgres, https://supabase.com/docs/guides/database/connecting-to-postgres | Direct connection is IPv6 (IPv4 only with paid add-on); shared pooler is IPv4; session mode port 5432, transaction mode 6543; transaction mode needs prepared statements off (asyncpg `statement_cache_size=0`); copy strings from the **Connect** button. |
| R8 | Supabase — Phone login, https://supabase.com/docs/guides/auth/phone-login | Phone OTP requires a third-party SMS provider (e.g. Twilio, Vonage, MessageBird). |
| R9 | Render — Custom domains, https://render.com/docs/custom-domains | Web services and static sites support custom domains; Hobby workspace includes 2 (extra ones billed per month); TLS certificates created and renewed automatically; the `onrender.com` subdomain can be disabled once a custom domain exists (it then returns 404). |
| R10 | Supabase — Auth CAPTCHA, https://supabase.com/docs/guides/auth/auth-captcha | Providers hCaptcha and Cloudflare Turnstile; enabled under Settings → Authentication → Bot and Abuse Protection; protects sign-in, sign-up and password reset. |
| R11 | Anthropic — claude-code-security-review, https://github.com/anthropics/claude-code-security-review | GitHub Action that reviews PR changes with Claude and comments findings; needs `CLAUDE_API_KEY`; not hardened against prompt injection (trusted PRs only); Claude Code also provides `/security-review` for local changes. |

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

## Datasets — verified in the build (17 Oct task, accessed 2026-10-21)
| ID | What we verified | Evidence |
|---|---|---|
| D1 | CC BY 4.0 (Mendeley `data_licence`); archive `Original Images.zip` 497,906,237 bytes, SHA-256 `3280cc17...2d9c83` published by host and recomputed by us (match); archive holds 1,560 images (page: 1,555) | https://data.mendeley.com/datasets/kx9rx8p2mz/1 ; `docs/datasheets/D1-RiceLeafBD.md` |
| D2 | CC BY 4.0 (host + `License .pdf` in the archive); archive `RiceLeafDisease-BD5.rar` 21,642,468 bytes, SHA-256 `ea5da4b3...c9d2b` published and recomputed (match); archive holds 3,150 images, all 300x300 px (page/README: 2,545 images, 224x224) | https://data.mendeley.com/datasets/sjkptpgv79/2 ; `docs/datasheets/D2-RiceLeafDisease-BD5.md` |
| D3 | GitHub licence field `cc-by-4.0`; pinned commit `5467f6012d78d1c446145d5f582da6096f852ae8`; not yet downloaded | https://github.com/pratikkayal/PlantDoc-Dataset ; `docs/datasheets/D3-D4-N1-X1.md` |
| D4 | GitHub licence field **empty** on 2026-10-21; blocked until the authors' terms are located | https://github.com/spMohanty/PlantVillage-Dataset |
