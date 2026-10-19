# Mobile Fuel Stations v0.7.3

## Nakordoni fuel and address normalization

### Fixed

- Correct E10 cheapest-station highlights for Nakordoni single-fuel requests.
- Preserve formatted and structured provider addresses.
- Exclude explicitly stale prices from current cheapest-station selection.

### Compatibility

- Existing Config Entries and Lovelace cards remain compatible.
- Navigation remains coordinate-based.
- Tankerkönig and Petromap behavior is unchanged.
- Missing provider address data is not synthesized.

This release was validated with mocked provider fixtures and CI. No live
provider API request or OAuth test was performed.
