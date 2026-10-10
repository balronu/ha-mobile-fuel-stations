# Mobile Fuel Stations

<p><img src="assets/branding/logo.png" alt="Mobile Fuel Stations" width="160"></p>

Mobile Fuel Stations is a Home Assistant custom integration for nearby fuel
stations based on a vehicle or device entity exposing `latitude` and
`longitude`. It is designed for cars, motorhomes, and other moving objects.

## Versions

| Channel | Version | Purpose |
| --- | --- | --- |
| Stable | `v0.4.0` | Recommended for production installations |
| Pre-release | `v0.5.0-beta.12` | Current beta with provider-status fix and compact status presentation |

Beta versions can change. Stable is the safer choice for production systems.

## Features

- Select E5, E10, Diesel, LPG/autogas, and HVO100 together
- One station card containing every available selected-fuel price
- Independent price evaluation per fuel; different fuels are never mixed in one ranking
- Nearest station by distance and cheapest station per fuel
- Merged highlight cards only when the same station has a matching stable station ID
- Distance sorting or price sorting for one explicitly selected fuel
- Compact responsive dashboard card for phones, tablets, and desktop
- Opening status, price age, missing-price states, E10/E5 fallback notices, and navigation
- Stable station entities and configurable 1–10 station slots
- Movement updates with threshold and cooldown
- Local Home Assistant branding in `custom_components/mobile_fuel_stations/brand/`
- General options can be saved independently of credential management

## Providers and coverage

Providers are selected with the official Home Assistant checkbox selector. One
selected provider runs directly. With two or more enabled providers, automatic
selection considers only those enabled and configured providers; a disabled or
unauthenticated provider is never used as a silent fallback.

