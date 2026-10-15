# Cold-start test (Render A1) — semi-manual

1. Leave the staging API idle ≥ 16 minutes (keep-warm workflow disabled).
2. On a phone (Slow 3G throttling in Chrome DevTools remote), open `/app`, take a photo, press send.
3. Expect: "সার্ভার চালু হচ্ছে…" within 2 s; photo shown as queued; no error dialog.
4. Measure time until result appears (record in table below). Expect ≤ ~90 s total.
5. Repeat with airplane mode on during step 2 → item stays in outbox → disable airplane mode → auto-sends.

| Date | Idle (min) | Time to first byte | Time to result | Outcome |
|---|---|---|---|---|
