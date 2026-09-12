# Model Card — Bangla NLU (Intent, ASR, TTS)

**Status:** Specification (not trained) · **Risk tier:** Medium
**Pack:** core · **Code:** `ml/models/bangla_nlu/`

---

## Intended use

Power the **voice-first path** for users who cannot comfortably read: speech recognition
for Bangla, intent classification over financial commands, slot extraction (amount,
recipient, urgency), and speech synthesis for confirmations and IVR.

This is the accessibility layer. For a meaningful share of recipients — older, with
limited literacy — it is not a convenience feature, it is the only usable interface.

## Out-of-scope use

- Not for authentication. **Voice is not a credential** in this system; voice cloning is
  cheap and the users are exactly those who would be targeted.
- Not for open-ended conversation. The intent surface is a closed, audited set.
- Not for transcribing calls without explicit consent.

## Training data

Bangla speech **stratified by region** — Dhaka, Chittagong, Sylhet, Rajshahi, Khulna,
Barisal, Rangpur, Mymensingh — plus age bands and gender, with financial vocabulary in
the words people actually use rather than formal register.

> The dominant failure of Bangla ASR products is training on Dhaka-standard broadcast
> speech and then failing on a Sylheti grandmother — who is precisely the user the voice
> interface exists for. Regional coverage is a requirement, not an enhancement.

Recorded with informed consent; anonymised; stored in-boundary.

## Evaluation

| Metric | Target |
|---|---|
| ASR word error rate, per region | ≤ 0.15 **each** |
| Intent F1, per region | ≥ 0.88 **each** |
| Amount slot exact match | ≥ 0.98 |
| TTS naturalness MOS | ≥ 4.0 |

**Per-region gates, never an average.** An average WER of 0.12 is fully compatible with
one region at 0.30, and that region's users would find the product unusable while the
dashboard looked healthy.

Additional strata: age band (60+ reported separately), gender, background-noise level.

## Known limitations

1. Code-switching (Bangla with embedded English financial terms — "balance", "send") is
   common and hard; explicitly included in training.
2. Numerals are ambiguous in speech: *lakh* and *hazar* conventions, plus Bengali and
   Arabic digit names. **Every voice-captured amount is read back for confirmation before
   any money moves.** No exceptions.
3. Noisy environments (markets, agent points) degrade accuracy materially.
4. Very old voices and atypical speech are under-represented in available corpora.

## Ethical considerations

- **Confirmation is mandatory.** Any amount or recipient captured by voice is read back
  and confirmed before execution. A misheard amount is a direct financial loss.
- A misrecognition must never silently execute the model's best guess.
- Voice recordings are retained only as long as needed for the transaction and for
  dispute resolution, and users are told this in Bangla at first use.
- An escape hatch to a human agent is always present and reachable without literacy.

## Maintenance

Continuous collection with consent; quarterly retraining; per-region monitoring with
rollback if any region falls below gate.
