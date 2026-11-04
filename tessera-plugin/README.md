# Mobile Fuel Stations for Tessera (development prototype)

This **unreleased** Tessera plugin shows the nearest and cheapest station from the existing Home Assistant [Mobile Fuel Stations](https://github.com/balronu/ha-mobile-fuel-stations) integration.

**Requires:** Tessera development version with plugin API 0.24 and Mobile Fuel Stations installed in Home Assistant.

## Architecture

The plugin reads the Mobile Fuel Stations overview sensor's `nearest_station`, `cheapest_station`, `station_count` and `data_stale` attributes. It does **not** call Tankerkönig, Petromap or Nakordoni directly and never accesses provider credentials. All API quotas and GPS updates remain controlled by Home Assistant.

## Prototype usage

This folder is currently embedded in the HA integration repository for review; it is **not yet a standalone installable Tessera repository**. The Tessera plugin manager's **Add with a link** expects a repository with the plugin manifest at its root. To test without a separate repository, copy this folder to `/config/tessera-plugins/mobile_fuel_stations/` and use Tessera's local-folder workflow. Do not install on the production display before manifest validation and preview builds pass.

In Tessera's layout editor, choose the `Nearby Stations` **overview sensor** (not a station-slot sensor). The tile maps the two nested station objects into eight scalar fields using Tessera's manifest `fields` support. No changes to HA entity IDs or integrations are required.

## Known limitations / release gates

- The tile's entity picker offers all sensors; the user must choose the Mobile Fuel Stations overview entity.
- The current `station_attributes()` serializer was checked: it exposes `station_name`, `price`, `distance`, and `currency`. The overview sensor exposes `nearest_station` and `cheapest_station`. Confirm that Tessera's field mapper delivers those eight values at the top level in a preview build.
- Tessera's entity data payload is capped at about 2.6 KB. If the large overview sensor payload is rejected, introduce an optional compact read-only entity on the HA integration side **in a separate reviewed PR**, not a breaking change.
- Test on small/medium/large screens, light/dark themes, missing/unknown/unavailable entities, currency and price age, no-data and stale cases.
- Run Tessera `tools/check.py`, `tools/preview.py` and firmware builds before releasing. No tests have been claimed as passed yet.
- Do not enable manual provider refresh, navigation or price submission in the initial read-only beta.
- Plugin lifecycle is separate from the HA integration's Stable releases; never remove a HA Stable release.
