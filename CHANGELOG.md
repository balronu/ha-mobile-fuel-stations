# Changelog

## 0.7.0-beta.2 — Protected Nakordoni diagnostics

- Add the administrator-only `mobile_fuel_stations.probe_nakordoni` service
  for one targeted Nakordoni request using the existing Home Assistant API-key
  or OAuth2 credential path.
- Keep the probe outside the coordinator, station cache, sensor state, and
  automatic provider selection; reject concurrent probes for one entry and do
  not retry automatically.
- Return only redacted status, quota, latency, station/price counts, price age,
  and coverage hints. API keys, tokens, raw payloads, station identities, and
  complete coordinates are excluded.
- Nakordoni OAuth remains experimental and has not been verified against a
  real live login.

## 0.6.1 — Stable release

- Promote the tested adaptive GPS refresh and persisted cooldown-cache recovery
  to the stable `v0.6.1` release.
- Keep adaptive updates disabled by default; when enabled, use validated GPS
  speed bands of 15, 5, 2, and 1 minute, subject to provider cooldowns and
  rate limits.
- Restore matching station data immediately after reload as `data_stale=true`
  and schedule one deduplicated provider refresh after cooldown expiry.
- Preserve existing config entries, provider selection, options, entities, and
  the independently versioned `0.6.0` frontend component.

## 0.6.1-beta.3 — Persisted startup cache and cooldown recovery

- Persist the last validated station result in the existing Home Assistant Store.
- Restore matching results as visibly stale data after reload/startup.
- Schedule one provider refresh after the Tankerkönig cooldown instead of
  exposing sensors as unavailable.
- Reject malformed or differently scoped cached data and clean up cooldown
  tasks during unload.

## 0.6.0 — Stable release

- Promote the validated beta.6 functionality to the stable `v0.6.0` release.
- Keep the six bundled brand logos reliable through normalized brand matching,
  station-name fallback, and a generic fallback for unknown brands.
- Include startup GPS recovery after approximately 3, 10, and 30 seconds,
  slower one-minute checks, bounded provider backoff, Retry-After handling,
  stale-cache preservation, and request deduplication.
- Preserve the Home Assistant Core polling lifecycle, movement refresh,
  provider selection, entity compatibility, and the complete German/English
  documentation.

## 0.6.0-beta.6 — Brand matching and repository documentation

- Resolve the six bundled logos from normalized brand variants and supported
  brand names when a provider leaves `brand` empty or verbose.
- Keep unknown brands and failed local assets on the generic pump fallback.
- Archive historical release notes under `docs/releases/` without changing
  their contents or release history.
- Refresh the German and English documentation and provider capability matrix.

## 0.6.0-beta.5 — Startup GPS recovery

- Add bounded startup recovery checks after approximately 3, 10, and 30
  seconds, followed by one-minute checks until GPS becomes available or the
  entry is unloaded.
- Track both state changes and state-reported GPS attribute updates so a
  tracker that keeps the same state string can still trigger recovery.
- Deduplicate startup, GPS-event, and timer triggers; preserve Core polling
  and movement refresh behavior.
- Add bounded transient-provider backoff with jitter, Retry-After enforcement,
  stale-cache preservation, and permanent-error termination.
- Extend secret-free diagnostics with recovery attempts, triggers, deadlines,
  GPS event metadata, in-flight state, and error classification.

## 0.6.0-beta.4 — Coordinator polling lifecycle fix

- Fix the collision with Home Assistant Core's `_schedule_refresh` method so
  the normal `DataUpdateCoordinator` polling timer remains Core-controlled.
- Delegate coordinator shutdown to Home Assistant Core after cancelling the
  integration's movement-recovery task and GPS listener.
- Report an explicit UNKNOWN polling-callback state while Core is refreshing,
  instead of claiming that periodic polling is absent.
- Add regression coverage for six listeners, three regular poll cycles after
  an initial GPS miss, scheduler preservation, shutdown cleanup, and diagnostics.
- Preserve provider selection, GPS recovery, stale-data behavior, frontend
  behavior, and bundled brand assets.

## 0.6.0-beta.3 — Coordinator lifecycle diagnostics

- Add safe runtime diagnostics for coordinator identity, listener registration,
  polling interval/scheduling, update/provider attempts, GPS listener state, and
  startup-recovery task state without exposing coordinates or credentials.
- Add lifecycle regression coverage for the actual Home Assistant coordinator
  listener registration path and repeated polling after an initial GPS miss.
- No speculative polling or retry behavior change is included because the live
  beta.2 root cause was not proven.

