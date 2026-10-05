# Changelog

## 0.2.0 — Stable release

### Deutsch

- Native Lovelace-Custom-Card mit visuellem Editor und automatischer
  Stationszuordnung ergänzt.
- Apple-Karten-, Google-Maps- und Waze-Navigation über explizite Providerwahl;
  AUTO verwendet Apple auf iOS/iPadOS und Google auf Android/Desktop.
- Dynamische sichtbare Stationsnamen bei stabilen Entity-IDs und Unique-IDs.
- HTTP-500 beim Öffnen der Integrationsoptionen behoben und OptionsFlow an die
  aktuelle Home-Assistant-API angepasst.
- Keine Breaking Changes und keine Config-Entry-Migration gegenüber v0.1.0.
- Versionslose Lovelace-Resource:
  `/mobile_fuel_stations/mobile-fuel-stations-card.js`.
- Sygic und providerbezogenes visuelles Branding sind nicht Bestandteil von
  v0.2.0 und für eine spätere Version vorgemerkt.

### English

- Added a native Lovelace custom card with visual editor and automatic station
  discovery.
- Added Apple Maps, Google Maps, and Waze navigation through explicit provider
  selection; AUTO uses Apple on iOS/iPadOS and Google on Android/desktop.
- Dynamic visible station names while keeping entity IDs and unique IDs stable.
- Fixed the HTTP 500 when opening integration options and updated the
  OptionsFlow for the current Home Assistant API.
- No breaking changes and no config-entry migration from v0.1.0.
- Versionless Lovelace resource:
  `/mobile_fuel_stations/mobile-fuel-stations-card.js`.
- Sygic and provider-specific visual branding are not part of v0.2.0 and are
  deferred to a later version.

## 0.2.0-beta.4 — Vierter Beta-Stand

### Deutsch

- HTTP-500-Fehler beim Öffnen der Integrationsoptionen über das Zahnrad behoben.
- Options-Flow an die aktuelle Home-Assistant-API angepasst; bestehende
  Config-Entries benötigen keine Migration.
- Neue Regressionstests für bestehende Config-Entries, leere Optionen,
  Defaultwerte und geschützte API-Key-Daten ergänzt.
- Apple Maps Directions und Google Maps Directions statt einfacher Ortssuche.
- AUTO-Plattformerkennung sowie explizite Auswahl Automatisch / Apple Karten /
  Google Maps verbessert.
- Entity-IDs und Unique-IDs bleiben unverändert; bestehende YAML-Karten bleiben
  kompatibel.
- Der kanonische versionslose Resource-Pfad bleibt unverändert.

### English

- Fixed the HTTP 500 when opening integration options from the gear icon.
- Updated the options flow for the current Home Assistant OptionsFlow API;
  existing config entries require no migration.
- Added regression coverage for legacy entries, empty options, defaults, and
  protected API-key data.
- Switched Apple Maps and Google Maps navigation from place search to directions.
- Improved automatic platform detection and explicit Automatic / Apple Maps /
  Google Maps provider selection.
- Entity IDs and unique IDs remain unchanged; existing YAML cards stay
  compatible.
- The canonical versionless resource path remains unchanged.

This remains a beta release for controlled HACS/Home Assistant testing.

## 0.2.0-beta.3 — Dritter Beta-Stand

### Deutsch

- Apple-Karten-, Google-Maps- und automatische Navigation ergänzt.
- Verbesserte iOS-Navigation sowie dauerhafte versionslose Lovelace-Resource.
- Beta-2-Tester müssen die Resource einmalig auf
  `/mobile_fuel_stations/mobile-fuel-stations-card.js` umstellen.
- Brand-Deduplizierung und sichtbare aktuelle Tankstellennamen verbessert.
- Visuellen Editor um den Navigationsanbieter erweitert.
- Zusätzliche Frontend-/Backend-Tests sowie reproduzierbares Bundle ergänzt.

### English

- Added Apple Maps, Google Maps, and automatic navigation.
- Improved iOS navigation and introduced a durable versionless Lovelace resource.
- Beta-2 testers must change the resource once to
  `/mobile_fuel_stations/mobile-fuel-stations-card.js`.
- Improved brand de-duplication and current visible station names.
- Extended the visual editor with navigation-provider selection.
- Added frontend/backend coverage and a reproducible runtime bundle.

This remains a beta release. Client handling of map links and browser/Companion
caching can still vary by platform.

## Unreleased — Runde 4

### English

- Added automatic, Apple Maps, and Google Maps navigation providers with
  coordinate validation and a visual-editor selector.
- Switched the recommended Lovelace resource to the stable versionless URL.
- Improved Unicode/punctuation-aware brand de-duplication.
- Station-slot display names now follow the current station without changing
  entity IDs or unique IDs.

### Deutsch

- Automatische, Apple-Karten- und Google-Maps-Navigationsanbieter mit
  Koordinatenvalidierung und Auswahl im visuellen Editor ergänzt.
- Versionslose Lovelace-Resource-URL als dauerhafte Empfehlung eingeführt.
- Unicode-/satzzeichenfeste Brand-Deduplizierung verbessert.
- Anzeigenamen der Stations-Slots folgen nun der aktuellen Tankstelle, ohne
  Entity-IDs oder Unique-IDs zu ändern.

## 0.2.0-beta.2 — Second beta

### English

- Added a visual Lovelace card editor with overview-entity selection.
- Added a navigation toggle and station navigation buttons for valid
  coordinates; station taps still open `more-info`.
- Improved the mobile header and brand de-duplication.
- Made German documentation the default HACS repository view.
- Added frontend coverage for editor, navigation, coordinate validation,
  language labels, and brand handling.

Navigation behavior depends on the client/platform. The Lovelace resource still
requires one manual registration, and the final UI/navigation behavior remains
under real-device validation.

### Deutsch

- Visuellen Lovelace-Karteneditor mit Overview-Entity-Auswahl ergänzt.
- Navigationsschalter und Navigationsbuttons für gültige Koordinaten ergänzt;
  Stations-Taps öffnen weiterhin `more-info`.
- Mobilen Header und Brand-Deduplizierung verbessert.
- Deutsche Dokumentation als HACS-Standardansicht eingerichtet.
- Frontend-Tests für Editor, Navigation, Koordinatenvalidierung, Sprache und
  Brand-Verarbeitung erweitert.

Das Navigationsverhalten hängt von Client/Plattform ab. Die Lovelace-Resource
muss weiterhin einmal manuell registriert werden; UI und Navigation werden noch
auf realen Geräten validiert.

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
