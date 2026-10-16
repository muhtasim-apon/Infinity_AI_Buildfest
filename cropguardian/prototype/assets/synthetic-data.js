/* SYNTHETIC DEMO DATA — invented for the clickable prototype.
   Not real farmers, not real diagnoses, not model output. No model exists yet.
   Probabilities below are illustrative values chosen by hand to show UI states. */
window.CG_SYNTHETIC = {
  diseases: {
    healthy:               { bn: "সুস্থ পাতা", en: "Healthy" },
    bacterial_leaf_blight: { bn: "ব্যাকটেরিয়াজনিত পাতা পোড়া", en: "Bacterial leaf blight" },
    brown_spot:            { bn: "বাদামী দাগ", en: "Brown spot" },
    narrow_brown_spot:     { bn: "সরু বাদামী দাগ", en: "Narrow brown spot" },
    blast:                 { bn: "ব্লাস্ট", en: "Blast" },
    sheath_blight:         { bn: "খোল পোড়া", en: "Sheath blight" },
    tungro:                { bn: "টুংরো", en: "Tungro" }
  },

  // Advice text in these scenarios is SAMPLE COPY to show layout. It is not agronomic advice.
  // In the real app, advice is generated only from cited DAE/BRRI/BARI sources (ADR 0006).
  sampleAdviceNote: {
    bn: "নমুনা লেখা — কৃষি পরামর্শ নয়। আসল অ্যাপে পরামর্শ শুধু উল্লেখিত উৎস থেকে আসবে।",
    en: "Sample text — not agronomic advice. In the real app, advice comes only from cited sources."
  },

  scenarios: {
    // A confident case (UI state: diagnosed, band high)
    blast: {
      status: "diagnosed", band: "high",
      top3: [["blast", 0.93], ["brown_spot", 0.04], ["narrow_brown_spot", 0.02]],
      heat: { cx: 58, cy: 46, r: 18 },
      advice: {
        summary: {
          bn: "পাতায় চোখের মতো দাগ ব্লাস্ট রোগের লক্ষণ হতে পারে। দেরি না করে ব্যবস্থা নিন।",
          en: "Eye-shaped spots on the leaf may indicate blast. Act without delay."
        },
        steps: {
          bn: ["আক্রান্ত জমিতে ইউরিয়া সার আপাতত বন্ধ রাখুন।", "জমিতে পানি ধরে রাখুন।", "উৎস নির্দেশিকা অনুযায়ী অনুমোদিত ছত্রাকনাশক ব্যবহারের আগে কৃষি কর্মকর্তার পরামর্শ নিন।"],
          en: ["Pause urea application on the affected plot.", "Keep water standing in the field.", "Consult your agriculture officer before using any approved fungicide listed in the source guide."]
        },
        safety: {
          bn: "কীটনাশক/ছত্রাকনাশক ব্যবহারে মাস্ক ও গ্লাভস পরুন, শিশুদের দূরে রাখুন।",
          en: "Wear a mask and gloves when spraying; keep children away."
        },
        chemical: null,
        citations: [{ title: "[SAMPLE CITATION — KB not yet ingested]", publisher: "BRRI", page: "—" }]
      }
    },
    // A medium-confidence case
    tungro: {
      status: "diagnosed", band: "medium",
      top3: [["tungro", 0.78], ["bacterial_leaf_blight", 0.12], ["healthy", 0.05]],
      heat: { cx: 40, cy: 55, r: 26 },
      advice: {
        summary: { bn: "হলুদ-কমলা রঙের পাতা টুংরো রোগের লক্ষণ হতে পারে। এটি পাতাফড়িং দ্বারা ছড়ায়।", en: "Yellow-orange leaves may indicate tungro, spread by leafhoppers." },
        steps: {
          bn: ["আক্রান্ত গাছ তুলে মাটিতে পুঁতে ফেলুন।", "জমিতে পাতাফড়িং আছে কিনা দেখুন।", "কৃষি কর্মকর্তাকে জানান।"],
          en: ["Uproot and bury infected plants.", "Check the field for leafhoppers.", "Inform your agriculture officer."]
        },
        safety: { bn: "ব্যবস্থা নেওয়ার আগে নিশ্চিত হোন।", en: "Confirm before taking chemical action." },
        chemical: null,
        citations: [{ title: "[SAMPLE CITATION — KB not yet ingested]", publisher: "DAE", page: "—" }]
      }
    },
    // The model declines (UI state: "not sure" — retake tips + local office card)
    unsure: {
      status: "not_sure", band: "low",
      top3: [["brown_spot", 0.41], ["narrow_brown_spot", 0.33], ["blast", 0.14]],
      heat: null, advice: null
    }
  },

  history: [
    { id: "S-1042", date: "2026-10-14", disease: "blast", status: "diagnosed" },
    { id: "S-1037", date: "2026-10-11", disease: null, status: "not_sure" },
    { id: "S-1029", date: "2026-10-06", disease: "healthy", status: "diagnosed" },
    { id: "S-1011", date: "2026-09-28", disease: "tungro", status: "diagnosed" }
  ],

  alerts: [
    { id: "A-7", disease: "blast", area: { bn: "সাভার (৫ কিমি)", en: "Savar (5 km)" }, reports: 6, risk: "high", status: "published", date: "2026-10-15", x: 58, y: 42 },
    { id: "A-6", disease: "tungro", area: { bn: "আশুলিয়া (৫ কিমি)", en: "Ashulia (5 km)" }, reports: 3, risk: "medium", status: "published", date: "2026-10-12", x: 30, y: 30 },
    { id: "A-8", disease: "bacterial_leaf_blight", area: { bn: "ধামরাই (৫ কিমি)", en: "Dhamrai (5 km)" }, reports: 3, risk: "low", status: "dismissed", dismissReason: { bn: "একই খামারের পুনরাবৃত্ত ছবি", en: "repeated photos from one farm" }, date: "2026-10-16", x: 22, y: 66 }
  ],

  users: [
    { name: "ডেমো কৃষক (Synthetic)", role: "farmer", upazila: "Savar" },
    { name: "Demo Admin (Synthetic)", role: "admin", upazila: "—" }
  ],

  counts: { scans_7d: 128, abstained_7d: 19, alerts_published_7d: 2, alerts_dismissed_7d: 1 }
};
