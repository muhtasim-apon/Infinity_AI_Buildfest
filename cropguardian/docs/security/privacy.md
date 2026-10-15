# Privacy design

| Principle | Implementation |
|---|---|
| Minimisation | collect phone (OTP) or email, display name, district/upazila. No NID, no exact address. |
| Location | browser gives GPS → rounded to 2 decimals (~1 km) **on the device** before upload. Exact coordinates never leave the phone. |
| Photos | EXIF stripped client-side and again by server re-encode; guidance to photograph the leaf only (no faces). |
| Purpose-specific consent | `service` (required), `training_use` (optional, default off), `sms_alerts` (optional). Bangla wording versioned. |
| Access | farmer sees and exports own data (JSON) from Settings. |
| Deletion | "Delete my data" → hard delete within 7 days (n8n job). |
| Retention | originals 90 days → thumbnails, unless labelled with training consent. |
| Third parties | LLM receives no personal data; SMS provider receives phone + alert text only. |
| Logs | request logs carry user id hash, never phone or coordinates; 14-day retention. |
| Demo | demo accounts contain synthetic data only. |

Consent text (draft, Bangla first) lives in `apps/web/src/i18n/bn.json` keys `consent.*`.
