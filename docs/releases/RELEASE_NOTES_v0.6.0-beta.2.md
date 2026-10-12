# Mobile Fuel Stations v0.6.0-beta.2

## Startup recovery

Beta.2 closes the Home Assistant startup race observed when the configured GPS
tracker was temporarily unavailable. After the initial coordinator refresh,
the current tracker state is checked again. If the tracker is already valid,
exactly one deduplicated recovery refresh is scheduled; movement thresholds,
cooldown, and regular 15-minute polling remain unchanged.

Missing GPS and a provider failure before the first result now produce an
unavailable overview. A numeric `0` is reserved for a completed provider
search that returned no stations. Existing in-memory station data remains
visible as stale during transient provider failures. Recovery tasks and the
tracker listener are cleaned up during unload.

## Brand assets

Beta.2 enables the existing safe brand lookup for new cards by default and
continues to respect `show_brand_logos: false`. Six sanitized SVG assets are
bundled for Aral, Shell, JET, TotalEnergies, ORLEN, and OMV. Their sources,
hashes, and residual trademark risks are documented in `BRAND_LOGOS.md`.
Unresolved brands, missing files, unsafe paths, and image-load failures use the
gas-pump icon; user-owned local SVG overrides remain supported.

## Validation

The real HA restart/edge/iOS smoke test remains outstanding. Release readiness
requires the full local and GitHub CI matrix to pass and a separate release
approval. No HA reload, restart, VM104 change, tag, or release is performed by
this development task.
