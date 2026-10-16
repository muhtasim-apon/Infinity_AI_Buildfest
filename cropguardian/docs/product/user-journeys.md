# User journeys

## J1 — Farmer scans a sick leaf (happy path)
1. Opens the app (home-screen icon) → Bangla home: big "📷 পাতার ছবি তুলুন".
2. Takes a photo → quality hint if dark/blurry → "পাঠান" (send).
3. If the server is waking: "সার্ভার চালু হচ্ছে… ছবিটি সংরক্ষিত আছে" (server waking… photo saved).
4. Result: disease name (bn), confidence band (উচ্চ/মাঝারি), heat-map, top-3 expandable.
5. Advice card: what to do today, steps, dose + safety, source; 🔊 listen.
6. Saved to history; optional "show alerts near me" (in-app).

## J2 — Farmer, uncertain result
4'. "নিশ্চিত নই" (not sure): no disease is named as the answer; retake tips (one leaf, close, daylight);
   "do not spray on a guess"; static card: "contact your Upazila Agriculture Office". The farmer can
   retake immediately.

## J3 — Farmer, offline in the field
2'. No network → photo queued (badge "১ অপেক্ষমাণ") → sent automatically when online.

## J4 — Automatic outbreak alert
Three or more confident diagnoses of the same notifiable disease within 5 km / 7 days → the system
publishes an in-app alert labelled "possible outbreak — unverified, rule-based" (risk, area, report
count) → farmers nearby see it under 🔔 → the team gets a notice in its Telegram channel → if the alert
looks wrong, the admin dismisses it with a reason (audited).

## J5 — Admin
`/admin` → thresholds (τ, outbreak radius / minimum reports / window / cooldown) with a required
reason → model versions (activate / roll back) → KB documents (add / retire) → users and roles →
dismiss an alert. Every action appears in `/audit`.

## J6 — Judge
`/demo-user` (CAPTCHA) → J1 with sample photos → J2 with a non-leaf photo → `/demo-admin` → J5 →
`/architecture`, `/data`, `/security`, `/audit`.
