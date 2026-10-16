# Mobile Fuel Stations v0.7.0-beta.5

## Provider cooldowns and Auto-mode correctness

This beta scopes persisted request timestamps to the provider that made the
request. A Tankerkönig cooldown therefore no longer blocks a newly selected
Petromap or Nakordoni provider in Auto mode. A provider-bound cache is dropped
on a provider switch so prices from another provider cannot be presented as
current data.

Nakordoni OAuth-only config entries are recognized as configured in Auto mode;
Home Assistant's OAuth helper remains responsible for token refresh and
reauthentication. Nakordoni country/price coverage remains unknown unless
explicitly declared by the provider capability contract.

Diagnostics now include the effective provider, selection reason, provider
cooldown/retry timing, cache validity/provider, and credential mode without
including secrets or exact coordinates.

No live Home Assistant, VM 104, provider API, config-entry, merge, tag, or
release action was performed for this candidate.
