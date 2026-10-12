# Mobile Fuel Stations v0.5.0-beta.11

## Highlights

- General options can be saved directly without opening credential management.
- An explicit **Manage credentials** step safely replaces or removes provider
  keys while empty fields preserve existing values.
- The first options page shows localized, non-secret status for each selected
  provider: stored but unchecked, successful runtime check, authentication
  failure, temporary unavailability, pending approval, no key, or not selected.
- Status is updated only by real provider requests and is reset after a key
  change; opening options does not perform network requests.
- Beta.10's multi-provider selection, per-fuel pricing, compact mobile card,
  stable entities, local branding, and migration behavior remain unchanged.

## Limitations

Nakordoni live API approval remains an external prerequisite. A stored key is
not claimed to be valid until a successful authenticated provider request has
actually completed.
