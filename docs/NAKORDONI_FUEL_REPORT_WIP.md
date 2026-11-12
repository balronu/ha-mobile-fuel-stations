# Nakordoni Fuel Report – development notes (not released)

This is an **unreleased, opt-in feature** under development in PR #62. The
existing Stable v0.8.7 does not expose a price-reporting action.

Source: https://nakordoni.eu/en/developers/docs/fuel-report

## API contract

- `POST https://nakordoni.eu/api/v2/data/fuel-report`
- Same per-user Nakordoni API credential, **subject to product permissions**.
- A directory `data.stations[].id` is required. A synthetic `station_ref`
  is **not** a substitute; rows without a numeric directory ID cannot report.
- The person must enter or confirm each grade, observed price, currency and
  optionally an ISO-8601 observation timestamp with timezone.
- Observations must be no more than six hours old and not in the future.
- Limits: 30 reports/hour, 200/24h and one station+grade/30 minutes.
- `dry=true` validates without applying a price but **still consumes quota**.
- Provider responses distinguish `accepted`, `pending` (more than 15%
  difference pending independent confirmation), and `rejected` with reasons.
- No automatic submissions based on GPS, fuel-stop detection or cached prices.
- No retry on failed submissions unless the user explicitly confirms again.
- Do not log API credentials or persist submitted prices in HA diagnostics.

The initial Andrii email said at most 14 grades; the public API reference
checked on 2026-11-02 lists at most 17. The first client conservatively
enforces 14 pending contract alignment.

## Remaining work before release

1. Preserve the Nakordoni directory numeric ID through the station model,
   sensors and Lovelace serialization; never infer it from `station_ref`.
2. Add an admin-only HA action that requires explicit confirmation and
   respects the configured Nakordoni auth method (API key or OAuth2).
3. Provide an explicit, accessible DE/EN price-entry UI with confirmation and
   distinct accepted/pending/rejected outcomes.
4. Enforce sensible client-side rate-limit feedback without bypassing the
   provider's authoritative limits.
5. Validate current fuel-stations empty-result and price-age contract:
   `data.empty_reason`, `coverage`, `suggestion`, `nearest_station_km`,
   `country`, `notices`; no automatic radius enlargement. Keep existing
   `confirmed_at`-based freshness, currency separation and 90-day omission.
6. Complete fixture tests, HA service permission tests, frontend tests,
   CI/HACS/Hassfest and actual Home Assistant field validation.
7. Update README.de.md, README.en.md, HACS instructions, changelog, release
   notes and SmartCamper765 site **only after implementation is complete**.
8. Verify all 60 bundled PNG station-brand assets and branding files.
9. After Stable is verified, remove obsolete beta releases/tags as required
   by the project's Stable-only policy, preserving all Stable rollbacks.
