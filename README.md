# Mobile Fuel Stations

Home Assistant custom integration for nearby fuel stations based on a vehicle
or device entity exposing valid latitude and longitude. It provides provider-
aware prices, stable station entities, movement updates, startup GPS recovery,
stale-data diagnostics, and an optional Lovelace card.

## Versions

| Channel | Version | Meaning |
| --- | --- | --- |
| Stable | `v0.5.1` | Recommended for production |
| Published beta | `v0.6.0-beta.5` | Startup GPS recovery and bounded provider retry |
| Development target | `v0.6.0-beta.6` | Logo matching and documentation; not released |

The beta branch is for controlled testing. A real production Home Assistant
restart test is still outstanding.

## Features

- Tankerkönig, Petromap, and Nakordoni provider adapters
- Diesel, E5, E10, LPG, and HVO100 where the selected provider supports them
- Radius, station count, sorting, refresh interval, movement threshold/cooldown
  and provider selection
- Startup GPS recovery, normal polling, bounded provider backoff, Retry-After
  handling, stale-data preservation, and secret-free diagnostics
- Responsive Lovelace card with navigation and optional local brand logos

## Documentation

- [Deutsch](README.de.md)
- [English](README.en.md)
- [Changelog](CHANGELOG.md)
- [Releases](docs/releases/)
- [Brand-logo sources and hashes](BRAND_LOGOS.md)

## Installation

Install **Mobile Fuel Stations** through HACS → Integrations, or add this
repository as a custom Integration repository. Then restart Home Assistant and
add the integration through **Settings → Devices & services**. Stable and
pre-release versions are selected in HACS; beta.6 is not published yet.

See the language-specific guides for setup, provider coverage, startup
recovery, logo fallback behavior, troubleshooting, privacy, and limitations.
