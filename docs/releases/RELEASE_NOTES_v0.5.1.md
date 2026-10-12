# Mobile Fuel Stations v0.5.1

## Highlights

- Responsive card layout using container queries.
- Single-column station list for narrow cards and mobile dashboards.
- Display of the actual data source used for station data.
- Explicit stale-data states with automatic recovery when data becomes available.
- Improved provider/runtime error diagnosis.
- Idempotent custom-element registration plus a one-shot browser `load`-event
  fallback for frontend registry/load-order races.

## Compatibility and limitations

- Existing config entries, credentials, entities, dashboard configuration, and
  local branding remain compatible.
- A full Home Assistant restart is required after installation so the
  integration can register the versioned frontend URL. No HA reload or restart
  was performed as part of publishing this release.
- The sporadic loading issue observed with Microsoft Edge and iOS Companion has
  not yet been conclusively verified in the production Home Assistant
  environment and is not claimed as fully fixed.
- Known `npm audit` warnings remain in development dependencies: two critical
  and one moderate finding. No unreviewed major upgrade was introduced.
