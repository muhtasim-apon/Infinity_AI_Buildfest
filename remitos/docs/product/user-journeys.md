# User Journeys

Four journeys. The first two carry the product; the third and fourth are where most
competitors fail and where the judging demo should spend its time.

---

## J1 — Abul sends the monthly remittance (happy path)

| Step | Screen | What matters |
|---|---|---|
| 1 | Open app | Biometric unlock; last recipient already surfaced (recommender, ADR: low-risk model) |
| 2 | Amount | Enter Tk 45,000 or "৪৫,০০০"; Bengali numerals accepted; lakh/crore grouping on display |
| 3 | **Routes** | **Three options, each showing landed BDT — not fee.** ETA with an interval. One-line Bangla reason: *"এই পথে ৳৩২০ বেশি পৌঁছাবে, ২ ঘণ্টা বেশি লাগবে"* |
| 4 | Timing hint | Optional, uncertainty-explicit, never blocking. "Send now" is at least as prominent |
| 5 | Confirm | Landed amount, ETA, total cost, incentive eligibility — on one screen, no scroll |
| 6 | Pay | Local funding method in the sending country |
| 7 | Track | Live status; Rahima receives a **Bangla voice call**, not only SMS |

**The differentiator is step 3.** Every competitor shows one price from one rail. This
screen shows the decision.

---

## J2 — Rahima receives (no smartphone, no data)

| Step | Channel | What matters |
|---|---|---|
| 1 | **IVR call in Bangla** | "আপনার ছেলে আবুল ৪৫ হাজার টাকা পাঠিয়েছেন" — spoken, Bengali numerals |
| 2 | IVR menu | 1 = hear balance · 2 = nearest agent · 3 = speak to a person |
| 3 | **Limit guidance, spoken** | "আজ এজেন্ট থেকে সর্বোচ্চ ৩০ হাজার টাকা তুলতে পারবেন" — **before she travels 40 minutes** |
| 4 | Agent visit | Agent-assisted; her PIN, agent identity logged |
| 5 | Confirmation | Spoken confirmation of the amount withdrawn |

Step 3 is the whole argument of ADR 0007, delivered by voice to someone who cannot read
it. A limit discovered at the counter after a 40-minute journey is a product failure, not
a regulatory one.

---

## J3 — The amount exceeds the cash-out limit (the journey nobody designs)

Abul sends Tk 120,000 for a medical emergency. Agent cash-out is capped at Tk 30,000/day.

**What every other product does:** quotes, accepts payment, pays to wallet, and Rahima
discovers at the counter that she can take Tk 30,000. In an emergency.

**What RemitOS does — before Abul pays:**

```
৳১,২০,০০০ পাঠাতে চান

  এই পরিমাণ একবারে তোলা যাবে না।
  নিয়ম: এজেন্ট থেকে দিনে সর্বোচ্চ ৳৩০,০০০

  আমরা যা করতে পারি:
  ┌────────────────────────────────────────┐
  │ ৳৩০,০০০  →  বিকাশ ওয়ালেট   আজই তোলা যাবে │
  │ ৳৯০,০০০  →  ব্যাংক হিসাব    আগামীকাল      │
  └────────────────────────────────────────┘
     মোট খরচ ৳৭৮০  ·  সম্পূর্ণ বৈধ

  [ এভাবে পাঠান ]   [ অন্য উপায় দেখুন ]
```

Split proposed, priced, timed, explained, and legal — communicated with icons and a voice
option for low-literacy users. No incumbent currently does this, and it demonstrates in
thirty seconds on stage that the system has read the regulation rather than just the API
docs.

---

## J4 — A transfer is held for compliance review

The highest-anxiety moment in the product. The money exists and the user cannot see it
moving.

| Step | What the user gets |
|---|---|
| 1 | Immediate notification — **never silence**. Silence is what sends people to hundi |
| 2 | **Plain-Bangla reason:** "পরিমাণ এবং হিসাবটি নতুন হওয়ায় আমরা যাচাই করছি" — not "risk score 0.73" |
| 3 | A stated SLA with a countdown, and what happens if it passes |
| 4 | What the user can do to speed it up, if anything |
| 5 | A visible appeal route to a human |
| 6 | Resolution notification on both channels |

Contrast with the incumbent experience, which is typically: nothing, then nothing, then
a customer-service queue.

---

## Accessibility requirements across all journeys

| Requirement | Standard |
|---|---|
| Bangla-first | ADR 0012 — designed in Bangla, English fits the Bangla layout |
| Voice available at every step | Bangla TTS; amounts always read back before execution |
| IVR/USSD parity for core flows | ADR 0008 |
| Contrast and target size | WCAG 2.2 AA; elder mode enlarges targets and type |
| Icon-led navigation | Every action carries an icon, not text alone |
| Low-bandwidth mode | Under 50 KB per screen |
| Offline composition | Queued with an honest "queued, not sent" state |
| Screen-reader support | Semantic labels in both languages |

The recurring principle: **the person who most needs the money is usually the person
least served by the interface.** Every journey above is designed from that end first.
