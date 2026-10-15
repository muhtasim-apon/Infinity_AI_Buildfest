# Live demo script (Congress Day: 3-minute pitch slot, S1 §9.3)

Flow required by S1 §9.3: problem → solution → demo → AI → impact, then judge questions.

## Pre-flight (T-30 min)
1. n8n keep-warm on; open `/healthz` → 200.
2. Supabase dashboard: project active.
3. Phone on hotspot; laptop on venue Wi-Fi; recorded video on desktop as backup.
4. Clear demo account (n8n reset) so history is clean.

## Demo (60–70 s inside the pitch)
| Step | Click | Say |
|---|---|---|
| 1 | `/demo-user` | "One click, Bangla by default." |
| 2 | Scan → choose fixture `blast_01.jpg` | "Photo compressed on the phone, location rounded, metadata stripped." |
| 3 | Result | "Top-3 with calibrated confidence; heat-map shows where it looked." |
| 4 | Advice | "Every line cites its source — no source, no advice." |
| 5 | Scan a non-leaf photo | "When it isn't sure, it says so." |
| 6 | `/demo-admin` → Review → Confirm | "An agronomist confirms; that becomes training data." |
| 7 | Alerts → approve draft | "Three nearby reports → draft alert → human approves → area notified." |

## Likely judge questions (prepared answers)
- *Accuracy?* → give measured macro-F1 with CI and coverage; mention abstention.
- *Why not just ChatGPT on the image?* → calibration, abstention, cost, data sovereignty, citations.
- *Business model?* → PRD §7.
- *What if wrong?* → abstain, agronomist loop, IPM-first, safety lines, admin threshold control.
- *Data from where? Licences?* → `/data`.
- *Scale?* → domain packs, portability, language packs.
