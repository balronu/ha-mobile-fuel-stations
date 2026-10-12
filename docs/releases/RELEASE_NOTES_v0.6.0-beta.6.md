# Mobile Fuel Stations v0.6.0-beta.6

## Status

Prepared development version; not yet released. Stable `v0.5.1` and the
published beta `v0.6.0-beta.5` remain available as rollback versions.

## Changes

- Fixed local brand-logo matching for normalized variants and supported brand
  names embedded in station names.
- Preserved the generic gas-pump fallback for unknown brands, missing assets,
  and image-load errors.
- Archived historical release notes under `docs/releases/` using Git moves;
  their contents and release history are unchanged.
- Updated the compact project page and complete German/English documentation to
  reflect the implemented providers, startup recovery, polling, diagnostics,
  logos, privacy boundaries, and known limitations.

## Validation scope

Frontend logo tests cover bundled brands, aliases, station-name matching,
unknown values, safe URLs, and image-error fallback. Python tests cover static
asset registration and version synchronization. Full local and CI results are
reported separately; this prepared branch is not committed, pushed, merged, or
released by this task.