## 0.6.0-beta.2 — Startup recovery and safe logo defaults

- Close the startup race by re-checking the tracker after the initial setup
  refresh and scheduling exactly one deduplicated recovery refresh when GPS is
  already valid.
- Return unavailable data for missing GPS or a provider failure before the
  first result; reserve state `0` for a successful provider search with no
  matching stations.
- Cancel outstanding movement/recovery tasks and unsubscribe the GPS listener
  during unload.
- Enable brand-logo lookup for new cards by default while preserving an
  explicit `show_brand_logos: false` opt-out and all safe local-path checks.
- Bundle six sanitized, locally served SVG logos (Aral, Shell, JET,
  TotalEnergies, ORLEN, and OMV) with source URLs, SHA256 hashes, and explicit
  residual trademark-risk notes in `BRAND_LOGOS.md`.
- Keep unresolved provider brands on the gas-pump fallback; user-owned local
  overrides and the explicit `show_brand_logos: false` opt-out remain supported.

## 0.6.0-beta.1 — User-owned station brand logos

- Added provider-independent brand alias resolution from the existing `brand`
  attribute for Aral, Shell, Esso, JET, Total/TotalEnergies, HEM, AVIA,
  ORLEN, OMV, Q1, and Raiffeisen.
- Added opt-in `show_brand_logos` and configurable local `logo_path` options.
- Rendered user-owned logos in station rows and nearest/cheapest highlights with
  constrained aspect-ratio-safe layout, alt text, and image-error fallback.
- Rejected external logo URLs, traversal paths, and unsafe provider-derived
  filenames; no logo CDN or bundled third-party artwork is used.
- Stable `v0.5.1` behavior remains the default when logos are not enabled.
- Brand image rights remain the user's responsibility; the beta ships no brand
  artwork.
- Kept config-entry setup alive when the GPS tracker is temporarily unavailable
  or a provider has a transient startup failure; the first valid tracker state
  now schedules one automatic refresh without a manual integration reload.
- Added regression coverage for startup GPS recovery, transient provider
  recovery, listener deduplication, and repeated reload cleanup.

## [0.5.1] — Responsive card and load recovery

- Added a responsive layout using container queries and a single-column station list.
- Show the actual data source for each result and distinguish stale data from
  unavailable data, including automatic recovery when data becomes available again.
- Improved visible error diagnosis for provider and runtime failures.
- Added an idempotent custom-element registration fallback on the browser
  `load` event to recover from a frontend registry/load-order race.
- The sporadic Microsoft Edge/iOS Companion loading issue remains unverified
  in the production Home Assistant environment and is not claimed as fully fixed.
- Known `npm audit` warnings in development dependencies remain documented and
  were not addressed with an unreviewed major upgrade.

## [0.5.0] — Stable release

- Added multi-provider selection for Tankerkönig, Petromap, and Nakordoni with
  automatic selection limited to enabled and configured providers.
- Added support for simultaneous E5, E10, Diesel, LPG, and HVO100 selection,
  per-fuel price comparison, combined station cards, and stable station slots.
- Added separate credential management, safe key replacement/removal, and
  provider-specific access status based on actual provider requests.
- Added distance and explicit-fuel price sorting, nearest/cheapest highlights,
  navigation, compact responsive dashboard presentation, GPS movement updates,
  and E10-to-E5 fallback notices.
- Added the approved Home Assistant branding, repository social-preview asset,
  complete German/English documentation, and user-facing API-key guides.
- Preserved existing config entries, credentials, entity IDs, dashboard
  resources, provider fallbacks, and sensor compatibility.
- Nakordoni live authorization remains an external prerequisite.

## 0.5.0-beta.12 — Provider status and repository branding

- Carry the provider-status fix into the release so successful provider-owned
  requests are reflected after coordinator/options-flow reload boundaries.
- Keep provider status provider-specific: an unused provider remains untested,
  and opening the options flow does not trigger network requests.
- Reduce the first options-page description to compact provider-mode and access
  status lines while keeping the native Home Assistant form order.
- Add a 1280×640 GitHub social-preview asset based on the approved logo; the
  GitHub Settings upload remains a manual repository action.
- Update the German and English README files and the versioned card resource
  reference for beta.12. Nakordoni live authorization remains pending.

## 0.5.0-beta.11 — Separate credential management and provider status

- Save general options without forcing an API-key form; credential management
  is an explicit separate step.
- Show localized, non-secret provider status on the first options page.
- Persist only status and timestamp metadata from real provider requests;
  stored keys are never treated as validated automatically.
