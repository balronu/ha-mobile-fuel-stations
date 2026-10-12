# Mobile Fuel Stations v0.6.0-beta.1

## Highlights

- Opt-in, provider-independent station brand resolution from the existing
  `brand` attribute.
- Supported aliases: Aral, Shell, Esso, JET, Total/TotalEnergies, HEM,
  AVIA, ORLEN, OMV, Q1, and Raiffeisen.
- New `show_brand_logos` and `logo_path` card options.
- User-owned local PNG logos in station rows and nearest/cheapest highlight
  cards with accessible alt text, bounded aspect-ratio-safe layout, and reliable
  gas-pump fallback on unknown brands or image errors.
- Unsafe/external paths and provider-derived filenames are rejected.
- Config-entry setup now survives a temporarily unavailable GPS tracker or a
  transient provider startup error. When the tracker becomes valid, one
  event-driven refresh is scheduled automatically; existing periodic,
  movement, cooldown, and stale-data behavior remains in place.

The identified cause was that a failed first coordinator refresh aborted
config-entry platform setup, while the position listener ignored the first
valid GPS state because no movement baseline existed yet. The fix keeps the
coordinator setup alive with an empty result and schedules the first valid
position refresh exactly once.

## Important rights boundary

No third-party fuel-station logo artwork is included. The reference projects'
MIT licenses cover their code, not automatically their logo image assets or
trademark rights. Users must provide and legally clear their own files under
`/config/www/fuel-logos/`, exposed to Home Assistant as `/local/fuel-logos/`.

## Compatibility and limitations

- `show_brand_logos` defaults to `false`; existing v0.5.1 dashboards continue
  to render with the gas-pump icon.
- No external CDN, automatic download, or automatic HACS logo installation is
  performed.
- Stable `v0.5.1` remains unchanged and is not replaced by this beta.
- No productive Home Assistant installation, reload, or restart was used for
  this release.
- The startup-recovery cause is covered by automated tests. A real HA restart
  on VM104 was not performed, so production restart behavior remains an
  explicit beta limitation.
