# Mobile Fuel Stations v0.8.4-beta.1

## Pre-release

This beta adds three Lovelace presentation modes:

- **Detailed**: all available station information with reduced unnecessary spacing.
- **Compact**: the v0.8.3 dense station-row presentation.
- **Individual**: per-card layout, sorting, visible-count, header, station-field,
  density, divider, and navigation choices.

The Individual editor offers a simple list, highlights plus list, and a
configured list. The nearest/cheapest priority is computed once and shared by
all layouts. If one station is both nearest and cheapest, it receives both
labels and is rendered once.

## Settings boundary and migration

Provider selection, location, radius, fetched station count, fuels actually
requested, polling, movement, cooldown, cache, credentials, and fetch mode
remain integration settings. Display mode, card sorting, price-sorting fuel,
visible station count, header, station fields, density, dividers, and highlight
layout are card settings. Existing integration sort values remain a legacy
fallback when a card does not specify its own sort.

Existing Config Entries, entity IDs, unique IDs, YAML cards, and storage cards
remain compatible. No stored card migration is required.

## Frontend update behavior

The resource URL is versioned with `?v=0.8.4-beta.1`; registration is
idempotent and does not accumulate duplicate resources or custom elements.
Home Assistant cannot safely replace an already executed ES module in an open
browser tab, so one dashboard reload may still be required after an update.
The beta intentionally does not implement an automatic hard-reload loop.

## Scope

Tests use isolated fixtures and mocks. No productive Home Assistant, VM 104,
dashboard, Config Entry, provider, OAuth, credential, quota, or backup state
is changed. Live provider/OAuth and Companion-App validation are not implied.
