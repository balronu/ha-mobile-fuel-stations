# Changelog

## 0.2.0-beta.1 — Beta preview

### English

- Beta preview of `custom:mobile-fuel-stations-card`.
- Responsive, mobile-first display with price, distance, open/closed status,
  address, HA theme support, and station tap to `more-info`.
- Automatic station discovery through the additive `station_entities`
  overview attribute.
- Frontend bundle delivered with the HACS integration and deterministic cache
  versioning.
- No breaking configuration changes; existing v0.1.0 config entries remain
  compatible.

Known limitations: the Lovelace resource must currently be registered manually
once, there is no navigation adapter, and there is no visual card editor. This
is a beta release intended for testing.

### Deutsch

- Beta-Vorschau der `custom:mobile-fuel-stations-card`.
- Responsive Mobile-first-Darstellung mit Preis, Entfernung, Öffnungsstatus,
  Adresse, HA-Theme-Unterstützung und Stations-Tap für `more-info`.
- Automatische Stations-Erkennung über das additive Overview-Attribut
  `station_entities`.
- Frontend-Bundle wird mit der HACS-Integration ausgeliefert und deterministisch
  über die Versions-URL gecacht.
- Keine Breaking Changes; bestehende v0.1.0-Config-Entries bleiben kompatibel.

Bekannte Einschränkungen: Die Lovelace-Resource muss derzeit einmal manuell
registriert werden; Navigation und visueller Karteneditor sind noch nicht
enthalten. Diese Beta dient dem Test.

## 0.1.0

- Initial development release.
- Tankerkönig provider with dynamic latitude/longitude searches.
- Configurable diesel, E5, and E10 fuel types, radius, and station count.
- Regular polling with optional movement-triggered refreshes.
- Configurable movement threshold and cooldown.
- Overview sensor and stable station-slot sensors.
- Station prices, opening status, addresses, distances, and coordinates.
- Config flow, options flow, diagnostics, English/German translations, tests,
  and HACS custom-repository support.
- Standard and optional Mushroom dashboard examples.
- Platform-agnostic navigation documentation; no navigation-provider
  dependency is included.
