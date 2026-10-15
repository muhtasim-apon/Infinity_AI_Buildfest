# User journeys

## J1 — Farmer scans a sick leaf (happy path)
1. Opens app (home-screen icon) → Bangla home: big "📷 পাতার ছবি তুলুন".
2. Takes photo → quality hint if dark/blurry → "পাঠান" (send).
3. If server waking: "সার্ভার চালু হচ্ছে… ছবিটি সংরক্ষিত আছে" (server waking… photo saved).
4. Result: disease name (bn), confidence band (উচ্চ/মাঝারি), heat-map, top-3 expandable.
5. Advice card: what to do today, steps, dose + safety, source; 🔊 listen.
6. Saved to history; optional "notify me of outbreaks nearby".

## J2 — Farmer, uncertain result
4'. "নিশ্চিত নই — কৃষি কর্মকর্তার কাছে পাঠানো হয়েছে" + expected response time + general safe steps
   (isolate, don't spray blindly). Notification when an agronomist answers.

## J3 — Farmer, offline in field
2'. No network → photo queued (badge "1 অপেক্ষমাণ") → auto-sends later.

## J4 — Agronomist reviews
`/app/review` → card with photo, model top-3, field info (crop, variety, stage) → Confirm / Correct
(choose disease) / Unclear + note → next card.

## J5 — Outbreak alert
System drafts alert (3+ reports within 5 km / 7 days) → agronomist sees map + reports → edits Bangla
message → Approve → farmers in radius get in-app (+ SMS/Telegram if subscribed).

## J6 — Admin
`/admin` → thresholds (τ, outbreak radius/min reports) with audit note required → model versions
(activate/rollback) → KB documents (add/retire) → users/roles.

## J7 — Judge
`/demo-user` → J1 with fixtures → `/demo-admin` → J4, J5, J6 → `/architecture`, `/data`, `/security`, `/audit`.
