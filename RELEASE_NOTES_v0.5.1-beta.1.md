# Mobile Fuel Stations v0.5.1-beta.1

## Highlights

- Responsive card layout using container queries.
- Single-column station list for narrow cards and mobile dashboards.
- Display of the actual data source used for station data.
- Explicit stale-data states with automatic recovery when data becomes available.
- Improved provider/runtime error diagnosis.
- Idempotent custom-element registration plus a one-shot browser `load`-event
  fallback for frontend registry/load-order races.

## Validation and compatibility

- Stable `v0.5.0` remains unchanged and is still the recommended production
  version.
- Existing config entries, credentials, entities, dashboard configuration, and
  local branding remain compatible.
- HACS installs the selected GitHub release; this is a pre-release and is not
  installed automatically. In HACS, enable pre-release versions or select
  `v0.5.1-beta.1` explicitly from the repository's versions.
- A full Home Assistant restart is required after installation so the
  integration can register the versioned frontend URL. No HA reload or restart
  was performed as part of publishing this release.

## Known limitations

The sporadic loading issue observed with Microsoft Edge and iOS Companion has
not yet been verified in the production Home Assistant environment. The beta
is therefore a controlled test candidate, not a claim of production-runtime
verification.

Development-only `npm audit` warnings remain: two critical and one moderate
finding in transitive development dependencies. No unreviewed major upgrade
was introduced for this beta.
