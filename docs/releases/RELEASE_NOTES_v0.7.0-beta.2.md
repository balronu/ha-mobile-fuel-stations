# Mobile Fuel Stations v0.7.0-beta.2

This pre-release adds a protected Nakordoni diagnostic path without changing
the productive provider mode, coordinator, station cache, sensor state, or
Home Assistant config entries.

- Added the administrator-only `mobile_fuel_stations.probe_nakordoni` service.
- Added one-request Nakordoni diagnostics using existing HA API-key or OAuth2
  credentials, with no automatic retry and same-entry concurrency protection.
- Added redacted HTTP/status, quota, latency, station/price count, price-age,
  and coverage results including empty-result hints.
- Preserved legacy API-key installations and automatic provider selection.
- Nakordoni OAuth remains experimental; a real Nakordoni OAuth login and live
  provider response were not verified in this release preparation.

Validation: Python 3.14.2 / Home Assistant 2026.10.1 tests, frontend tests and
build, Hassfest, syntax validation, and secret scanning passed on the release
candidate commit.