- Reset a provider's status after explicit key replacement or removal.
- Retain the beta.10 multi-provider, fuel, mobile-card, branding, and
  backwards-compatibility behavior.

## 0.5.0-beta.10 — Compact multi-provider mobile cards

- Kept the tested multi-provider checkbox flow and secure API-key status,
  replacement, removal, and beta.9 migration behavior.
- Reduced mobile station-card spacing while keeping names and addresses
  wrapping, prices/status visible, and navigation touch targets accessible.
- Merged nearest and per-fuel cheapest highlights for the same station only
  when its stable station identity matches; different stations remain separate.
- Added frontend regressions for highlight deduplication and long station
  details. Nakordoni live authorization remains provider-dependent.
- Reworked the German and English README files to document the beta.10
  provider coverage, API-key lifecycle, HACS setup, mobile card, privacy, and
  known limitations.

## 0.5.0-beta.9 — Non-blocking country initialization

- Load the offline country dataset once through Home Assistant's executor
  during config-entry setup, eliminating synchronous file reads from the event
  loop during coordinator refreshes.
- Cache failed or unavailable dataset loads as an empty result so repeated GPS
  updates fail open without repeated disk access.
- Retain the beta.8 options-flow translations, multi-fuel sorting behavior,
  responsive card, and approved local branding unchanged.
- Nakordoni live authorization remains provider-dependent.

## 0.5.0-beta.8 — Correct multi-fuel results and mobile presentation

- Stations are shown once with all available selected-fuel prices on one card.
- Nearest is distance-based; cheapest stations are calculated independently per fuel.
- Added explicit distance/price sorting and a required price-sorting fuel.
- Completed German and English flow labels and automatic provider mode for new installations.
- Included approved local branding and responsive mobile card improvements.
- Nakordoni live authorization remains provider-dependent.

## 0.5.0-beta.7 — Multi-fuel selection and provider-aware results

- Added selectable Super E5, Super E10, Diesel, LPG and HVO100 fuel types.
- Preserved legacy single-fuel configuration while storing canonical multi-fuel values.
- Added per-station fuel metadata, namespaced multi-provider station IDs and explicit E10-to-E5 fallback metadata.
- Extended the frontend card to show the selected fuel per station and multi-fuel summaries.
- Nakordoni remains implemented behind its documented, externally blocked live authorization; no unverified HVO100 capability is enabled.

## 0.5.0-beta.6 — Nakordoni failure diagnostics

- Added safe Nakordoni rate, quota, permission, and first-refresh diagnostics.
- No additional provider requests, credentials, or location data are stored or logged.

## 0.5.0-beta.5 — Nakordoni provider

- Added explicit Nakordoni support for diesel, E5, E10 and LPG.
- Added persistent Nakordoni credentials, privacy consent and provider-specific reauthentication.
- Added one-request nearby searches with price timestamps, stale metadata and quota headers.
- Added conditional `Data by nakordoni.eu` attribution in the dashboard card.
- Nakordoni is not part of Auto mode in this beta; HVO100 and multi-provider selection remain unsupported.

## 0.5.0-beta.4 — ConfigEntry migration version persistence

- Fixed persistence of the ConfigEntry version during the 1→2 migration.
- No provider or runtime behavior changes.

## 0.5.0-beta.3 — Atomic options and provider reloads

- Options changes now become active immediately after saving.
- Provider switches reload using the final persisted configuration.
- Fixed stale runtime state where saved LPG/provider settings could leave the previous coordinator active.

## 0.5.0-beta.2 — LPG fuel support

### Deutsch

- Petromap-LPG / Autogas ist als eigener Kraftstoff mit `fuelFamily=lpg`
  verfügbar.
- Tankerkönig wird für LPG nicht als unterstützt markiert.
- HVO100 bleibt blockiert, weil kein verifizierter providerbezogener
  API-Selektor vorliegt; es gibt keinen Diesel-Fallback.

### English

- Petromap LPG / Autogas is available as a distinct fuel using
  `fuelFamily=lpg`.
- Tankerkönig is not marked as LPG-capable.
- HVO100 remains blocked because no verified provider-specific API selector is
  available; no diesel fallback is used.

## 0.5.0-beta.2 — Provider UX

### Deutsch

- Die Geräteherstelleranzeige folgt jetzt dem konfigurierten Modus: Tankerkönig,
  Petromap oder eine stabile neutrale Anzeige für Auto.
- Providerwechsel sind über den Options Flow möglich, ohne Device-Identifier,
  Entity-IDs oder Unique-IDs zu verändern.
