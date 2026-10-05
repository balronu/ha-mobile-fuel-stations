# Mobile Fuel Stations

**[Deutsche Version](README.md)**

Mobile Fuel Stations is a Home Assistant custom integration that finds nearby fuel stations using a configurable location entity. It is suited to vehicles, motorhomes, GPS trackers, and other moving objects.

The currently supported fuel-station provider is **Tankerkönig**.

## Features

- setup and options through the Home Assistant UI
- configurable location entity with `latitude` and `longitude` attributes
- diesel, E5, and E10
- search radius from 1 to 25 km
- 1 to 10 stable station slots
- regular refreshes and optional movement-triggered updates
- movement threshold and cooldown
- sorting by distance and price
- overview sensor with station data and search status
- diagnostics without exposing an API key or exact location
- German and English translations
- native dashboard card with visual editor
- automatic frontend registration
- navigation with Apple Maps, Google Maps, or Waze
- highlights for the nearest and cheapest open station

## Requirements

- Home Assistant with HACS, or access to a manual custom-integration installation
- a location entity exposing `latitude` and `longitude`
- a Tankerkönig API key

## Installation

### HACS (custom repository)

1. Open **HACS → Integrations**.
2. Open the three-dot menu and select **Custom repositories**.
3. Add `https://github.com/balronu/ha-mobile-fuel-stations` with category **Integration**.
4. Install **Mobile Fuel Stations**.
5. Restart Home Assistant completely.
6. Add the integration through **Settings → Devices & services → Add integration**.

The dashboard card is registered automatically. The automatically registered
frontend URL `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.4.0`
includes the integration version so an update does not reuse stale card
JavaScript from the cache. A manual Lovelace resource entry is not required
for a new installation.

### Manual installation

Download the repository and copy `custom_components/mobile_fuel_stations` to `config/custom_components/`. Restart Home Assistant completely, then set up the integration through **Settings → Devices & services**.

## Setup

Choose the location entity, radius, fuel type, and number of station slots. Configure refresh and movement options as needed.

## Dashboard card

### Add it through the card picker

After installation and restart:

1. Edit the dashboard and select **Add card**.
2. Search for **Mobile Fuel Stations**.
3. Select the card.
4. Select the overview entity or accept the suggested entity.
5. Save the card.

### Minimal YAML example

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.<overview_entity>
```

### Options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `entity` | entity ID | required | Overview sensor provided by the integration |
| `navigation` | Boolean | `true` | Show the separate navigation button |
| `navigation_provider` | `auto`, `apple`, `google`, `waze` | `auto` | Map provider used by the navigation button |

The station block still opens More Info. Navigation is started through the separate button.

### Nearest and cheapest station

The card optionally shows two highlights above the station list: **Nearest** and **Cheapest**. Both are selected from the complete Tankerkönig result set before the list is limited to the configured station slots. The nearest station does not require a valid price; when its price is missing, the card displays “Price unavailable”. If no suitable open station exists, the corresponding highlight is omitted.

Existing station slots retain their price-oriented behavior and their entity IDs
remain unchanged. If a highlight is not part of the visible slots, navigation
remains available; More Info is opened only when the station can be safely
mapped to a visible station entity.

### Navigation

With `navigation_provider: auto`:

- iOS/iPadOS: Apple Maps
- Android: Google Maps
- desktop and other devices: Google Maps

Use `apple`, `google`, or `waze` to select a provider explicitly. Waze is never selected automatically. Set `navigation: false` to hide the button.

Navigation starts only after a user action. The card does not put a fixed starting position into the URL; the browser, companion app, and operating system determine how an installed map app receives the destination. Sygic is currently not supported.

Waze example:

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.<overview_entity>
navigation: true
navigation_provider: waze
```

## Upgrading from older versions

For an upgrade from v0.3.1 to v0.4.0, update through HACS and restart Home Assistant completely. No migration is required. The Tankerkönig radius is limited to 25 km; existing configurations with a higher stored value are defensively capped at 25 km for the API request.

Older v0.2.x installations may still contain the former manual Lovelace resource `/mobile_fuel_stations/mobile-fuel-stations-card.js`. Update the integration first, restart Home Assistant, and verify the card and card picker. Then remove the old entry through the Home Assistant UI and fully reload the browser or companion app. Never edit `.storage` manually.

## Location entity

The location entity must provide numeric `latitude` and `longitude` attributes. For movement-triggered updates, the configured movement threshold and cooldown control when a new search is performed.

## Generated entities

The overview sensor exposes attributes including:

`radius`, `fuel_type`, `location_entity`, `station_count`, `station_entities`, `last_successful_update`, `reference_latitude`, `reference_longitude`, `distance_since_last_search`, `nearest_station`, `cheapest_station`

Station slots expose attributes including:

`station_id`, `station_name`, `brand`, `distance`, `is_open`, `street`, `house_number`, `postcode`, `place`, `latitude`, `longitude`

Station-slot entity IDs and unique IDs remain stable. The station currently shown in a slot may change after an update, and its display name follows the current station. An empty slot is `unavailable`. Prices use `EUR/L`.

## Alternative dashboard examples

The native Mobile Fuel Stations card is the recommended default. The generated sensors can also be displayed with standard Home Assistant cards. Mushroom Cards are an optional additional custom-card dependency.

## Troubleshooting

- **No stations:** Check the location, radius, fuel type, and API access.
- **Location unavailable:** Check that the location entity provides current numeric `latitude` and `longitude` attributes.
- **Prices do not update:** Check the overview sensor, last successful update, and Home Assistant logs.
- **The card is missing from Add card:** Update the integration, restart Home Assistant completely, fully reload the browser or companion app, and check that an overview sensor exists. A manual resource entry is not required for current installations.
- **API errors:** Check the Tankerkönig API key and the log messages.
- **Movement updates:** Check the movement threshold and cooldown.
- **Entity IDs:** Review the generated entities under **Settings → Devices & services → Entities**.

If the problem persists, inspect frontend logs and the browser console, then open a GitHub issue with relevant redacted logs.

## Privacy and security

The API key is stored in the config entry and must not be published. The location is sent to Tankerkönig for the station search. Review diagnostics for sensitive data before sharing them. Do not publish exact locations or credentials in issues.

## API and attribution

Station data is provided by the configured Tankerkönig service. Follow its terms of use and API limits.

## Development and contributions

Development and testing information is available in [CONTRIBUTING.md](CONTRIBUTING.md). Keep user-facing changes synchronized between `README.md` and `README.en.md`.

## License

See [LICENSE](LICENSE).
