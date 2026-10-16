Updated plan

──────────────────────────────────────────────────────────────────────────────────
 Ready to code?
     
 Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Plan — External resources catalogue + field-level loss-reduction evaluation

 Context

 The user wants two new Markdown documents in the docs-only template:
 1. cropguardian/docs/research/external-resources.md — every free external
    dataset and every other
    external resource the project needs (datasets, knowledge sources, weather/geo
    data, models, tools,
    platforms), with links, licence status and how we use each.
 2. cropguardian/docs/evaluation/field-loss-reduction.md — an honest evaluation
    of "how much will
    field-level loss reduction work": what the evidence says, a transparent
    impact model with
    scenarios, what limits it, and how we will measure it.
    Rules that apply: no uncited numbers (CLAUDE.md #2), no claims of results
    (§20.4), docs only.

 Evidence gathered (verified 2026-10-16, to cite)

 Datasets (image, rice/plant disease):
 - D1 RiceLeafBD (Mendeley kx9rx8p2mz) 1,555 imgs, 4 classes, CC BY 4.0 — already
   in sources.
 - D2 RiceLeafDisease-BD5 (Mendeley sjkptpgv79) 2,545 imgs, 5 classes, CC BY 4.0
   — already.
 - Dhan-Shomadhan (Mendeley znsxdctwtt, DIU, 6 Apr 2021) 1,106 imgs, field +
   white background,
   5 classes (brown spot, leaf scald, blast, tungro, sheath blight), CC BY 4.0.
 - Paddy Doctor (IEEE DataPort, DOI 10.21227/hz4v-af08; paddydoc.github.io)
   16,225 field images,
   13 classes (12 diseases + healthy), India, agronomist-annotated; licence not
   stated on page → verify.
 - Rice Leaf Disease Image Samples (Sethy, Mendeley fwcj7stb8r, v2 2024) 5,932
   imgs, 4 classes
   (BLB, blast, brown spot, tungro), India; licence to verify; RiceSeg-5932 masks
   (92jc6w6mcy).
 - D3 PlantDoc (CC BY 4.0), D4 PlantVillage (licence unconfirmed) — already.
 - Mendeley "Rice Leaf Disease Dataset" z4hx2v3ywc — listed as "found, details to
   verify".
   Impact / loss evidence:
 - Savary et al. 2019, Nature Ecology & Evolution 3:430–439 — global rice loss to
   pests & pathogens
   30.0 % (24.6–40.9 %), expert survey; major rice culprits incl. sheath blight,
   blast, brown spot,
   bacterial blight.
 - FAO 2021 — up to 40 % of global crop production lost to pests annually ("up
   to" figure).
 - Fabregas, Kremer & Schilbach 2019, Science 366:eaay3038 — digital ag info: +4
   % yields, +22 %
   odds of adopting recommended inputs (meta-analysis, SSA + India).
 - Beach et al. 2025, Global Food Security 45:100866 — 20 studies: yield +6 % (95
   % CI +2 to +9 %),
   income +6 %, fertilizer adoption +23 %.
 - Plant clinics Bangladesh (CABI Case Study 19, Rajendran & Islam 2017) —
   observational: regular users
   reported higher yields/profits; not causal; 30 clinics, 10 districts, DAE
   Plant Protection Wing.
 - PlantVillage Nuru — Mrisho et al. 2020: diagnosis accuracy 74–88 % (six
   leaves/plant), better than
   extension agents; Côte d'Ivoire 2024 adoption 45 %; no published yield-impact
   trial found.
 - Search found no randomized evaluation of image-based crop-disease apps on
   yield.
 - Bangladesh context already sourced: S2 (up to 62 % worst case, BRRI 1.0 %
   insect national), S3 (blast
   up to 80 % locally), S4 (no national disease-loss figure), S5 (45 %
   employment).

 Deliverable 1 — docs/research/external-resources.md

 Sections (tables with: name · link · what · size/coverage · licence · access ·
 our use · status):
 1. Rice/plant disease image datasets — primary (D1, D2, Dhan-Shomadhan),
    secondary (Paddy Doctor,
    Sethy + RiceSeg, PlantDoc, PlantVillage, Mendeley z4hx2v3ywc), with a
    "licence verified?" column and
    a merge plan (taxonomy mapping incl. new classes leaf scald / other Paddy
    Doctor classes; dedup).
 2. Knowledge sources for RAG — BRRI, DAE, BARI, IRRI Rice Knowledge Bank, FAO
    IPM — "permission to
    confirm" status; banned-pesticide list (to source).
 3. Weather & climate — Open-Meteo, NASA POWER, (CHIRPS rainfall) — marked
    "verify terms".
 4. Geography & admin boundaries — OpenStreetMap tiles/Nominatim (usage policy),
    GADM / HDX Bangladesh
    boundaries — "verify licence".
 5. Statistics & context — FAOSTAT, BBS, BRRI annual reports, papers above.
 6. Pre-trained models & libraries — timm/ImageNet weights, multilingual-e5-small
    (HF), ONNX Runtime,
    pytorch-grad-cam, Tesseract ben.
 7. Compute & platforms — Colab, Kaggle, Render, Supabase, Cloudflare, n8n,
    UptimeRobot (link to guides).
 8. Evidence base (papers) for impact claims.
 9. Licence-check procedure + attribution text template.
    Every number carries its source; anything unverified is labelled "verify
    before use".

 Deliverable 2 — docs/evaluation/field-loss-reduction.md

 1. Question & honest bottom line: no evidence yet that image-diagnosis apps
    reduce yield loss;
    closest evidence (digital advice) ≈ +4 % to +6 % yield on average → our
    realistic expectation is a
    small average effect, concentrated in outbreak-affected fields; unproven
    until the pilot.
 2. Evidence table (above) with what each does/does not tell us.
 3. Impact pathway & where it breaks: photo taken → correct diagnosis (or honest
    "not sure") → advice
    understood → action taken in time → action effective → loss avoided; plus
    alerts reaching neighbours.
 4. Transparent impact model: avoided loss ≈ L × d × u × a × e (L = share of
    yield lost to the diseases
    we cover; d = correct-and-answered rate; u = share of affected fields where
    the app is used in time;
    a = adherence; e = efficacy of the recommended action). Scenario table
    (conservative / moderate /
    optimistic) where every input is an explicit assumption, bounded by cited
    evidence, with the
    arithmetic shown and labelled illustrative, not a claim.
 5. What limits it (coverage of classes, abstention rate, reach/smartphones,
    timing, efficacy of
    cultural vs chemical control, alert reach, rule-based alert false positives).
 6. Measurement plan: link to pilot-protocol; primary/secondary outcomes; design
    (matched comparison or
    cluster randomisation by village); sample-size formula with example inputs
    marked as assumptions;
    leading indicators measurable in the preliminary window (diagnosis accuracy,
    not-sure rate,
    time-to-advice, advice comprehension); reporting rules (report nulls).
 7. What we may say in the pitch (exact safe wording) and what we may not.

 Consistency updates

 - docs/research/sources.md: add new IDs (D5 Dhan-Shomadhan, D6 Paddy Doctor, D7
   Sethy, D8 RiceSeg,
   S6 Savary, S7 FAO, S8 Fabregas, S9 Beach, S10 CABI plant clinics, S11
   Mrisho/Nuru) with access date.
 - docs/data/datasets.md: add the new datasets to §2 with licence status; link to
   external-resources.
 - Link both new docs from docs/README.md, cropguardian/README.md
   (where-to-start),
   docs/ai/eval-plan.md §5, docs/product/pilot-protocol.md,
   docs/congress/rubric-map.md (business
   value / impact rows), video script line on impact.
 - Rebuild the PDF (builder in scratchpad) with the two new chapters.

 Verification


 - Link check: zero broken relative links; external links resolve as written.
 - Every number in the two new docs traces to an ID in sources.md (manual scan +
   grep of %).
 - Scenario arithmetic re-computed by script; labelled "illustrative
   assumptions".
 - No "agronomist"/human-review wording reintroduced; docs-only rule intact (no
   new non-md files).
 - PDF rebuilds; new chapters listed with page numbers.
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

───────────────────────