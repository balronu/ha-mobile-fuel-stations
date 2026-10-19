# v0.7.1

## Stable hotfix

- Fix Lovelace editor discovery for integration-owned overview sensors whose
  Home Assistant state is `unavailable` or `unknown` and therefore lacks the
  usual integration attributes.
- Centralize overview discovery across the card, editor, stub configuration,
  and entity suggestions.
- Preserve multiple Config Entries, entry-order independence, disabled-entity
  safety, foreign-sensor exclusion, and direct YAML entity IDs.
- Keep the automatically registered Lovelace resource at
  `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.7.1`.
- This release contains no live provider API request or OAuth callback test.
