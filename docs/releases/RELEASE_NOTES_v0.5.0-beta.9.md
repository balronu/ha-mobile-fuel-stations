# Mobile Fuel Stations v0.5.0-beta.9

## Highlights

- Fixes the Home Assistant blocking-I/O warning during the first country
  resolution by loading the offline country dataset once through the executor.
- Repeated location updates use the in-memory country cache and preserve the
  existing automatic provider-selection behavior.
- Missing or corrupt country data fails open without repeated synchronous file
  reads.
- Includes the previously validated beta.8 options-flow UI improvements and
  translations.

## Compatibility

- Existing config entries, provider credentials, sensor entity IDs, GPS logic,
  multi-fuel behavior, and local branding are retained.
- Nakordoni live authorization remains an external provider limitation.
