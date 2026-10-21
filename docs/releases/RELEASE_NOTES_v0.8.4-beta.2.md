# Mobile Fuel Stations v0.8.4-beta.2

This GitHub pre-release refines the three Lovelace card modes introduced in
beta.1. Stable users should continue using `v0.8.3`; beta versions must be
selected explicitly in HACS.

## Changes

- Individual **Highlights + list** now uses a dedicated compact tile component.
  The nearest and cheapest stations are side by side at 390 CSS pixels and
  stack only when the card container is below 359px.
- Highlight tiles keep price, distance, navigation, logos, labels, equal row
  height, and keyboard accessibility without becoming detailed station cards.
- Individual compact density now changes the station information flow, not
  only outer padding: status, distance, provider, and freshness share a
  responsive metadata row.
- The Compact mode remains the beta.1/v0.8.3 reference layout.
- The visual editor uses grouped fieldsets and `[checkbox] label` controls;
  navigation is configured once with its provider selector.
- Existing YAML and storage configurations, entity IDs, Config Entries,
  integration settings, provider requests, and legacy sort fallbacks remain
  unchanged.

## Cache/update behavior

The frontend resource is versioned as
`/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.8.4-beta.2` and the
checked-in bundle contains the same marker. Registration remains idempotent.
An already executed JavaScript module cannot be replaced safely in a live
Home Assistant tab, so one ordinary dashboard reload can still be required;
the release does not attempt a hard-reload loop or custom-element replacement.

## Verification

- Frontend: 79 Vitest tests, TypeScript, production build, and generated
  bundle synchronization passed locally.
- Python: 389 tests passed in the pinned local HA fixture environment.
- Chromium at 390 CSS pixels: Compact 444px, Detailed 477px, Individual list
  normal 439px, Individual list compact 364px, Highlights + list 346px.
  The two 390px highlight tiles are approximately 179px wide each inside the
  366px card content area; below the 359px container breakpoint they stack.
- Compileall, JSON validation, and `git diff --check` passed. Hassfest and
  secret scanning remain authoritative CI gates.

Known limitation: no live Home Assistant, provider, OAuth, VM 104, dashboard,
credential, or Companion-App test was performed.
