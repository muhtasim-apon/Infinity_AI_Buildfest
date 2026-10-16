# Live demo script (Congress Day: 3-minute pitch slot, S1 §9.3)

Flow required by S1 §9.3: problem → solution → demo → AI → impact, then judge questions.

## Pre-flight (T-30 min)
1. Keep-warm monitor on (UptimeRobot / n8n workflow 03); open `<API URL>/healthz` → 200.
2. Supabase dashboard: project active (not paused).
3. Phone on hotspot; laptop on venue Wi-Fi; recorded demo video on the desktop as backup.
4. Reset the demo account (n8n workflow 08) so history is clean.
5. Open the prototype URL in a second tab as a no-backend fallback.

## Demo (60–70 s inside the pitch)
| Step | Click | Say |
|---|---|---|
| 1 | `/demo-user` → CAPTCHA tick | "One click, Bangla by default, protected against bots." |
| 2 | Scan → sample blast leaf | "Photo compressed on the phone, location rounded, metadata stripped." |
| 3 | Result | "Top-3 with calibrated confidence; the heat-map shows where it looked." |
| 4 | Advice | "Every line cites its source — no source, no advice." |
| 5 | Scan a non-leaf photo | "When it isn't sure, it says so — it never guesses a disease." |
| 6 | 🔔 Alerts | "Several nearby reports become an early warning — clearly labelled unverified and rule-based." |
| 7 | `/demo-admin` → Settings → change τ with a reason → `/audit` | "Every admin action is logged in a tamper-evident audit trail." |

## Likely judge questions (prepared answers)
- *Accuracy?* → measured macro-F1 with 95 % CI and the coverage at τ; explain the "not sure" rate.
- *Why not just ChatGPT on the image?* → calibration and abstention, cost, data sovereignty, citations.
- *What if an alert is wrong?* → conservative rules, cooldown, "unverified" label, in-app only, admin kill-switch.
- *What if the advice is wrong?* → advice only from cited DAE/BRRI guides; banned-pesticide block; safety lines.
- *Business model?* → PRD §7. · *Data and licences?* → `/data`. · *Security?* → `/security` (19-point checklist).
- *Scale?* → domain packs, portable hosting, language packs.
