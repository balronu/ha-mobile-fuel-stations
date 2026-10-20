# Mobile Fuel Stations v0.8.3 — Unified station prioritization

## Change

v0.8.3 gives the compact and detailed Lovelace views one shared, pure frontend
prioritization function. The nearest station is always first, followed by the
distinct cheapest station for the configured price-sorting fuel. If one station
wins both comparisons it appears once with both accessible labels. Remaining
stations follow the configured distance/price order with deterministic tie-breaks.

The detailed view is now one complete station list; the former separate nearest
and cheapest highlight cards are not rendered. Compact spacing, navigation,
multi-fuel prices, existing YAML cards, providers, fetch modes and backend
station data remain compatible. Overview metadata now exposes the existing
`sort_mode` and `sort_fuel` options so the frontend can apply the same contract.

## Verification

- Shared prioritization and component regression tests cover distance/price modes,
  same-station labels, missing values, fuel selection, provider-neutral data,
  both display modes, navigation, accessibility labels and no service calls.
- Frontend tests and production bundle were rebuilt on the candidate tree.
- Python, Hassfest, syntax and secret-scan checks are required in CI.
- No live provider/OAuth call, productive Home Assistant, dashboard, Config
  Entry, credential, backup or VM 104 change was made.
