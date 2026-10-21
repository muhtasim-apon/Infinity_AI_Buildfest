# Bangla style guide (Crop Guardian · ফসল রক্ষী)

Owner: Raisa (copy) · consumers: Sara (`cropguardian-ui`, `frontend/src/i18n/bn.json`), Raisa/Salwa
(advisory prompt, fallback cards). Source: build spec 10.10, 15.1, 15.5, 0.2.10.

> **Status: team-authored, not expert-reviewed.** Every Bangla string and every disease term below is the
> team's own wording. Disease terminology must be checked against BRRI/DAE terms once `kb/sources.yaml`
> documents are extracted (Salwa, P5), and ideally by a native-speaking agronomist before any pilot.
> Nothing here is claimed to be agronomist-approved.

## 1. Principles
1. **Bangla is the source locale.** Write `bn.json` first, then `en.json`. English is never the template.
2. **Respectful and plain.** Use "আপনি". Short everyday words; no officialese, no English words where a
   common Bangla word exists (except names: BRRI, DAE, SMS).
3. **One idea per sentence, <= 15 words** (enforced by `i18n.test.ts`). One idea per advice step.
4. **Verb first for actions:** "পাতা পরীক্ষা করুন", "আবার ছবি তুলুন", "কৃষি অফিসে যোগাযোগ করুন".
5. **Never blame, never frighten.** Errors say what to do next. Alerts avoid fear words (মহামারি, ধ্বংস,
   সর্বনাশ); use calm, factual wording ("আপনার এলাকায় ব্লাস্ট রোগের রিপোর্ট বাড়ছে").
6. **No raw percentages for farmers.** Use bands: উচ্চ নিশ্চয়তা / মাঝারি নিশ্চয়তা. (Staff console may show numbers.)
7. **Be honest about uncertainty.** "আমি নিশ্চিত নই" is a first-class answer. Never soften it into a guess.

## 2. Mechanics
| Topic | Rule | Example |
|---|---|---|
| Sentence end | Use the danda `।`, not `.`; `?` and `!` as usual | "ছবিটি পাঠানো হয়েছে।" |
| Numerals | Bangla digits in the bn UI (`Intl.NumberFormat('bn-BD')`); input accepts both | ৩টি পাতা |
| Dates | `১৬ অক্টোবর ২০২৬`; Bangla month names via `Intl.DateTimeFormat('bn-BD')` | |
| Time zone | Stored UTC, shown `Asia/Dhaka` | |
| Units | Spelled simply | "প্রতি লিটার পানিতে ২ গ্রাম" |
| Doses | Copied **verbatim** from the cited source; never paraphrased or rounded | |
| Disease names | Bangla first; English in brackets once on first mention | ব্লাস্ট (Blast) |
| Plurals | Bangla needs no plural form in UI; use "টি/টা/গুলো" naturally | ৩টি ছবি |
| Punctuation for voice | Keep commas and dandas; they drive text-to-speech pauses | |
| Buttons | Verb + object, no full stop | "ছবি তুলুন" |
| Action naming | The same action keeps one name through a flow | "সংরক্ষণ করুন" -> "সংরক্ষণ হয়েছে" |

## 3. Glossary (draft - verify against BRRI/DAE terminology in the KB)
| Code | Bangla (draft) | English | Notes |
|---|---|---|---|
| `healthy` | সুস্থ পাতা | Healthy leaf | |
| `bacterial_leaf_blight` | ব্যাকটেরিয়াজনিত পাতা পোড়া | Bacterial leaf blight | notifiable in our taxonomy |
| `brown_spot` | বাদামী দাগ | Brown spot | |
| `narrow_brown_spot` | সরু বাদামী দাগ | Narrow brown spot | |
| `blast` | ব্লাস্ট | Blast | notifiable |
| `sheath_blight` | খোল পোড়া | Sheath blight | notifiable |
| `tungro` | টুংরো | Tungro | notifiable |
| reviewer | পর্যালোচক | Reviewer | the human who checks unsure photos |
| agriculture office | কৃষি অফিস | Upazila agriculture office | say "স্থানীয় কৃষি অফিস" |
| not sure | আমি নিশ্চিত নই | Not sure | never "অজানা" (unknown) |
| simulated | সিমুলেটেড | Simulated | always shown with the purple badge |
| demo data | ডেমো ডেটা | Demo data | |
| alert | সতর্কতা | Alert | |

## 4. Tone by situation
- **Result (confident):** state the likely disease, the band, then what to do today. Do not say "নিশ্চিত"
  (certain) - say "উচ্চ নিশ্চয়তা" (high confidence).
- **Not sure:** calm, no red, no apology. Say why and what helps: more light, closer to one leaf, retake;
  offer the local agriculture office; say the photo went to a reviewer.
- **Not a rice leaf:** neutral, helpful: "একটি ধানের পাতার কাছ থেকে আবার ছবি তুলুন।"
- **Advice:** numbered short steps; each step carries a source chip; chemical steps carry the safety line
  ("রাসায়নিক ব্যবহারের আগে লেবেল পড়ুন এবং সুরক্ষা পোশাক পরুন।"); end with "কখন কৃষি অফিসে যাবেন".
  Always show: "প্রকাশিত BRRI/DAE নির্দেশনার ভিত্তিতে · কৃষি বিশেষজ্ঞ এখনও পর্যালোচনা করেননি".
- **Alerts:** factual, local, actionable, no fear words; always labelled SIMULATED in the demo.
- **Offline / waking server:** reassure and say what is saved ("ছবি সংরক্ষিত থাকবে").

## 5. Do / don't
| Do | Don't |
|---|---|
| "আলো বেশি এমন জায়গায় আবার ছবি তুলুন" | "ছবি খারাপ হয়েছে" (blames the user) |
| "এই ছবি থেকে সঠিক রোগ বলা যাচ্ছে না" | "রোগ অজানা" |
| "আপনার এলাকায় রিপোর্ট বাড়ছে" | "ভয়াবহ প্রাদুর্ভাব!" |
| ৩টি ধাপ | 3টি ধাপ (mixed digits) |
| ব্লাস্ট (Blast) | Blast (English only) |

## 6. Review checklist (every new string)
- [ ] In `bn.json` first, key mirrored in `en.json` (same placeholders).
- [ ] <= 15 words per sentence; ends with `।` where it is a sentence.
- [ ] No raw percentage, no fear word, no blame.
- [ ] Read aloud once; does the text-to-speech pause naturally?
- [ ] Disease/agronomy terms match the glossary (or flag `TERM-CHECK` in the PR).
- [ ] Fits the layout at 360 px (long compound words wrap, never truncate meaning).

## 7. Fluency rating protocol (P6 gate, 23 Oct)
Three team members read the advice for all 7 classes aloud and rate fluency 1-5 and "would a farmer
understand this?" yes/no. Results are recorded as **team-rated** (not expert-rated) in
`docs/RAG.md`; no fluency claim is made beyond that.
