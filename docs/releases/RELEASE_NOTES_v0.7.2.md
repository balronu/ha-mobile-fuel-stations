# Mobile Fuel Stations v0.7.2

## Provider-neutral station highlights

### Fixed

- Nearby and cheapest station highlights now include stations with unknown
  opening status.
- Explicitly closed stations remain excluded.
- Known-open stations are preferred on equal distance or price.
- Station selection is deterministic.

### Compatibility

- No changes to existing Config Entries, sensor attributes, or Lovelace YAML
  configuration.
- The behavior applies across Tankerkönig, Nakordoni, and Petromap.
- Unknown opening status is not rendered as “Open” or “Geöffnet”.

This release was validated with mocked provider fixtures and CI. No live
provider API request or OAuth test was performed.
