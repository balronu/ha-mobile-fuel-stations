# Mobile Fuel Stations

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

Mobile Fuel Stations intentionally does not depend on Apple Maps, Google Maps,
Sygic, Waze, or another navigation provider. Each station exposes dynamic
`latitude` and `longitude` attributes for dashboards, automations, and
client-specific navigation solutions.

The standardized `geo:` URI is defined by [RFC 5870](https://datatracker.ietf.org/doc/html/rfc5870.html).
Clients that support it may use it, but support depends on the frontend,
Companion App, operating system, and installed applications. The integration
does not claim uniform `geo:` behavior on every Home Assistant client and does
not provide an installed-app chooser.

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
- Navigation is intentionally platform-agnostic. The integration does not
  require or depend on Apple Maps, Google Maps, Sygic, Waze, or another
  navigation provider.
- Dashboard authors may use the station coordinates with a client-specific
  navigation mechanism. The standardized `geo:` URI is documented by RFC
  5870, but support and app selection depend on the receiving platform; this
  project does not claim that `geo:` works uniformly in every Home Assistant
  frontend or Companion App.
- The integration does not create map or navigation links.

## Development

```bash
python -m pytest -q
```

Fixtures use invented data and never contain real API keys or private GPS
coordinates.

## License

MIT. See [LICENSE](LICENSE).
