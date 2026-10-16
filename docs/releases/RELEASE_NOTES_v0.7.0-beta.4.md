# Mobile Fuel Stations v0.7.0-beta.4

This local candidate fixes the coordinator cache/cooldown boundary identified
after v0.7.0-beta.3. It does not change provider HTTP adapters or productive
Home Assistant configuration.

- Track whether the current provider/query has a validated result separately
  from historical request and success timestamps.
- Do not turn an invalidated or missing cache into a successful `0` during the
  provider cooldown.
- Keep genuine empty provider responses as an available `0` result.
- Keep valid station data visible and stale during transient provider errors.
- Preserve provider-scoped cache invalidation, cooldown timing, and request
  deduplication.

Release validation is intentionally local-only for this candidate. No merge,
tag, GitHub release, HA change, VM change, provider switch, or live API call
was performed.
