# Mobile Fuel Stations for Tessera (beta test)

This **beta-stage** Tessera plugin shows the nearest and cheapest station from the existing Home Assistant [Mobile Fuel Stations](https://github.com/balronu/ha-mobile-fuel-stations) integration.

**Requires:** Tessera development version with plugin API 0.24 and Mobile Fuel Stations installed in Home Assistant.

## Architecture

The plugin reads the Mobile Fuel Stations overview sensor's station, fuel and freshness attributes. It does **not** call Tankerkönig, Petromap or Nakordoni directly and never accesses provider credentials. All API quotas and GPS updates remain controlled by Home Assistant.

The highlights tile adapts from 1×1 to 4×4. Tapping any supported size opens an official Tessera detail card with nearest/cheapest station, address, opening status, fuel selection and freshness. Fuel selection is display-local and never changes the HA configuration or starts another request.

## Set up

Install this read-only beta using the steps below. No additional Home Assistant template sensor is required.

### Install the beta from GitHub

This is a **development-branch beta test**, not a published GitHub Release or a Tessera community-index listing.

1. Open Tessera's **Plugins** page and choose **Add with a link**.
2. Enter the repository folder URL: `https://github.com/balronu/ha-mobile-fuel-stations/tree/main/tessera-plugin`.
3. If Tessera offers **Test a branch**, choose `feature/tessera-display-plugin-prototype` in the branch field. The folder is already encoded in the URL; do not put the slash-containing branch name into the URL path.
4. Check the plugin details and add it to a test display. Building a Tessera plugin recompiles the display firmware; do not overwrite a production display without reviewing the proposed build.
5. Add the **Nearest and cheapest stations** tile in Tessera's layout editor, select the Mobile Fuel Stations overview sensor, and check the results.

The plugin requires a Tessera firmware/app build supporting **plugin API 0.24** (currently tested against Tessera's `dev` firmware). If your installed Tessera version does not support that API, do not force installation: update to a compatible Tessera release first.

In Tessera's layout editor, choose the Mobile Fuel Stations **overview sensor** (not a station-slot sensor). The manifest requests only the nested station objects and selected diagnostic attributes. No changes to HA entity IDs or integrations are required.

## Known limitations / release gates

- The tile's entity picker offers all sensors; the user must choose the Mobile Fuel Stations overview entity.
- The tile consumes the existing `nearest_station`, `cheapest_station`, `cheapest_stations_by_fuel`, `fuel_types`, `data_stale`, `price_age_hours`, `station_stale`, address and opening-status fields when present. Older responses without optional fields remain valid and display a localized fallback.
- Tessera's entity data payload is capped at about 2.6 KB. If the large overview sensor payload is rejected, introduce an optional compact read-only entity on the HA integration side **in a separate reviewed PR**, not a breaking change.
- The official Tessera manifest check and strict Guition host preview pass on the current PR commit. The offline preview covers populated, empty, stale and multiple-fuel data; other physical display sizes, German device locale and real HA data still require hardware testing.
- The plugin is still a development-branch beta, not a published plugin release. Hardware installation and firmware flashing are intentionally not part of this PR.
- Do not enable manual provider refresh, navigation or price submission in the initial read-only beta.
- Plugin lifecycle is separate from the HA integration's Stable releases; never remove a HA Stable release.
