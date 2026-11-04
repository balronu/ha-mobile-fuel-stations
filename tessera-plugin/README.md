# Mobile Fuel Stations for Tessera (beta test)

This **beta-stage** Tessera plugin shows the nearest and cheapest station from the existing Home Assistant [Mobile Fuel Stations](https://github.com/balronu/ha-mobile-fuel-stations) integration.

**Requires:** Tessera development version with plugin API 0.24 and Mobile Fuel Stations installed in Home Assistant.

## Architecture

The plugin reads the Mobile Fuel Stations overview sensor's `nearest_station`, `cheapest_station`, `station_count` and `data_stale` attributes. It does **not** call Tankerkönig, Petromap or Nakordoni directly and never accesses provider credentials. All API quotas and GPS updates remain controlled by Home Assistant.

## Set up

Install this read-only beta using the steps below. No additional Home Assistant template sensor is required.

### Install the beta from GitHub

This is a **development-branch beta test**, not a published GitHub Release or a Tessera community-index listing.

1. Open Tessera's **Plugins** page and choose **Add with a link**.
2. Enter the plugin folder URL: `https://github.com/balronu/ha-mobile-fuel-stations/tree/feature/tessera-display-plugin-prototype/tessera-plugin`.
3. If Tessera offers **Test a branch**, choose `feature/tessera-display-plugin-prototype` for this repository and use `tessera-plugin` as the folder.
4. Check the plugin details and add it to a test display. Building a Tessera plugin recompiles the display firmware; do not overwrite a production display without reviewing the proposed build.
5. Add the **Nearest and cheapest stations** tile in Tessera's layout editor, select the Mobile Fuel Stations overview sensor, and check the results.

The plugin requires a Tessera firmware/app build supporting **plugin API 0.24** (currently tested against Tessera's `dev` firmware). If your installed Tessera version does not support that API, do not force installation: update to a compatible Tessera release first.

In Tessera's layout editor, choose the `Nearby Stations` **overview sensor** (not a station-slot sensor). The tile maps the two nested station objects into eight scalar fields using Tessera's manifest `fields` support. No changes to HA entity IDs or integrations are required.

## Known limitations / release gates

- The tile's entity picker offers all sensors; the user must choose the Mobile Fuel Stations overview entity.
- The current `station_attributes()` serializer was checked: it exposes `station_name`, `price`, `distance`, and `currency`. The overview sensor exposes `nearest_station` and `cheapest_station`. The Tessera field mapper places the eight scalar values under the incoming `attributes` object; the tile reads them from there. Verify the mapped values in the rendered fixture and on a real screen.
- Tessera's entity data payload is capped at about 2.6 KB. If the large overview sensor payload is rejected, introduce an optional compact read-only entity on the HA integration side **in a separate reviewed PR**, not a breaking change.
- Guition host preview (light/dark, populated/empty) passed with zero warnings; other display sizes, German device locale, real HA data, and stale-state behavior still require hardware testing.
- Official Tessera manifest check and strict Guition host build passed in GitHub Actions run #41798931868; the generated preview images were reviewed. This is not yet a hardware-tested stable release.
- Do not enable manual provider refresh, navigation or price submission in the initial read-only beta.
- Plugin lifecycle is separate from the HA integration's Stable releases; never remove a HA Stable release.
