# Product Requirements Document — Crop Guardian (web)

## 1. Vision
Every farmer can know, within a minute, what is wrong with a crop and what to do about it — in
their own language, from a trusted source — and every village hears about an outbreak before it
reaches their field.

## 2. Problem
See SDD §1. Short: diagnosis is slow, advice is biased or unavailable, outbreaks are noticed late,
and there is no national field-level disease data [S4].

## 3. Target users
Farmer (primary), admin (operator — the team). Personas: `personas.md`.

## 4. Jobs to be done
- *When* I see unusual spots on my rice, *I want* to know what it is and what to do today, *so* I
  don't lose my crop or waste money on the wrong spray.
- *When* many farmers in my area report the same disease, *I want* to be warned early, *so* I can
  protect my field.
- *When* the app cannot tell, *I want* it to say so and tell me how to take a better photo, *so* I
  never act on a guess.

## 5. MVP features (31 Oct)
P0: demo access (CAPTCHA) · scan with compression/offline outbox · diagnosis with confidence +
honest "not sure" · cited Bangla advice · history · automatic rule-based alerts (labelled unverified,
in-app) · admin (thresholds, models, KB, users, dismiss alert) · audit page ·
architecture/data/security pages.
P1 (stretch): voice playback · map view · Grad-CAM gallery.
Later: more crops · Precision Farm pack · on-device inference.

## 6. Value proposition & how we will measure it
| For | Value | Measure (pilot) |
|---|---|---|
| Farmer | faster correct action; fewer unnecessary sprays | time-to-correct-treatment; spray count vs comparison group |
| Extension service | aggregate disease map from app use | alert lead time vs official reports |

## 7. Business model (hypotheses to validate in Phase 3–4)
| Segment | Offer | Pricing hypothesis |
|---|---|---|
| Farmers | app free forever | ৳0 |
| Government extension (DAE) / projects | regional dashboard, alerting, aggregate data exports | annual licence / project contract |
| NGOs & development programmes | white-label deployment for their farmer groups | per-programme fee |
| Agri-insurers | aggregate outbreak risk by area (no personal data) | data-subscription |
| Agri-input companies | **non-promotional**: anonymised demand signals; never product placement in advice | subscription, with ethics clause |
Costs today: ৳0 infra (free tiers) + LLM usage (cached → low). Unit economics to be measured.

## 8. Competitors / alternatives
Neighbour/shopkeeper advice, DAE hotlines and Krishi call centres, generic plant-ID apps, general
chatbots. Our difference: Bangla + local datasets + honest abstention + citations + outbreak alerts. (Competitive facts to be sourced in `docs/research/sources.md` before being stated.)

## 9. Success criteria for preliminary
Working public prototype, honest metrics, complete docs, 3-min video.

## 10. Open questions
Which extension office will host the post-preliminary pilot? Final Bangla disease names (checked
against BRRI's published terminology).
