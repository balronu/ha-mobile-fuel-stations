# Mobile Fuel Stations v0.7.0-beta.3

This pre-release is a combined hotfix release for Nakordoni response handling
and provider-result availability. It does not change the frontend component
version or productive Home Assistant configuration.

- Fix Nakordoni API-key requests by binding the aiohttp response returned from
  the request context manager before accessing headers, status, or JSON.
- Preserve successful empty provider responses as `[]` during cooldown and
  transient provider failures instead of turning them into `None`.
- Keep retained results visibly stale during temporary failures so old prices
  are not presented as current.
- Preserve provider-scoped cache invalidation when the configured provider
  changes.
- Preserve existing API-key installations, Nakordoni OAuth2 support, automatic
  provider selection, and the administrator-only
  `mobile_fuel_stations.probe_nakordoni` service.
- The Nakordoni OAuth flow remains experimental and has not been verified with
  a real live Nakordoni login.

Validation covers Python/HA and frontend tests, the production frontend build,
the Nakordoni context-manager regression, empty-result cooldown/transient
failure regressions, compileall, and diff checks. Hassfest, secret scanning,
and all final CI checks are reported from GitHub Actions for the release PR.
