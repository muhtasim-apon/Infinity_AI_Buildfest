# Features

Fourteen features, Clean Architecture per feature: `data/` then `domain/` then
`presentation/`. The domain layer imports nothing from the other two.

**Core feature:** `send_money/` - amount entry, route comparison led by landed amount,
and the split proposal (journey J3). See `send_money/domain/route_option.dart`.
