# Unit tests

Owner: each developer for their own code. Tools: pytest (API), Vitest (web). Run on every PR.

| ID | Unit | Case | Expected |
|---|---|---|---|
| U1 | `ScanCreateIn` | `lat_coarse = 23.851` | validation error (must be multiple of 0.01) |
| U2 | `ScanCreateIn` | crop `jute` | validation error |
| U3 | `SettingsIn` | missing `reason` | validation error |
| U4 | `SettingsIn` | τ = 0 or 1 | validation error (exclusive bounds) |
| U5 | `audit_chain.scrub` | detail with phone, email, lat/lon nested | all removed, other keys kept |
| U6 | `outbreak.haversine_km` | known coarse points | within 0.5 km of reference |
| U7 | `ratelimit.check` | 31st scan in an hour | denied with retry-after > 0 |
| U8 | web `coarsen()` | 23.85678 / 90.2649 | 23.86 / 90.26 |
| U9 | web `prepareImage()` | photo with EXIF | output JPEG has no APP1 segment; long side ≤ 1024 |
| U10 | web `prepareImage()` | dark photo | flag `dark` |
| U11 | web i18n | every key in `en.json` | exists in `bn.json` |
