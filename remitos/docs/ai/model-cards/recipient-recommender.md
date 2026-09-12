# Model Card - Recipient Recommender

**Status:** Specification (not trained) · **Risk tier:** Low
**Pack:** borderless_money · **Code:** `ml/models/recipient_recommender/`

---

## Intended use

Rank a sender's saved recipients and suggest a likely amount, so the common case - the
same person, the same amount, every month - takes two taps instead of twelve fields.

Entry error is a real cost in remittance: a mistyped account number sends money to a
stranger and is frequently unrecoverable. Reducing typing reduces that risk.

## Out-of-scope use

- Never auto-selects a recipient. It orders a list; the user chooses.
- Never pre-fills an amount without the user confirming it.
- Not used to infer relationships for any purpose other than ordering this list.

## Training data

The sender's own transfer history only. **No cross-user collaborative filtering** - one
user's recipient graph must never influence another's suggestions, because that leaks the
existence of relationships between people.

## Features

Recency, frequency, amount stability per recipient, day-of-month pattern, seasonality
(Eid, school-fee cycles), time since last transfer.

## Evaluation

| Metric | Target |
|---|---|
| Top-1 recipient accuracy | >= 0.75 |
| Top-3 recipient accuracy | >= 0.92 |
| Amount suggestion within 10 % | >= 0.70 |
| Reduction in time-to-send vs manual | >= 40 % |

## Known limitations

1. Cold start for new senders - falls back to plain recency ordering.
2. Irregular senders gain little.
3. Emergency transfers break the learned pattern by definition, which is fine: the model
   simply offers no useful suggestion rather than a wrong one.

## Ethical considerations

Recipient lists are sensitive. They reveal family structure, second households, and
financial obligations. Suggestions are rendered only on an authenticated, unlocked
session, never in a notification preview, and never in a shared-device view.

## Maintenance

Retrain monthly. Low-risk tier: drift monitoring and documented limitations only.