| Provider | Key | Current implementation coverage |
| --- | --- | --- |
| [Tankerkönig](https://onboarding.tankerkoenig.de/) | Yes | Germany; Diesel, E5, and E10; API radius up to 25 km |
| [Petromap v2](https://developer.petromap.eu/) | Yes | DE/AT station prices for Diesel, E5, and LPG; other countries depend on verified Petromap coverage |
| [Nakordoni](https://nakordoni.dev/) | Yes | Implemented for Diesel, E5, E10, and LPG; live API/market approval is still pending |

HVO100 is a real selectable fuel type. Prices depend on a verified provider and
country capability; HVO100 is not documented as universally unsupported and is
never silently represented as Diesel.

### API keys for regular Home Assistant users

Each enabled provider needs its own access. You do not need programming skills,
your own app, or your own API client. Open the provider's official page,
register or request access, and wait for the provider's approval. If asked for
the purpose of use, you may state **Private use with Home Assistant / Mobile
Fuel Stations**, where applicable. Always follow the provider's terms,
registration restrictions, quotas, and possible charges.

#### Tankerkönig

1. Open the [Tankerkönig onboarding page](https://onboarding.tankerkoenig.de/).
2. Register and request the intended access.
3. If asked for the purpose, state private use with Home Assistant / Mobile
   Fuel Stations where applicable.
4. Wait for registration and key issuance, and observe Tankerkönig's terms of
   use and any registration restrictions.
5. In Home Assistant, open **Settings → Devices & services → Mobile Fuel
   Stations → Configure → Manage credentials**.
6. Enter the key and save it.
7. Check the actual access status afterwards. A stored key is not automatically
   treated as successfully checked.

#### Petromap

1. Open the [Petromap Developer page](https://developer.petromap.eu/).
2. Register or request API access.
3. If asked for the purpose, state private use with Home Assistant / Mobile
   Fuel Stations where applicable.
4. Wait for Petromap's manual approval and key issuance; registration alone
   does not guarantee usable access.
5. In Home Assistant, open **Settings → Devices & services → Mobile Fuel
   Stations → Configure → Manage credentials**.
6. Enter the key and save it.
7. Check the actual access status. Petromap remains “stored – not checked yet”
   until a successful provider-owned request has occurred.

#### Nakordoni

1. Open the [Nakordoni Developer page](https://nakordoni.eu/en/developers).
2. Register or request key issuance.
3. If asked for the purpose, state private use with Home Assistant / Mobile
   Fuel Stations where applicable.
4. Wait for both key issuance and the required approval for the countries and
   fuel data you need. A key alone does not automatically mean that data
   access is approved; live approval is still pending.
5. In Home Assistant, open **Settings → Devices & services → Mobile Fuel
   Stations → Configure → Manage credentials**.
6. Enter the key and save it.
7. Check the actual status. Immediate approval or unrestricted use is not
   assumed.

Keys are never shown in full in the UI, logs, diagnostics, or Git files.

The options flow shows a non-sensitive status for each provider:

- No API key stored
- API key stored – not checked yet
- Access successfully checked
- Authentication failed
- Access cannot be checked right now
- API approval pending
- Not selected

“API key stored” explicitly does not mean “access successfully checked”. A
successful runtime provider request records the check status; opening the
options flow never starts a network request. General settings save directly.
The **Manage credentials** control opens the separate credential manager.
Leaving a key field empty keeps an existing key; replacement requires entering a
new value, removal requires an explicit remove option, and a key change resets
that provider's check status.

The native Home Assistant form renders the compact status lines as its
description above the fields. The fields then appear in the order provider
selection, credential management, and general settings. Home Assistant does
not provide a supported way to place a free-form status section between native
form fields.

## HACS installation

1. Open **HACS → Integrations**.
2. Search for **Mobile Fuel Stations**. If it is not listed, add
   `https://github.com/balronu/ha-mobile-fuel-stations` under **Custom
   repositories** with category **Integration**.
3. Install it and restart Home Assistant completely.
4. Add it under **Settings → Devices & services → Add integration**.

The dashboard card registers automatically. Beta.12 uses the versioned resource
URL:

`/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.5.0-beta.12`

The local icon/logo is Home Assistant integration branding. A HACS repository
icon and Home Assistant integration branding are separate mechanisms; no extra
unsupported manifest field is required.

## Setup

Choose the vehicle location entity, radius from 1 to 25 km, one or more fuel
types, 1–10 station slots, refresh interval, movement updates, threshold and
cooldown, distance or fuel-price sorting, and one or more providers.

Automatic provider selection starts with two enabled providers. It considers
country, fuel capability, station-price coverage, and available keys. With one
provider selected, only that provider is used.

In countries without verified E10 coverage, E5 may be used as the documented
E10 fallback and is shown as **E5 instead of E10**. No fallback is applied to
Diesel, LPG, or HVO100, or merely because one API/station price is temporarily
missing.

## Prices, card, and navigation

Distance ascending is the default. Price sorting requires an explicit sorting
fuel; stations without a valid price for that fuel are placed last. Diesel,
E10, E5, LPG, and HVO100 never compete in one cross-fuel price ranking.

The card shows station name, address, opening status, distance, all available
prices, fallback notices, and a navigation button. Long names and addresses
wrap without horizontal overflow. Navigation supports Apple Maps, Google Maps,
Waze, or automatic selection.

No current UI screenshot is stored in the repository. The approved branding
preview is available at [`assets/branding/preview.png`](assets/branding/preview.png).
The GitHub social preview is prepared at
[`assets/github-social-preview.png`](assets/github-social-preview.png). GitHub
uses it only after a manual upload under **Repository → Settings → General →
Social preview**.

## Updating an existing installation

Create a Home Assistant backup, update through HACS, and restart Home Assistant
completely. Existing config entries, credentials, station slots, sensor entity
IDs, dashboard resources, and compatible sensor attributes are retained. Legacy
single-provider values migrate losslessly to the provider selection.

## Privacy and attribution

Depending on the selected provider, vehicle coordinates, radius, and selected
fuels may be sent to that provider. Full API keys are not logged and exact
locations are not exposed in diagnostics. Nakordoni requires visible
attribution: **Data by nakordoni.eu**.

## Troubleshooting

- **No stations:** Check the location entity, coordinates, radius, provider
  capability, and API key.
- **Price unavailable:** No valid price exists for that exact station and fuel;
  another fuel is not substituted.
- **Provider inactive:** Check the provider checkbox and stored-key status.
- **Stale card after update:** Restart Home Assistant completely. The versioned
  resource URL normally prevents stale card JavaScript from being reused.
- **Nakordoni:** Live approval, market permission, and quotas remain external
  prerequisites and are not claimed as available in beta.12.

## Known limitations

- Nakordoni live API approval is still pending.
- Provider and country coverage can change with external API contracts,
  permissions, quotas, and station data.
- HVO100 is shown with prices only when a provider/country capability is verified.

## Development and tests

Beta.12 is checked with Python tests, frontend tests, the production build,
Hassfest, JSON/syntax checks, bundle-diff validation, and `git diff --check`.
Provider/API tests also use mocks and fixtures; unapproved live access is never
claimed as successful.
