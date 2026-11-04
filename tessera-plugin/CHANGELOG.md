# Changelog

## 0.1.0 - 2026-11-04
- Initial read-only Tessera highlights tile prototype for Home Assistant Mobile Fuel Stations.
- Responsive 1x1 to 4x4 tile with nearest and cheapest station names, prices, distance and stale-state indicator.
- Official Tessera detail card with address, opening status, price age, selected-fuel view and live state refresh.
- E5, E10 and Diesel views use the overview sensor's existing `fuel_types` and `cheapest_stations_by_fuel` attributes.
- German and English translations.
- Width-aware text fitting, ellipsis instead of hard clipping, and graceful unknown/unavailable/missing-field handling.
- Offline fixtures for populated, empty, stale and multi-fuel responses plus contract assertions.
- Passed official Tessera manifest validation and strict Guition firmware preview.
- Available for test installation by linking directly to the plugin folder on the development branch; not yet a GitHub Release.
