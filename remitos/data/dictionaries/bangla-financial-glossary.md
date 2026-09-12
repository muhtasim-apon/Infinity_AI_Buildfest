# Bangla Financial Glossary

Reviewed by native speakers. **Not machine-translated** (ADR 0012).

The failure this file prevents: literal translation produces English-in-Bengali-script
that is grammatically valid and that no Bangladeshi actually uses when talking about
money. A user who reads it understands the words and not the sentence - which on a
confirmation screen reads as a product that was not built for them.

| Concept | Term to use | Never use | Note |
|---|---|---|---|
| Landed amount | যত টাকা পৌঁছাবে | অবতরণ পরিমাণ | Say what it means, not a calque |
| Exchange rate | বিনিময় হার | - | Standard and well understood |
| Transfer fee | পাঠানোর খরচ | স্থানান্তর ফি | Plain words beat register |
| Cash out | টাকা তোলা | নগদীকরণ | What people say at the agent point |
| Under review | যাচাই করা হচ্ছে | পর্যালোচনাধীন | Formal register alarms people |
| Wallet balance | হিসাবে আছে | ওয়ালেট ব্যালেন্স | - |
| Agent point | এজেন্টের দোকান | এজেন্ট পয়েন্ট | "Shop" is what it actually is |
| Split transfer | ভাগ করে পাঠানো | বিভক্ত লেনদেন | Journey J3 |
| Daily limit | দিনের সীমা | দৈনিক সীমাবদ্ধতা | - |

**Numerals:** Bengali digits (১২৩) are user-selectable and default on.
**Grouping:** lakh/crore - ১,২০,০০০, never ১২০,০০০. See `bdt_formatter.dart`.

Stub - to be completed and reviewed in Phase 2.
