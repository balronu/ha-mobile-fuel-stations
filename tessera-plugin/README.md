# Mobile Fuel Stations for Tessera (development prototype)

This **unreleased** Tessera plugin shows the nearest and cheapest station from the existing Home Assistant [Mobile Fuel Stations](https://github.com/balronu/ha-mobile-fuel-stations) integration.

**Requires:** Tessera development version with plugin API 0.24 and Mobile Fuel Stations installed in Home Assistant.

## Architecture

The plugin reads the Mobile Fuel Stations overview sensor's `nearest_station`, `cheapest_station`, `station_count` and `data_stale` attributes. It does **not** call Tankerkönig, Petromap or Nakordoni directly and never accesses provider credentials. All API quotas and GPS updates remain controlled by Home Assistant.

## Set up

This is an unreleased development plugin. Do not install it on a production screen until the stricter preview is clean, the generated images have been reviewed, and a standalone plugin repository is available.

## Prototype usage

This folder is currently embedded in the HA integration repository for review; it is **not yet a standalone installable Tessera repository**. The Tessera plugin manager's **Add with a link** expects a repository with the plugin manifest at its root. To test without a separate repository, copy this folder to `/config/tessera-plugins/mobile_fuel_stations/` and use Tessera's local-folder workflow. Do not install on the production display before manifest validation and preview builds pass.

In Tessera's layout editor, choose the `Nearby Stations` **overview sensor** (not a station-slot sensor). The tile maps the two nested station objects into eight scalar fields using Tessera's manifest `fields` support. No changes to HA entity IDs or integrations are required.

## Known limitations / release gates

- The tile's entity picker offers all sensors; the user must choose the Mobile Fuel Stations overview entity.
- The current `station_attributes()` serializer was checked: it exposes `station_name`, `price`, `distance`, and `currency`. The overview sensor exposes `nearest_station` and `cheapest_station`. The Tessera field mapper places the eight scalar values under the incoming `attributes` object; the tile reads them from there. Verify the mapped values in the rendered fixture and on a real screen.
- Tessera's entity data payload is capped at about 2.6 KB. If the large overview sensor payload is rejected, introduce an optional compact read-only entity on the HA integration side **in a separate reviewed PR**, not a breaking change.
- Test on small/medium/large screens, light/dark themes, missing/unknown/unavailable entities, currency and price age, no-data and stale cases.
- The official Tessera manifest checker and one host firmware preview build passed in GitHub Actions run #41792568952 (12 images, with a grid-fit warning). A stricter Guition preview and visual inspection remain release gates.
- Do not enable manual provider refresh, navigation or price submission in the initial read-only beta.
- Plugin lifecycle is separate from the HA integration's Stable releases; never remove a HA Stable release.
