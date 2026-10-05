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

- Home Assistant 2026.9 or newer.
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

- `sensor.mobile_fuel_stations_nearby_stations`: current result count and
  configuration/status metadata.
- `sensor.mobile_fuel_stations_station_1` through the configured slot count:
  current price in EUR/L and station attributes.

Station slot IDs are stable; the station assigned to a slot can change after a
refresh. A failed request retains the last successful result where possible.

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
