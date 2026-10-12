# Mobile Fuel Stations — English guide

Mobile Fuel Stations is a Home Assistant custom integration for nearby fuel
stations. It reads latitude and longitude from a configured vehicle or device
tracker, queries the selected provider, and exposes stable overview and station
entities plus an optional responsive Lovelace card.

## Version status

- **Stable:** `v0.5.1`, the production recommendation.
- **Published beta:** `v0.6.0-beta.5`, with startup GPS recovery and bounded
  transient-provider retry.
- **Development target:** `v0.6.0-beta.6`. This branch is not released.

Stable remains unchanged. Beta.5 is the rollback version. A real production
restart test is still outstanding, so the occasional browser-specific loading
issue is not claimed as fixed.

## Requirements and installation

Install through **HACS → Integrations**, search for **Mobile Fuel Stations**, or
add `https://github.com/balronu/ha-mobile-fuel-stations` as a custom
Integration repository. Select stable for production or enable pre-releases for
beta testing. Restart Home Assistant after installation, then add the
integration under **Settings → Devices & services → Add integration**.

The integration needs a tracker entity with valid `latitude` and `longitude`.
Provider access requires a provider-specific API key and any required approval.
No key is bundled with the project.

## Setup and fuel selection

The config flow lets you choose a location entity, radius from 1–25 km, 1–10
station slots, E5, E10, Diesel, LPG, or HVO100, sorting, refresh interval,
movement threshold/cooldown, and one or more providers. Multiple fuels remain
one station entity with several price rows. Ranking is per fuel; different
fuels are never compared. E10 may use E5 only where capability explicitly
allows it. Diesel, LPG, and HVO100 are not silently substituted.

## Providers and verified capability matrix

This is the capability declared in code, not a guarantee that every account or
station returns data.

| Provider | Country/price coverage in code | Fuels in code | Key and limits |
| --- | --- | --- | --- |
| [Tankerkönig](https://onboarding.tankerkoenig.de/) | Germany (`DE`), per-station prices | Diesel, E5, E10 | API key; maximum radius 25 km; provider terms and response limits apply |
| [Petromap](https://developer.petromap.eu/) | `DE`/`AT` per-station; `BG`/`PL`/`SK` national-only; `ME`/`RS` no prices | Diesel, E5, LPG | API key and approval; response metadata may provide credits/rate/retry information |
| [Nakordoni](https://nakordoni.eu/en/developers/docs) | Account/market dependent; no fixed country allow-list is claimed | Diesel, E5, E10, LPG | Bearer key and possible market approval; official Explorer documentation currently states 2 QPS and 1,000 standard calls/day, subject to plan changes |

HVO100 is selectable, but current provider declarations do not claim universal
HVO100 station-price support. Empty prices remain empty. Provider limits can
change; the runtime honors Retry-After/rate-limit metadata where supplied.

### API keys

Open **Settings → Devices & services → Mobile Fuel Stations → Configure →
Manage credentials**. Enter only the key for the selected provider. Statuses
distinguish missing, stored-not-checked, successful, authentication-failed,
temporarily-unavailable, and approval-pending. Opening options does not start a
network request; keys are never printed in logs or diagnostics.

## Startup recovery, polling, and errors

After startup the normal first refresh runs. If GPS is unavailable, beta.5
schedules checks around 3, 10, and 30 seconds, then slower checks about every
60 seconds. A GPS state event can accelerate the next check, while timers cover
missed events and attribute-only changes. Once valid coordinates are available,
one deduplicated provider refresh runs immediately.

Normal DataUpdateCoordinator polling remains active at the configured interval
(15 minutes by default), and movement refreshes retain their threshold and
cooldown. Recovery, movement, and polling share a deduplicated request path.
Temporary network, timeout, and rate-limit failures use bounded exponential
backoff with jitter and honor Retry-After. Permanent authentication/configuration
errors stop aggressive retries. Successful data is retained and marked stale
during temporary failures. Recovery ends after success; unload cancels timers,
tasks, and listeners.

## Lovelace card and brand logos

The card is registered automatically:

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.mobile_fuel_stations_device_tracker_auto_nearby_stations
navigation: true
show_brand_logos: true
logo_path: /mobile_fuel_stations/logos/
```

Six local SVGs are bundled: Aral, Shell, JET, TotalEnergies, ORLEN, and OMV.
Matching normalizes case, accents, punctuation, and whitespace. Beta.6 also
recognizes a supported brand embedded in a station name when `brand` is empty
or verbose, such as `Aral Tankstelle` or `Total Energies`. Unknown brands,
empty fields, missing files, and image-load errors use the generic pump icon.

User-owned SVGs may be placed in `/config/www/fuel-logos/` and referenced as
`/local/fuel-logos/`. Only safe `/local/...` and `/hacsfiles/...` paths are
accepted; external URLs, query strings, backslashes, and traversal are
rejected. Sources, hashes, and rights boundaries are in
[`BRAND_LOGOS.md`](BRAND_LOGOS.md). No external logo is downloaded.

The card shows station name, useful brand text, address, provider, opening
state, distance, prices, stale/fallback information, navigation, and nearest/
cheapest highlights. Coordinates are not shown in diagnostics.

## Diagnostics and troubleshooting

Diagnostics expose only non-sensitive state such as refresh status, last
successful update, stale/error classification, GPS availability, recovery
state, and retry timing. They omit API keys, tokens, and exact coordinates.

- **No stations after startup:** check tracker coordinates, provider
  country/fuel support, API key, and approval.
- **Stale data:** inspect the error classification and provider status;
  temporary failures retain the last successful data.
- **No price:** no valid price was returned for that exact fuel; no silent
  substitution occurs except the documented E10→E5 case.
- **Generic logo:** the brand is unknown/unsupported or the local asset failed
  to load. Check the static logo path and browser cache after an update.
- **Nakordoni unavailable:** market approval, product permission, quotas, and
  current authorization are external prerequisites.

## Privacy, limitations, and links

The selected provider receives the requested location, radius, and fuel query.
Review provider terms and privacy policies. Exact coordinates, API keys, and
tokens are not written to diagnostics or logs. Provider coverage, prices,
quotas, approval, and API behavior can change independently of this project.

- [Repository](https://github.com/balronu/ha-mobile-fuel-stations)
- [Issues](https://github.com/balronu/ha-mobile-fuel-stations/issues)
- [Releases](https://github.com/balronu/ha-mobile-fuel-stations/releases)
- [Changelog](CHANGELOG.md)
- [German guide](README.de.md)
