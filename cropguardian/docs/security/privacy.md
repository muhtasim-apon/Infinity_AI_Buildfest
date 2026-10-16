# Privacy design

| Principle | Implementation |
|---|---|
| Minimisation | collect email (OTP sign-in), display name, district/upazila. No phone, no NID, no exact address. |
| Location | browser gives GPS → rounded to 2 decimals (~1 km) **on the device** before upload. Exact coordinates never leave the phone. |
| Photos | EXIF stripped client-side and again by server re-encode; guidance to photograph the leaf only (no faces). |
| Purpose-specific consent | `service` (required), `in_app_alerts` (optional). Bangla wording versioned. User photos are never used for training. |
| Access | farmer sees and exports own data (JSON) from Settings. |
| Deletion | "Delete my data" → hard delete within 7 days (n8n job). |
| Retention | originals 90 days → thumbnails. |
| Third parties | LLM receives no personal data; no SMS provider is used in this version (alerts are in-app). |
| Logs | request logs carry user id hash, never email or coordinates; 14-day retention. |
| Demo | demo accounts contain synthetic data only. |

Consent text (Bangla first) lives in `apps/web/i18n/bn.json` keys `consent.*`.
