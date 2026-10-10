# Mobile Fuel Stations v0.5.0-beta.10

## Highlights

- Multi-provider checkbox selection for Tankerkönig, Petromap, and Nakordoni.
- Masked API-key status with safe replacement and explicit removal; existing
  beta.9 configurations migrate without changing entity IDs.
- More compact mobile station cards with wrapping long names/addresses,
  visible prices and status, and accessible navigation targets.
- Duplicate nearest/cheapest highlights are merged only for the same stable
  station identity; different fuel highlights remain correctly labeled.

## Compatibility

Existing config entries, provider credentials, entities, sensor attributes,
dashboard resources, and the approved local branding are retained. Nakordoni
live API authorization remains an external prerequisite and was not claimed as
available by this release.
