# Changelog

## 0.4.0-beta.1 — Nearest and cheapest station

### Deutsch

- Übersichtssensor stellt strukturierte Kandidaten für die nächste und
  günstigste offene Tankstelle bereit.
- Die Auswahl erfolgt aus der vollständigen Tankerkönig-Ergebnismenge vor der
  Begrenzung auf Stations-Slots.
- Die Dashboard-Karte zeigt beide Kandidaten oberhalb der bestehenden Liste.
- Der API-Radius wird auf die dokumentierten 25 km begrenzt; bestehende höhere
  Werte werden beim Request defensiv begrenzt.

### English

- The overview sensor provides structured candidates for the nearest and
  cheapest open station.
- Selection is performed on the complete Tankerkönig result set before station
  slots are limited.
- The dashboard card shows both candidates above the existing list.
- API requests are capped at the documented 25 km radius; existing higher
  values are handled defensively.

## 0.3.1 — Stable release

### Deutsch

- Behebt die Card-Picker-Regression, durch die Mobile Fuel Stations als leerer,
  dauerhaft ladender Eintrag erscheinen konnte.
- Vorhandene Overview-Entities werden für die initiale Kartenkonfiguration
  robust erkannt.
- Fehlende Overview-Entities werden kontrolliert behandelt, ohne den Picker
  zum Absturz zu bringen.

### English

- Fixed the Home Assistant card-picker regression that could show Mobile Fuel
  Stations as an empty, permanently loading entry.
- Existing overview entities are detected robustly for the initial card
  configuration.
- Missing overview entities are handled safely without crashing the picker.

## 0.3.1-beta.1 — Card-picker hotfix test release

### Deutsch

- Behebt einen Fehler, bei dem die Mobile Fuel Stations Card im Home-Assistant-
  Card-Picker als leerer, dauerhaft ladender Eintrag erscheinen konnte.
- `getStubConfig` erkennt vorhandene Overview-Entities für die initiale
  Kartenkonfiguration.
- Fehlende Overview-Entities werden im Picker kontrolliert behandelt, ohne den
  Picker zum Absturz zu bringen.

### English

- Fixed an issue where Mobile Fuel Stations could appear as an empty,
  permanently loading entry in the Home Assistant card picker.
- `getStubConfig` detects existing overview entities for the initial card
  configuration.
- Missing overview entities are handled without crashing the picker.

## 0.3.0 — Stable release

### Deutsch

- Dashboard-Karte wird nach HACS-Installation und Home-Assistant-Neustart
  automatisch durch die Integration registriert.
- Neuinstallationen benötigen keinen manuellen Lovelace-Resource-Eintrag.
- Upgrade-Hinweis für bestehende v0.2.x-Installationen: alten manuellen
  Resource-Eintrag erst nach Update, Neustart und erfolgreichem Funktionstest
  über die Home-Assistant-Oberfläche entfernen.
- Duplicate-Load-Schutz für die Übergangsphase bleibt enthalten.
- Apple Karten, Google Maps, Waze, visueller Editor und bestehende
  Integration-/Sensor-Entities bleiben unterstützt bzw. unverändert.
- Sygic, Navigationsprovider-Logos, Tankstellenmarkenlogos und Brand-Badges
  sind nicht Bestandteil dieser Version.

### English

- The dashboard card is automatically registered by the integration after HACS
  installation and a Home Assistant restart.
- New installations do not require a manual Lovelace resource entry.
- For existing v0.2.x installations, remove the old manual resource entry only
  after updating, restarting, and successfully testing the card.
- Duplicate-load protection remains available for the transition period.
- Apple Maps, Google Maps, Waze, the visual editor, and existing
  integration/sensor entities remain supported or unchanged.
- Sygic, navigation-provider logos, fuel-brand logos, and brand badges are not
  part of this release.

## 0.3.0-beta.1 — First v0.3.0 beta

### Deutsch

- Dashboard-Karte wird nach HACS-Installation und Home-Assistant-Neustart
  automatisch durch die Integration geladen.
- Neue Installationen benötigen keinen manuellen Lovelace-Resource-Eintrag.
- Schutz gegen doppeltes Laden der Karte und des visuellen Editors ergänzt.
- Nutzer von v0.2.0 oder älter sollen den bisherigen manuellen Resource-Eintrag
  erst nach erfolgreichem Update, Neustart und Funktionstest entfernen.
- Navigation bleibt auf Automatisch, Apple Karten, Google Maps und Waze begrenzt;
  Sygic und visuelles Branding sind nicht Bestandteil dieser Beta.

### English

- The dashboard card is automatically loaded by the integration after HACS
  installation and a Home Assistant restart.
- New installations no longer require a manual Lovelace resource entry.
- Added duplicate-load protection for the card and visual editor.
- Users upgrading from v0.2.0 or earlier should remove the existing manual
  resource only after a successful update, restart, and functional test.
- Navigation remains limited to Automatic, Apple Maps, Google Maps, and Waze;
  Sygic and visual branding are not part of this beta.

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