- Providerwechsel zeigen vor der ersten Petromap-Aktivierung die Privacy
  Disclosure und speichern nur die für den Zielmodus erforderlichen Credentials.
- Der Wechsel führt keine Petromap-Netzwerkrequests aus; die bestehende Runtime-
  und Request-Semantik bleibt unverändert.

### English

- Device manufacturer information now follows the configured mode: Tankerkönig,
  Petromap, or a stable neutral label for Auto.
- Provider switching is available through the options flow without changing
  device identifiers, entity IDs, or unique IDs.
- Switching to a Petromap-capable mode shows the privacy disclosure first and
  stores only the credentials required by the target mode.
- Switching performs no Petromap network request; existing runtime and request
  semantics remain unchanged.

## 0.5.0-beta.1 — Beta release

### Deutsch

- Provider-Abstraktion und Petromap-v2-Runtime-Unterstützung ergänzt.
- Offline-Country-Resolver und automatische Provider-Auswahl eingeführt:
  Deutschland nutzt Tankerkönig; Österreich nutzt Petromap für Diesel und E5.
- Auto-Einträge speichern getrennte Tankerkönig- und Petromap-Credentials.
- Privacy Disclosure und provider-spezifische Reauth-Flows bleiben erhalten.
- Petromap-Runtime verwendet pro Refresh höchstens eine Places-Seite; kein
  `/usage`-Aufruf im normalen Runtime-Refresh.
- AT/E10 bleibt in dieser Beta bewusst vor dem Netzwerk blockiert.
- Petromap runtime support is included in beta; real-world API access depends
  on the permissions of the configured Petromap developer key.

### English

- Added provider abstraction and Petromap v2 runtime support.
- Added the offline country resolver and automatic provider selection:
  Germany uses Tankerkönig; Austria uses Petromap for diesel and E5.
- Auto entries store separate Tankerkönig and Petromap credentials.
- Privacy disclosure and provider-specific reauthentication flows remain in
  place.
- Petromap runtime uses at most one Places page per refresh; normal runtime
  refreshes never call `/usage`.
- AT/E10 remains deliberately blocked before the network in this beta.
- Petromap runtime support is included in beta; real-world API access depends
  on the permissions of the configured Petromap developer key.

## 0.4.0 — Stable release

### Deutsch

#### Added

- Die Karte zeigt die nächste offene und die günstigste offene Tankstelle als
  getrennte Highlights.
- Beide Kandidaten werden aus der vollständigen Tankerkönig-Ergebnismenge vor
  der Begrenzung auf Stations-Slots bestimmt.
- Die Highlight-Navigation funktioniert auch für eine nächste Tankstelle
  außerhalb der sichtbaren Stations-Slots.

#### Changed

- Neue Tankerkönig-Radiuswerte sind auf das dokumentierte Maximum von 25 km
  begrenzt.
- Bereits gespeicherte größere Werte bleiben ladbar; API-Anfragen werden auf
  maximal 25 km begrenzt.
- Die automatisch registrierte Frontend-URL ist versionsabhängig und verhindert
  veralteten Card-JavaScript-Code nach Integrations-Updates.

#### Compatibility

- Keine neuen Entities oder Unique IDs.
- Bestehende Stations-Slots, Konfigurationen und Navigation bleiben kompatibel.
- Ein manueller Lovelace-Resource-Eintrag ist nicht erforderlich.

### English

#### Added

- The card shows separate highlights for the nearest open and cheapest open
  station.
- Both candidates are calculated from the complete Tankerkönig result set
  before the configured station-slot limit is applied.
- Highlight navigation also works when the nearest station is outside the
  visible station slots.

#### Changed

- New Tankerkönig radius values are limited to the documented maximum of 25 km.
- Existing larger stored values remain loadable; API requests are capped at
  25 km.
- The automatically registered frontend URL is versioned to prevent stale card
  JavaScript after integration updates.

#### Compatibility

- No new entities or unique IDs.
- Existing station slots, configurations, and navigation remain compatible.
- No manual Lovelace resource entry is required.

## 0.4.0-beta.2 — Versioned frontend URL

### Deutsch

- Die automatisch registrierte Frontend-URL enthält jetzt die
  Integrationsversion und verhindert dadurch veralteten JavaScript-Code nach
  einem Update.
- Ein manueller Lovelace-Resource-Eintrag ist weiterhin nicht erforderlich.

### English

- The automatically registered frontend URL now includes the integration
  version to prevent stale dashboard JavaScript after an update.
- No manual Lovelace resource entry is required.

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
