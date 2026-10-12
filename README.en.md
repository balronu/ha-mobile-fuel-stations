# Mobile Fuel Stations

[🇩🇪 Deutsch](README.md) | 🇬🇧 **English**

<p align="center"><img src="assets/branding/logo.png" alt="Mobile Fuel Stations" width="220"></p>

Mobile Fuel Stations is a Home Assistant custom integration for nearby fuel
stations. It uses the coordinates of a vehicle, motorhome, or other device
entity and exposes stations, prices, distance, opening status, and navigation
through sensors and a Lovelace card.

## Contents

- [Versions and features](#versions-and-features)
- [Installation with HACS](#installation-with-hacs)
- [Setup and configuration](#setup-and-configuration)
- [Providers, countries, and fuels](#providers-countries-and-fuels)
- [API keys](#api-keys)
- [GPS, polling, and startup recovery](#gps-polling-and-startup-recovery)
- [Lovelace card and brand logos](#lovelace-card-and-brand-logos)
- [Prices, sorting, and navigation](#prices-sorting-and-navigation)
- [Updates and migration](#updates-and-migration)
- [Privacy and limitations](#privacy-and-limitations)
- [Troubleshooting and diagnostics](#troubleshooting-and-diagnostics)
- [Development and tests](#development-and-tests)
- [Release archive](#release-archive)

## Versions and features

| Channel | Version | Meaning |
| --- | --- | --- |
| Stable | `v0.6.0` | Current stable release |
| Previous stable | `v0.5.1` | Available rollback version |
| Last release candidate | `v0.6.0-beta.6` | Previous beta |

`v0.6.0` is the current stable release. It includes the improved local
detection of the six bundled brand logos and the updated documentation from
Beta.6. The provider backend, startup recovery, and regular polling retain the
validated beta.5/beta.6 behavior.

Features include nearby stations based on a tracker entity, E5/E10/diesel/LPG
and HVO100 selection, multi-fuel station sensors, distance and fuel-price
sorting, automatic provider selection, startup recovery, regular coordinator
polling, movement refreshes, navigation, and a responsive Lovelace card.

## Installation with HACS

1. Open **HACS → Integrations**.
2. Search for **Mobile Fuel Stations**. If it is not listed, add
   `https://github.com/balronu/ha-mobile-fuel-stations` under **Custom
   repositories** with type **Integration**.
3. Install the integration.
4. Fully restart Home Assistant.
5. Open **Settings → Devices & services → Add integration** and select
   **Mobile Fuel Stations**.

`v0.6.0` is the stable HACS version. Beta.6 remains available in the GitHub
archive as the last release candidate; `v0.5.1` remains available as the
previous stable rollback.

The Lovelace card is supplied and registered by the integration. The versioned
Beta.6 resource is:

```text
/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.6.0
```

For technical resource-loading details, see
[docs/RESOURCE_LOADING.md](docs/RESOURCE_LOADING.md).

## Setup and configuration

The configuration flow selects a position entity with `latitude` and
`longitude`, radius, station slots (1–10), one or more fuel types, provider
mode, sorting, polling interval, movement threshold/cooldown, and navigation
service. General options and credentials are stored separately. Empty
credential fields keep existing keys; keys are never shown in full.

## Providers, countries, and fuels

The following matrix reflects capabilities verified in the code and tests.
External contracts, quotas, and account permissions can reduce availability.

| Provider | Access | Verified coverage and fuels |
| --- | --- | --- |
| [Tankerkönig](https://onboarding.tankerkoenig.de/) | API key | Germany; diesel, E5, E10; maximum API radius 25 km |
| [Petromap](https://developer.petromap.eu/) | API key and possibly approval | Station prices in Germany and Austria for diesel, E5, and LPG; further countries/data depend on Petromap |
| [Nakordoni](https://nakordoni.eu/en/developers) | API key and market/access approval | Diesel, E5, E10, and LPG in the implemented API model; country and live coverage are account- and market-dependent |

Selectable fuel keys are `e5`, `e10`, `diesel`, `lpg`, and `hvo100`. A provider
is used only when its capability and response support the requested fuel.
HVO100 is not silently converted to diesel. Prices are shown only where a
provider/country capability is verified. In automatic mode only enabled and
configured providers are considered. E10 may use an explicitly supported E5
substitution; this does not apply to diesel, LPG, or HVO100.

## API keys

Each enabled provider requires its own access. Follow the provider's
registration, approval, quota, cost, privacy, and terms requirements:

- [Tankerkönig onboarding](https://onboarding.tankerkoenig.de/)
- [Petromap developer portal](https://developer.petromap.eu/)
- [Nakordoni developer portal](https://nakordoni.eu/en/developers)

Enter keys under **Settings → Devices & services → Mobile Fuel Stations →
Configure → Manage credentials**. A stored key is not proof of a successful
live check. The options flow does not perform unnecessary network requests.
Credentials are never written to Git, logs, or diagnostics.

## GPS, polling, and startup recovery

The configured entity must provide valid coordinates. After startup, the
integration creates its entities and performs the normal coordinator refresh. If
GPS is unavailable, startup recovery checks again at approximately 3, 10, and
30 seconds, then approximately every 60 seconds until GPS becomes available or
the integration is unloaded.

A matching GPS event can trigger the next attempt immediately. Timed checks
remain active so missed `state_changed` events and attribute-only changes do
not force users to wait for the next 15-minute cycle. All recovery triggers go
through one deduplicated path. Recovery and regular polling never issue
parallel provider requests.

Transient provider failures use bounded exponential backoff and jitter.
`Retry-After` and detected rate limits take precedence. Permanent
authentication or configuration failures are diagnosed without an aggressive
retry loop. Valid cached data is retained and marked stale during transient
failures. Successful recovery ends the recovery loop; normal polling and the
movement refresh remain active. Timers, tasks, and listeners are cleaned up on
unload/reload.

## Lovelace card and brand logos

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations
navigation: true
show_brand_logos: true
```

Beta.6 recognizes the six bundled local SVGs: Aral (`aral.svg`), Shell
(`shell.svg`), JET (`jet.svg`), Total/TotalEnergies (`total.svg`),
ORLEN/ORLEN Express (`orlen.svg`), and OMV (`omv.svg`). Matching normalizes
case, Unicode accents, whitespace, and punctuation. If `brand` is missing or
does not match, the station name is checked as a fallback. Unknown, empty, or
unloadable logos use the generic fuel-pump symbol. Set
`show_brand_logos: false` to disable logos. Sources and checksums are listed in
[docs/BRAND_LOGOS.md](docs/BRAND_LOGOS.md).

The card shows station name, address, distance, opening status, price age,
available prices, E5/E10 substitution hints, and navigation. Local SVGs may be
placed under `/config/www/fuel-logos/` and referenced through `/local/...`;
unsafe paths and external URLs are rejected. Image errors fall back to the
generic symbol.

## Prices, sorting, and navigation

Stations are sorted by distance by default. Price sorting requires one explicit
fuel type; stations without a valid price appear last. Different fuel types
are never mixed into one ranking, and a missing price is not replaced with a
different fuel. Depending on configuration, navigation can use Apple Maps,
Google Maps, Waze, or automatic selection.

## Updates and migration

Create a Home Assistant backup before updating. Update through HACS and fully
restart Home Assistant. Existing config entries, credentials, station sensors,
and compatible dashboard configurations are retained. Check the versioned card
resource and browser cache after a major update. `v0.5.1` remains available as
the previous stable rollback; beta releases remain in the GitHub archive.

## Privacy and limitations

Depending on the selected provider, coordinates, radius, and fuel selection
may be sent to external APIs. Review each provider's privacy policy and terms.
The integration does not send a device ID to Nakordoni, does not log complete
API keys, and does not expose exact private coordinates in diagnostics. Keep
the visible **Data by nakordoni.eu** attribution when using Nakordoni.

Provider coverage, prices, opening hours, quotas, and permissions can change.
Nakordoni market coverage and HVO100 prices are not universally guaranteed.

## Troubleshooting and diagnostics

- **No stations:** check the entity, valid coordinates, radius, provider mode,
  and credential status.
- **GPS unavailable at startup:** inspect recovery status, attempt count, and
  next retry; a valid GPS event accelerates recovery.
- **Missing price:** no valid price was returned for that station and fuel.
- **Provider error:** fix authentication/configuration errors; transient
  errors retain cached data and mark it stale.
- **Missing logo:** check `brand`, station name, `show_brand_logos`, resource
  version, and browser cache.

Diagnostics include recovery status, attempt count, last trigger, next retry,
GPS event type/time, in-flight status, and error classification, but no
coordinates, tokens, or complete keys.

## Development and tests

```bash
python -m pytest
cd frontend && npm ci && npm test -- --run && npm run typecheck && npm run build
python -m compileall custom_components tests
```

CI additionally checks Home Assistant/Hassfest compatibility, bundle and diff
consistency, Markdown/version consistency, and secret scanning. Provider and
recovery tests use mocks and fixtures rather than unverified live credentials.

## Release archive

Historical release notes are preserved under
[`docs/releases/`](docs/releases/), including the current
[`v0.6.0 release notes`](docs/releases/RELEASE_NOTES_v0.6.0.md).
See also [CONTRIBUTING.md](CONTRIBUTING.md),
[docs/BRAND_LOGOS.md](docs/BRAND_LOGOS.md), and the
[GitHub releases](https://github.com/balronu/ha-mobile-fuel-stations/releases).
