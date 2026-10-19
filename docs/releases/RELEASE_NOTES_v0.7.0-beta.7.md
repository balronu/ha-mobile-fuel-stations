# v0.7.0-beta.7

## Nakordoni Account Usage

- Polls the official `GET /api/v2/account/usage` endpoint no more often than every 15 minutes.
- Supports both the existing OAuth2/PKCE path and manual API-key path.
- Adds HA sensors for cheap-quota calls remaining, cheap-quota reset time, and Trip Pass state.
- Exposes documented cheap/heavy/route quotas, QPS, market allowance, Trip Pass validity, and official upgrade/pass links without tokens or raw payloads.
- Classifies `quota_exceeded`, `market_not_allowed`, and `integration_product_not_allowed` safely; no payment flow is implemented.

## Station Logos

- The supplied archive was inventoried but not published because it contains no provenance or redistribution permission.
- The audit found 66 files, 63 unique contents, three duplicate pairs, and several files with a `.png` name but JPEG encoding.
- Existing separately sourced local SVGs remain the only bundled logos. Other recognized brands use the neutral pump icon unless the user supplies a permitted local override.

## Compatibility and scope

- Tankerkönig, Petromap, and Nakordoni remain available.
- Provider priorities, fallback behavior, cooldowns, existing config entries, manual keys, and HVO100 protection remain unchanged.
- No external logo CDN, extra logo network request, payment handling, Home Assistant VM/config-entry change, merge, tag, or release is included in this development branch.
