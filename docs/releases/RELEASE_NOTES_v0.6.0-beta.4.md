# Mobile Fuel Stations v0.6.0-beta.4

## Coordinator polling lifecycle fix

- Fix a method-name collision with Home Assistant Core that prevented the
  normal 15-minute `DataUpdateCoordinator` polling timer from being scheduled
  and rescheduled correctly.
- Delegate coordinator shutdown to Home Assistant Core after cleaning up the
  integration's GPS listener and movement-recovery task.
- Improve polling diagnostics by reporting UNKNOWN while Core has temporarily
  cleared its callback during an in-flight refresh.
- Add regression coverage for six listeners, three regular provider poll
  cycles after an initial GPS miss, scheduler preservation, cleanup, and
  diagnostics.
- Provider selection, GPS recovery, stale-data behavior, frontend behavior,
  and bundled brand logos remain unchanged.

## Validation and known limitation

Frontend Vitest, TypeScript, the production build, Python tests, HA-Core
compatibility checks, Hassfest, and secret scanning are required gates for the
release. A real Home Assistant restart test remains outstanding and is not
performed by this release workflow.
