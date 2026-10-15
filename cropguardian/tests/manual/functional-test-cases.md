# Manual functional test cases

Tester · build/commit · device · browser · network · locale recorded per run. Result: Pass / Fail (+ bug link).

| ID | Route | Steps | Expected | Result |
|---|---|---|---|---|
| M01 | `/demo-user` | open link once | lands on `/app`, Bangla, synthetic banner visible | |
| M02 | `/app/scan` | take photo with camera | preview shown; send enabled | |
| M03 | `/app/scan` | pick dark photo | "ছবিটি অন্ধকার" hint, can still send | |
| M04 | `/app/scan` | send with airplane mode | queued message; badge count 1 | |
| M05 | — | disable airplane mode | item sends automatically; result appears | |
| M06 | result | open a diagnosed result | disease name bn, band, top-3 expandable, disclaimer | |
| M07 | result | open advice | steps, safety, ≥ 1 source with title + page | |
| M08 | result | tap 🔊 | Bangla speech or pre-recorded audio plays | |
| M09 | result | upload a photo of a cup | "নিশ্চিত নই" — no disease named as an answer | |
| M10 | `/app/history` | open | newest first; statuses correct | |
| M11 | `/app/alerts` | open | approved alerts only; risk wording; map loads or list fallback | |
| M12 | `/demo-admin` | open | admin dashboard | |
| M13 | `/admin` | change τ without reason | save blocked | |
| M14 | `/admin` | change τ with reason | saved; appears in `/audit` change history | |
| M15 | `/app/review` | confirm / correct / unclear | card removed; farmer notified | |
| M16 | `/audit` | click "generate" | report with all sections; unmeasured = "not yet measured" | |
| M17 | language | toggle bn ↔ en on each page | no missing strings, no overflow | |
| M18 | `/architecture`, `/data`, `/security`, `/presentation`, `/pitchdeck` | open each from a fresh browser | loads without login | |
| M19 | any | refresh on a deep link | page loads (no 404) | |
| M20 | cold start | follow `tests/timeout/cold_start_e2e.md` | graceful waking UI | |
