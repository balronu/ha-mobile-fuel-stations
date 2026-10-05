# Mobile Fuel Stations

[Deutsch](README.md) | [English](README.en.md)

A Home Assistant custom integration that searches nearby fuel stations from a
moving GPS entity. The first provider is [Tankerkönig](https://creativecommons.tankerkoenig.de/).

## Features

- Config flow: provider API key, location entity, radius, fuel, slot count.
- Regular cloud polling (15 minutes by default).
- Movement refresh when the location moved at least 2 km since the last
  successful search, with a hard five-minute cooldown.
- Persistent reference coordinates and successful-request timestamp.
- Open stations first, then valid fuel prices ascending; missing prices last.
- Stable station-slot entities with price, address, coordinates, status, and
  distance attributes.
- Each station slot exposes latitude and longitude so dashboard authors can
  connect it to the navigation mechanism supported by their client/device.
- Diagnostics that exclude API keys and exact coordinates.

## Dashboard card (`v0.2.0`)

Version 0.2.0 adds the native Lovelace card
`custom:mobile-fuel-stations-card` to the same HACS integration. The bundle is
shipped with the integration. After installation and restart, register this
Lovelace resource once:

```text
/mobile_fuel_stations/mobile-fuel-stations-card.js
```

Then use:

```yaml
type: custom:mobile-fuel-stations-card
entity: <OVERVIEW_ENTITY>
```

Version 0.2.0 also fixes the HTTP 500 when opening integration options and uses the
current Home Assistant OptionsFlow API. Existing config entries require no
migration, and the API key remains protected in the config-entry data.

The card includes a visual editor for selecting the overview entity and a
separate navigation button per station. Navigation is enabled by default and
can be disabled with `navigation: false`. The station block still opens
`more-info`; the navigation button uses an HTTPS maps link. Browser/app
handling is client-dependent and no specific maps app is guaranteed. Providers
are **Automatic**, **Apple Maps**, **Google Maps**, and **Waze**. Waze is
explicitly selected; AUTO continues to use Apple on iOS/iPadOS and Google on
Android/desktop.
The visual editor offers **Automatic**, **Apple Maps**, **Google Maps**, and
**Waze**; YAML can use `navigation_provider: auto|apple|google|waze`. The versionless resource
URL remains unchanged across HACS updates. A browser/Companion cache may still
need a reload. A station slot's displayed name follows the current station,
while its entity ID and unique ID remain stable.

Waze example:

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.<overview_entity>
navigation: true
navigation_provider: waze
```

Sygic is not included in v0.2.0.

## Requirements

- Home Assistant 2026.2 or newer.
- A Tankerkönig API key.
- A Home Assistant entity exposing numeric `latitude` and `longitude`
  attributes, normally a GPS `device_tracker`.

## Installation

### HACS custom repository

1. Open HACS → Integrations → three-dot menu → Custom repositories.
2. Add `https://github.com/balronu/ha-mobile-fuel-stations` as an Integration.
3. Install **Mobile Fuel Stations** and restart Home Assistant.

### Manual

Copy `custom_components/mobile_fuel_stations` into the Home Assistant
`config/custom_components` directory and restart Home Assistant.

## Configuration

Add the integration through **Settings → Devices & services → Add integration**
and select **Mobile Fuel Stations**. Choose the location entity and set radius,
fuel type, number of station slots, polling interval, movement threshold, and
cooldown. The API key is stored in the config entry and is never exposed in
entity attributes or diagnostics.

Defaults are 20 km, diesel, five slots, 15-minute polling, a 2 km movement
threshold, and a five-minute cooldown. The movement reference point advances
only after a successful provider response.

## Entities

- Entity IDs include the normalized location entity and can vary slightly with
  Home Assistant entity-ID normalization. Check **Settings → Devices & services
  → Entities** after setup.
- For a generic location `device_tracker.my_vehicle`, typical IDs are
  `sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations` and
  `sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1` through
  `_station_5`.
- The overview state is the current result count. Its attributes include
  `radius`, `fuel_type`, `location_entity`, `station_count`,
  `last_successful_update`, `reference_latitude`, `reference_longitude`, and
  `distance_since_last_search`.
- Each station slot reports the current price in EUR/L and attributes
  `station_id`, `station_name`, `brand`, `distance`, `is_open`, `street`,
  `house_number`, `postcode`, `place`, `latitude`, and `longitude`.

Station slot IDs are stable; the station assigned to a slot can change after a
refresh. A failed request retains the last successful result where possible.

## Location entity

The source can be a vehicle tracker, person/device tracker, or another GPS
entity. Generic example only:

```yaml
device_tracker.my_vehicle:
  state: not_home
  attributes:
    latitude: 50.0000
    longitude: 8.0000
```

Replace the example entity and coordinates with values from your own system.

## Dashboard example (standard cards)

This example requires no custom card. Replace the example entity IDs with the
entity IDs created on your Home Assistant instance.

```yaml
type: entities
title: Nearby fuel stations
entities:
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations
    name: Stations found
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1
    name: Station 1
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_2
    name: Station 2
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_3
    name: Station 3
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_4
    name: Station 4
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_5
    name: Station 5
```

## Mushroom example (optional)

Requires [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom). The
example uses native station attributes directly: no JSON parsing, JavaScript,
CSS hacks, absolute positioning, or negative margins.

For a Sections view, a full-width header can use:

```yaml
type: custom:mushroom-template-card
entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations
primary: Nearby fuel stations
secondary: >-
  {{ states('sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations') }} stations ·
  {{ state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations', 'radius') | int }} km ·
  {{ (state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations', 'fuel_type') or 'diesel') | title }}
multiline_secondary: true
layout: horizontal
fill_container: true
grid_options:
  columns: full
  rows: 2
```

A station card can use a native slot entity and its attributes:

```yaml
type: custom:mushroom-template-card
entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1
primary: >-
  {{ state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1', 'station_name') or 'Station unavailable' }}
secondary: >-
  {{ states('sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1') }} €/L ·
  {{ state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1', 'distance') }} km ·
  {{ 'open' if is_state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1', 'is_open', true) else 'closed' }}
multiline_secondary: true
layout: horizontal
fill_container: true
```

Duplicate the station card for slots 2–5 and replace only the entity ID. This
example is display-only and works without navigation.

## Navigation

The card shows a separate navigation button by default when valid coordinates
are available. The visual editor and YAML support `navigation_provider: auto`,
`apple`, `google`, and `waze`. `auto` selects Apple Maps for iOS/iPadOS and the
Google HTTPS web link for Android and desktop. Apple, Google, and Waze links
may be handled differently by the browser, Companion App, and installed apps;
no specific app is guaranteed. Waze is used only when explicitly selected.
Set `navigation: false` to hide the button.

## Troubleshooting

### No stations found

- Confirm that the selected location entity exists and has numeric
  `latitude`/`longitude` attributes.
- Check the radius and fuel type.
- Confirm the Tankerkönig API key and provider availability.

### Location unavailable

If the GPS entity is `unknown`, `unavailable`, or has invalid coordinates, no
request is sent with those coordinates. The last valid result is retained where
possible. Restore the GPS source and wait for the next update.

### Prices are not updating

Check the regular interval, movement-update setting, movement threshold, and
cooldown. Provider rate limits and price freshness are external factors.

### Dashboard entity not found

Find the actual IDs under **Settings → Devices & services → Entities**. Entity
IDs include the normalized location entity and may differ from examples.

## API and attribution

The integration calls the Tankerkönig nearby-stations endpoint with dynamic
latitude, longitude, radius, fuel type, and price sort parameters. Tankerkönig
usage is subject to its own API terms, rate limits, and attribution
requirements. Users must obtain and protect their own API key.

## Privacy

The selected location is sent to the provider to perform the requested search.
Do not publish diagnostics containing exact location data. API keys must never
be posted in issues, logs, screenshots, fixtures, or pull requests.

## Limitations

- Version 0.1.0 supports Tankerkönig only.
- A station slot is not a permanent station identity; it is a ranked slot.
- Provider availability, price freshness, and rate limits are external.
- Navigation is intentionally platform-agnostic. The card creates HTTPS links
  for Apple Maps, Google Maps, and explicitly selected Waze; app handoff
  remains client-dependent. Sygic is not included.
- Dashboard authors may use the station coordinates with a client-specific
  navigation mechanism. The standardized `geo:` URI is documented by RFC
  5870, but support and app selection depend on the receiving platform; this
  project does not claim that `geo:` works uniformly in every Home Assistant
  frontend or Companion App.

## Development

```bash
python -m pytest -q
```

Fixtures use invented data and never contain real API keys or private GPS
coordinates.

## License

MIT. See [LICENSE](LICENSE).
