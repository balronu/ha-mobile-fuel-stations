# v0.7.0-beta.8

## Logo hotfix

- Bump the integration resource URL from `v=0.6.0` to `v=0.7.0-beta.8` to
  invalidate stale Home Assistant browser and frontend-resource caches.
- Resolve the reported `Eni (Agip Eni)` station name to `agip-eni.png` and
  `OIL! Tankstelle Sulzbach` to `oil.png` using explicit aliases.
- Keep all 60 local assets and the neutral fallback; no CDN or additional API
  requests are introduced.
- Add regression coverage for every bundled local resource path and the exact
  reported station names.

## OAuth static QA

- Keep the redirect URI at `https://my.home-assistant.io/redirect/oauth`.
- Continue using Home Assistant's PKCE helper for code exchange, Config Entry
  token storage, and refresh-token grants without a client secret.
- Bound the options callback at 30 seconds, require a positive `expires_in`,
  and distinguish timeout and token-exchange failures.
- No live OAuth authorization was initiated; external callback reachability
  remains a live deployment prerequisite.

## Compatibility and rights

- Providers, priorities, fallbacks, cooldowns, existing Config Entries, manual
  API keys, and HVO100 behavior remain unchanged.
- The 60 local assets and their source/rights caveats remain documented; this
  release does not imply a trademark license or endorsement.
