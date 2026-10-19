# v0.7.0

## Stable release

- Promote the tested Tankerkönig, Petromap, and Nakordoni integration features
  to stable, including automatic provider selection, country/market-aware
  fallback, cooldowns, quota and Trip Pass diagnostics, and error handling.
- Keep Nakordoni OAuth2-PKCE and manual API-key setup available. The OAuth
  redirect, PKCE, token exchange, storage, refresh path, and failure handling
  were statically tested; a live external callback was not performed.

## Unified local station logos

- Replace the six legacy station-brand SVGs with the matching files from the
  supplied `gasstation_logos.zip`: Aral, JET, OMV, ORLEN, Shell, and Total.
- Bundle exactly 60 normalized PNG assets from the archive in both frontend and
  integration resource trees. Duplicate files and generic `404.png`/`svg.png`
  are excluded; mislabeled JPEGs are decoded to PNG.
- Keep explicit provider aliases, proportional 32×32 card presentation, local
  resource loading, neutral unknown-brand fallback, and no runtime CDN/API
  requests.
- The archive has no per-image license. Its source was matched to the upstream
  Tankerkönig reference directory and the supplied-archive authorization is
  documented as redistribution basis, not a trademark license or endorsement.

## Installation and compatibility

- HACS remains the supported installation path; the Lovelace resource is
  registered automatically as `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.7.0`.
- Existing Config Entries, provider priorities, manual API keys, cooldowns,
  HVO100 restrictions, and migration behavior remain compatible.
