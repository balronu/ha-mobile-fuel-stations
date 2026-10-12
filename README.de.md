# Mobile Fuel Stations – Deutsche Anleitung

🇩🇪 **Deutsch** ([Hauptseite](README.md)) | [🇬🇧 English](README.en.md)

Mobile Fuel Stations ist eine Home-Assistant-Custom-Integration für nahe
Tankstellen anhand der Koordinaten einer Fahrzeug-, Wohnmobil- oder
Geräte-Entity. Sie stellt Stationssensoren und eine responsive Lovelace-Karte
mit Preisen, Entfernung, Öffnungsstatus und Navigation bereit.

## Inhaltsübersicht

- [Versionen und Funktionsumfang](#versionen-und-funktionsumfang)
- [Installation über HACS](#installation-über-hacs)
- [Einrichtung und Konfiguration](#einrichtung-und-konfiguration)
- [Provider, Länder und Kraftstoffe](#provider-länder-und-kraftstoffe)
- [API-Schlüssel](#api-schlüssel)
- [GPS, Polling und Startup-Recovery](#gps-polling-und-startup-recovery)
- [Lovelace-Karte und Markenlogos](#lovelace-karte-und-markenlogos)
- [Preise, Sortierung und Navigation](#preise-sortierung-und-navigation)
- [Updates und Migration](#updates-und-migration)
- [Datenschutz und Einschränkungen](#datenschutz-und-einschränkungen)
- [Fehlerbehebung und Diagnostics](#fehlerbehebung-und-diagnostics)
- [Entwicklung und Tests](#entwicklung-und-tests)
- [Release-Archiv](#release-archiv)

## Versionen und Funktionsumfang

| Kanal | Version | Bedeutung |
| --- | --- | --- |
| Stable | `v0.5.1` | Empfohlene stabile Version |
| Pre-Release | `v0.6.0-beta.6` | Aktuelle veröffentlichte Beta |
| Rollback | `v0.6.0-beta.5` | Vorherige Beta bleibt verfügbar |

`v0.6.0` ohne Beta-Suffix ist noch nicht als Stable veröffentlicht. Beta.6
verbessert die Erkennung der sechs lokalen Markenlogos und aktualisiert die
Dokumentation. Provider-Backend, Startup-Recovery und reguläres Polling sind
gegenüber Beta.5 unverändert.

Enthalten sind Tankstellen im Suchradius, E5, E10, Diesel, LPG/Autogas und
HVO100, Mehrfachauswahl, Entfernung- und Preissortierung, stabile Sensoren,
automatische Providerauswahl, Startup-Recovery, reguläres Polling,
Bewegungsupdates, Navigation und eine mobile Lovelace-Karte.

## Installation über HACS

1. **HACS → Integrationen** öffnen.
2. Nach **Mobile Fuel Stations** suchen. Falls das Repository fehlt, unter
   **Benutzerdefinierte Repositories**
   `https://github.com/balronu/ha-mobile-fuel-stations` als **Integration**
   hinzufügen.
3. Installieren und Home Assistant vollständig neu starten.
4. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen**
   **Mobile Fuel Stations** wählen.

Beta.6 ist ein Pre-Release. Aktiviere gegebenenfalls Beta-Versionen in HACS.
Stable bleibt `v0.5.1`. Die technische Beschreibung der Kartenressource steht
in [docs/RESOURCE_LOADING.md](docs/RESOURCE_LOADING.md). Für Beta.6 lautet die
versionierte Resource-URL:

```text
/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.6.0-beta.6
```

## Einrichtung und Konfiguration

Der Flow fragt eine Entity mit `latitude` und `longitude`, Radius, 1 bis 10
Stationsplätze, Kraftstoffarten, Provider oder **Automatisch**, Sortierung,
Polling-Intervall, Bewegungsschwelle, Cooldown und Navigation ab. Allgemeine
Optionen und Zugangsdaten werden getrennt gespeichert. Ein leeres Credential-
Feld lässt einen vorhandenen Schlüssel unverändert; vollständige Schlüssel
werden nie angezeigt.

## Provider, Länder und Kraftstoffe

Diese Matrix entspricht den im Code und in Tests belegten Capabilities. Externe
Verträge, Quoten und Kontoberechtigungen können die Live-Verfügbarkeit ändern.

| Provider | Zugang | Belegte Abdeckung und Kraftstoffe |
| --- | --- | --- |
| [Tankerkönig](https://onboarding.tankerkoenig.de/) | API-Key | Deutschland; Diesel, E5, E10; maximal 25 km API-Radius |
| [Petromap](https://developer.petromap.eu/) | API-Key, gegebenenfalls Freigabe | Stationspreise in Deutschland und Österreich für Diesel, E5 und LPG; weitere Daten hängen von Petromap ab |
| [Nakordoni](https://nakordoni.eu/en/developers) | API-Key und Markt-/Zugangsfreigabe | Diesel, E5, E10 und LPG im implementierten API-Modell; Länder und Live-Abdeckung konto- und marktabhängig |

Auswählbar sind `e5`, `e10`, `diesel`, `lpg` und `hvo100`. Ein Provider wird
nur verwendet, wenn Capability und Antwort den Kraftstoff unterstützen. HVO100
wird nicht still als Diesel ausgegeben. Preise erscheinen nur bei verifizierter
Provider-/Länder-Capability. Im Automatikmodus werden nur aktivierte und
konfigurierte Provider betrachtet. E10 kann bei ausdrücklich unterstützter
Capability als E5-Ersatz angezeigt werden; das gilt nicht für Diesel, LPG oder
HVO100.

## API-Schlüssel

Für jeden aktivierten Provider wird ein eigener Zugang benötigt. Registrierung,
Freigabe, Quoten, Kosten und Bedingungen legt der Anbieter fest.

- [Tankerkönig-Onboarding](https://onboarding.tankerkoenig.de/)
- [Petromap Developer Portal](https://developer.petromap.eu/)
- [Nakordoni Developer Portal](https://nakordoni.eu/en/developers)

Nach der Registrierung den Schlüssel unter **Einstellungen → Geräte & Dienste
→ Mobile Fuel Stations → Konfigurieren → Zugangsdaten verwalten** eintragen.
Ein gespeicherter Schlüssel ist noch kein erfolgreicher Live-Test. Der
Optionsdialog startet keine unnötigen Netzwerkanfragen. Schlüssel werden nicht
in Git, Logs oder Diagnostics gespeichert.

## GPS, Polling und Startup-Recovery

Die Standort-Entity muss gültige Koordinaten liefern. Nach dem Start werden die
Entities angelegt und der normale Coordinator-Refresh versucht. Fehlt GPS,
prüft die Recovery ungefähr nach 3, 10 und 30 Sekunden erneut. Danach folgen
ungefähr alle 60 Sekunden Prüfungen, bis GPS verfügbar ist oder entladen wird.

Ein passendes GPS-Event kann den nächsten Versuch sofort beschleunigen. Die
Timer bleiben aktiv, damit verpasste `state_changed`-Events und reine
Attributänderungen nicht bis zum nächsten 15-Minuten-Zyklus warten. Alle
Recovery-Trigger laufen über einen deduplizierten Pfad; Recovery und reguläres
Polling stellen keine parallelen Provider-Anfragen.

Temporäre Providerfehler verwenden begrenzten exponentiellen Backoff mit
Jitter. `Retry-After` und Rate-Limits haben Vorrang. Permanente Authentifizierungs-
oder Konfigurationsfehler werden diagnostiziert und nicht aggressiv wiederholt.
Gültige Cachedaten bleiben bei temporären Fehlern erhalten und werden als stale
markiert. Nach Erfolg endet die Recovery; 15-Minuten-Polling und Movement-
Refresh bleiben aktiv. Timer, Tasks und Listener werden bei Reload/Unload
aufgeräumt.

## Lovelace-Karte und Markenlogos

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations
navigation: true
show_brand_logos: true
```

Die sechs lokalen SVGs sind Aral (`aral.svg`), Shell (`shell.svg`), JET
(`jet.svg`), Total/TotalEnergies (`total.svg`), ORLEN/ORLEN Express
(`orlen.svg`) und OMV (`omv.svg`). Groß-/Kleinschreibung, Akzente,
Leerzeichen und Satzzeichen werden normalisiert. Fehlt `brand` oder passt es
nicht, wird zusätzlich der Stationsname geprüft. Unbekannte, leere oder nicht
ladbare Logos fallen auf das generische Zapfsäulensymbol zurück.

`show_brand_logos: false` deaktiviert Logos. Quellen und Prüfsummen stehen in
[docs/BRAND_LOGOS.md](docs/BRAND_LOGOS.md). Eigene lokale SVGs können unter
`/config/www/fuel-logos/` liegen und über `/local/...` verwendet werden;
unsichere Pfade und externe URLs werden abgelehnt.

Die Karte zeigt Name, Adresse, Entfernung, Öffnungsstatus, Preisalter,
verfügbare Preise, Ersatzhinweise und Navigation.

## Preise, Sortierung und Navigation

Standard ist Entfernung aufsteigend. Preissortierung benötigt eine eindeutig
gewählte Kraftstoffart; Stationen ohne gültigen Preis stehen am Ende.
Kraftstoffarten werden nie in einer Rangliste vermischt und fehlende Preise
nicht durch einen anderen Kraftstoff ersetzt. Je nach Konfiguration sind Apple
Maps, Google Maps, Waze oder automatische Navigation möglich.

## Updates und Migration

Vor dem Update ein Home-Assistant-Backup erstellen, über HACS aktualisieren
und Home Assistant vollständig neu starten. Config Entries, Credentials,
Sensoren und kompatible Dashboard-Konfigurationen bleiben erhalten. Nach einem
größeren Update die versionierte Kartenressource und den Browser-Cache prüfen.
Beta.5 bleibt als Rollback verfügbar; `v0.5.1` bleibt Stable und `v0.6.0`
Stable ist noch nicht veröffentlicht.

## Datenschutz und Einschränkungen

Je nach Provider können Koordinaten, Radius und Kraftstoffauswahl an externe
APIs gesendet werden. Datenschutzbedingungen der Provider beachten. Es wird
keine Geräte-ID an Nakordoni gesendet; vollständige API-Keys und exakte private
Koordinaten erscheinen nicht in Diagnostics. Bei Nakordoni muss die Attribution
**Data by nakordoni.eu** sichtbar bleiben.

Providerabdeckung, Preise, Öffnungszeiten, Quoten und Berechtigungen können
sich ändern. Nakordoni-Märkte und HVO100-Preise sind nicht pauschal garantiert.

## Fehlerbehebung und Diagnostics

- **Keine Tankstellen:** Entity, Koordinaten, Radius, Provider und Zugang prüfen.
- **GPS unavailable:** Recovery-Status, Versuchszähler und nächsten Retry prüfen.
- **Preis fehlt:** Für Station und Kraftstoff wurde kein gültiger Preis geliefert.
- **Providerfehler:** Dauerhafte Auth-/Konfigurationsfehler beheben; bei
  temporären Fehlern Cache und stale-Markierung beachten.
- **Logo fehlt:** `brand`, Stationsname, `show_brand_logos`, Resource-Version
  und Browser-Cache prüfen.

Diagnostics enthalten Recovery-Status, Versuchszähler, letzten Trigger, nächsten
Retry, GPS-Eventtyp/-zeit, In-Flight-Status und Fehlerklasse, aber keine
Koordinaten, Tokens oder vollständigen Schlüssel.

## Entwicklung und Tests

```bash
python -m pytest
cd frontend && npm ci && npm test -- --run && npm run typecheck && npm run build
python -m compileall custom_components tests
```

Die CI prüft zusätzlich Hassfest, Home-Assistant-Kompatibilität, Bundle-/Diff-
Synchronität, Markdown-/Versionskonsistenz und Secret-Scanning. Provider- und
Recovery-Tests verwenden Mocks und Fixtures, keine ungeprüften Live-Schlüssel.

## Release-Archiv

Historische Release Notes liegen unverändert unter
[`docs/releases/`](docs/releases/), einschließlich
[`RELEASE_NOTES_v0.6.0-beta.6.md`](docs/releases/RELEASE_NOTES_v0.6.0-beta.6.md).
Weitere Informationen: [CONTRIBUTING.md](CONTRIBUTING.md),
[docs/BRAND_LOGOS.md](docs/BRAND_LOGOS.md) und das
[GitHub-Release-Archiv](https://github.com/balronu/ha-mobile-fuel-stations/releases).
