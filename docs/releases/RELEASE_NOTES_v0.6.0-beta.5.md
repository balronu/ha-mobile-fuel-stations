# Mobile Fuel Stations v0.6.0-beta.5

## Startup GPS recovery

- Retry missing startup GPS after approximately 3, 10, and 30 seconds, then
  every 60 seconds until valid GPS is available or the integration unloads.
- React to both `EVENT_STATE_CHANGED` and GPS attribute-only
  `EVENT_STATE_REPORTED` updates.
- Deduplicate recovery triggers and keep Home Assistant Core's normal
  15-minute polling and movement refresh lifecycle unchanged.
- Apply bounded exponential backoff with jitter to temporary provider errors,
  while respecting `Retry-After` and provider rate limits.
- Preserve valid cached stations as stale during temporary failures and stop
  recovery for permanent authentication/configuration failures.
- Extend diagnostics without exposing GPS coordinates, credentials, or tokens.

## Validation and known limitation

Python tests, frontend Vitest, TypeScript, and production build are required
gates for this branch. A real Home Assistant restart test is still not
performed; no HA restart, deployment, merge, or release is included here.
