# v0.7.0-beta.7

## Nakordoni Account Usage

- Polls the official `GET /api/v2/account/usage` endpoint no more often than every 15 minutes.
- Supports both the existing OAuth2/PKCE path and manual API-key path.
- Adds HA sensors for cheap-quota calls remaining, cheap-quota reset time, and Trip Pass state.
- Exposes documented cheap/heavy/route quotas, QPS, market allowance, Trip Pass validity, and official upgrade/pass links without tokens or raw payloads.
- Classifies `quota_exceeded`, `market_not_allowed`, and `integration_product_not_allowed` safely; no payment flow is implemented.

## Station Logos

- The supplied 66-file archive is integrated as 54 normalized PNG assets. Generic `404.png`/`svg.png`, duplicate copies, and archive variants already covered by the six canonical SVGs are excluded; mislabeled JPEG files are decoded to PNG.
- The audit found 66 files, 63 unique contents, three duplicate pairs, and several files with a `.png` name but JPEG encoding.
- The exact upstream source directory is documented. The upstream repository is MIT-licensed as code but has no per-image license; explicit authorization for this branch is recorded as the redistribution basis, without claiming trademark license, endorsement, or affiliation.

## Compatibility and scope

- Tankerkönig, Petromap, and Nakordoni remain available.
- Provider priorities, fallback behavior, cooldowns, existing config entries, manual keys, and HVO100 protection remain unchanged.
- No external logo CDN, extra logo network request, payment handling, Home Assistant VM/config-entry change, merge, tag, or release is included in this development branch.
