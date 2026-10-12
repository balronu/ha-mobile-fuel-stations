# Mobile Fuel Stations v0.6.0

## Deutsch 🇩🇪

`v0.6.0` ist die stabile Veröffentlichung von Mobile Fuel Stations. Die
validierten Änderungen aus Beta.1 bis Beta.6 sind enthalten; das Provider-
Backend und die bestehenden Home-Assistant-Konfigurationsschnittstellen
bleiben kompatibel.

### Funktionen und Verbesserungen

- Tankstellen über Tankerkönig, Petromap und Nakordoni mit aktivierter,
  konfigurierter Provider-Auswahl und begrenztem Fallback.
- Gleichzeitige Auswahl von E5, E10, Diesel, LPG und HVO100, soweit Provider
  und Länder-Capability konkrete Daten liefern.
- Startup-Recovery nach ungefähr 3, 10 und 30 Sekunden, danach langsame
  Prüfungen ungefähr alle 60 Sekunden, wenn GPS beim Start fehlt.
- GPS-Events und zeitgesteuerte Prüfungen decken verpasste Events sowie reine
  Attributänderungen ab; Recovery-Anfragen werden dedupliziert.
- Temporäre Providerfehler mit begrenztem exponentiellem Backoff, Jitter,
  `Retry-After`-/Rate-Limit-Beachtung und Erhalt gültiger stale Cachedaten.
- Normales Home-Assistant-Core-Polling ungefähr alle 15 Minuten und
  bewegungsabhängige Aktualisierung bleiben erhalten.
- Lovelace-Karte mit Preisen, Entfernung, Öffnungsstatus, Preisalter,
  Navigation und E5/E10-Ersatzhinweisen.
- Lokale Erkennung von Aral, Shell, JET, Total/TotalEnergies, ORLEN und OMV
  durch Normalisierung von Markennamen und Stationsnamen-Fallback.
- Generisches Zapfsäulensymbol für unbekannte Marken, fehlende Assets oder
  Bildfehler.
- Erweiterte, geheimnisfreie Diagnostics sowie vollständige deutsche und
  englische Dokumentation.

### Provider und Zugang

Tankerkönig ist für Deutschland mit Diesel, E5 und E10 implementiert.
Petromap liefert belegte Stationspreis-Capabilities für Deutschland und
Österreich mit Diesel, E5 und LPG; weitere Daten hängen vom Anbieter ab.
Nakordoni unterstützt das implementierte Modell für Diesel, E5, E10 und LPG;
Marktfreigabe, Quoten und Live-Abdeckung sind kontoabhängig. Für aktivierte
Provider werden eigene API-Schlüssel und die jeweiligen Anbieterfreigaben
benötigt. Koordinaten, Radius und Kraftstoffauswahl können an externe APIs
übertragen werden.

### Upgrade und Einschränkungen

Vor dem Update ein Home-Assistant-Backup erstellen und Home Assistant nach dem
HACS-Update neu starten. Bestehende Config Entries, Zugangsdaten, Entity-IDs
und kompatible Dashboard-Ressourcen bleiben erhalten. `v0.5.1` bleibt als
vorherige Stable-Rollback-Version verfügbar; `v0.6.0-beta.6` bleibt als letzter
Release Candidate im Archiv erhalten. Providerabdeckung, Preise, Quoten,
Nakordoni-Marktfreigaben und HVO100-Preise sind externe Einschränkungen.

## English 🇬🇧

`v0.6.0` is the stable Mobile Fuel Stations release. It includes the validated
changes from beta.1 through beta.6. The provider backend and existing Home
Assistant configuration interfaces remain compatible.

### Features and improvements

- Tankerkönig, Petromap, and Nakordoni with enabled/configured provider
  selection and bounded fallback.
- Simultaneous E5, E10, diesel, LPG, and HVO100 selection where the provider
  and country capability return concrete data.
- Startup recovery after approximately 3, 10, and 30 seconds, followed by
  slower approximately one-minute checks when GPS is missing at startup.
- GPS events and timed checks cover missed events and attribute-only changes;
  recovery requests are deduplicated.
- Transient provider failures use bounded exponential backoff, jitter,
  `Retry-After`/rate-limit handling, and preservation of valid stale cache data.
- Normal Home Assistant Core polling at approximately 15-minute intervals and
  movement-triggered refreshes remain enabled.
- Lovelace card with prices, distance, opening status, price age, navigation,
  and E5/E10 substitution hints.
- Local matching for Aral, Shell, JET, Total/TotalEnergies, ORLEN, and OMV by
  normalizing brand names and falling back to the station name.
- Generic fuel-pump fallback for unknown brands, missing assets, or image
  errors.
- Extended secret-free diagnostics and complete German/English documentation.

### Providers and access

Tankerkönig is implemented for Germany with diesel, E5, and E10. Petromap has
verified station-price capabilities for Germany and Austria with diesel, E5,
and LPG; further data depends on the provider. Nakordoni implements diesel,
E5, E10, and LPG; market approval, quotas, and live coverage are account-
dependent. Enabled providers require their own API keys and any provider
approval. Coordinates, radius, and fuel selection may be sent to external APIs.

### Upgrade and limitations

Create a Home Assistant backup before updating and restart Home Assistant after
the HACS update. Existing config entries, credentials, entity IDs, and
compatible dashboard resources are retained. `v0.5.1` remains available as the
previous stable rollback; `v0.6.0-beta.6` remains archived as the last release
candidate. Provider coverage, prices, quotas, Nakordoni market approval, and
HVO100 prices remain external limitations.
