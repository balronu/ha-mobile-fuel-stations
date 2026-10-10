# Mobile Fuel Stations v0.5.0

Mobile Fuel Stations 0.5.0 is the stable release of the multi-provider,
multi-fuel Home Assistant integration.

## Highlights

- Select Tankerkönig, Petromap, and Nakordoni individually or together. With
  multiple enabled providers, automatic selection uses only enabled and
  configured providers.
- Select E5, E10, Diesel, LPG, and HVO100 together. Stations appear once with
  all available selected-fuel prices, while comparisons remain separate per
  fuel.
- Show the nearest station and the cheapest station per fuel, with duplicate
  highlights merged only when station identity is reliable.
- Sort by distance or by an explicitly selected fuel price. Stations without a
  valid price for that fuel are placed last.
- Manage provider credentials safely, including masked status, replacement,
  explicit removal, and provider-specific validation status.
- Keep GPS movement updates, threshold/cooldown handling, navigation, stable
  station entities, and the compact responsive dashboard card.
- Include the approved Home Assistant branding and updated German/English
  documentation with user-oriented API-key setup instructions.

## Upgrade and compatibility

Update through HACS and restart Home Assistant after installation. Existing
config entries, credentials, entity IDs, dashboard resources, and compatible
sensor attributes are preserved. No new API client or programming setup is
required for normal use.

## Providers and limitations

Provider coverage depends on country, fuel, permissions, quotas, and current
station data. E5 may be used as an explicitly labelled E10 fallback only where
the country lacks verified E10 support; it is not used as a generic outage
fallback. Nakordoni live authorization remains pending and is not claimed as a
verified live capability.
