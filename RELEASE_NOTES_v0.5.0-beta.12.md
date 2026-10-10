# Mobile Fuel Stations v0.5.0-beta.12

## Highlights

- Provider-specific authentication status now survives coordinator/options-flow
  reload boundaries and is updated by successful provider-owned requests.
- The first options page uses a more compact native Home Assistant layout:
  provider selection, automatic-mode/status description, credential management,
  and general settings remain in one flow.
- Added `assets/github-social-preview.png`, a 1280×640 repository preview based
  on the approved Mobile Fuel Stations logo.
- Updated the German and English README files for beta.12.

## Compatibility and limitations

- Existing config entries, credentials, entities, card resources, and local
  Home Assistant branding are preserved.
- Opening the options flow does not perform additional API requests.
- “API key stored” is not treated as successful authentication; only a
  successful request made through that provider records a successful check.
- Nakordoni live authorization remains an external prerequisite.
- GitHub does not apply a repository social-preview file automatically; upload
  it manually under **Settings → General → Social preview** if desired.
