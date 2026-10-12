# Mobile Fuel Stations

🇩🇪 **Deutsch** | [🇬🇧 English](README.en.md)

<p align="center"><img src="assets/branding/logo.png" alt="Mobile Fuel Stations" width="220"></p>

Mobile Fuel Stations ist eine Home-Assistant-Custom-Integration für nahe
Tankstellen. Sie verwendet die Positionsdaten einer Fahrzeug-,
Wohnmobil- oder Geräte-Entity und stellt Tankstellen, Preise, Entfernung,
Öffnungsstatus und Navigation als Sensoren und Lovelace-Karte bereit.

> Diese README ist die ausführliche deutsche Hauptanleitung. Eine vollständige
> englische Fassung steht unter [README.en.md](README.en.md); die identische
> deutsche Sprachfassung steht unter [README.de.md](README.de.md).

## Inhaltsübersicht

- [Versionen und Funktionsumfang](README.md#versionen-und-funktionsumfang)
- [Installation über HACS](README.md#installation-über-hacs)
- [Einrichtung und Konfiguration](README.md#einrichtung-und-konfiguration)
- [Provider, Länder und Kraftstoffe](README.md#provider-länder-und-kraftstoffe)
- [API-Schlüssel](README.md#api-schlüssel)
- [GPS, Polling und Startup-Recovery](README.md#gps-polling-und-startup-recovery)
- [Lovelace-Karte und Markenlogos](README.md#lovelace-karte-und-markenlogos)
- [Preise, Sortierung und Navigation](README.md#preise-sortierung-und-navigation)
- [Updates und Migration](README.md#updates-und-migration)
- [Datenschutz und Einschränkungen](README.md#datenschutz-und-einschränkungen)
- [Fehlerbehebung und Diagnostics](README.md#fehlerbehebung-und-diagnostics)
- [Entwicklung und Tests](README.md#entwicklung-und-tests)
- [Release-Archiv](README.md#release-archiv)

## Versionen und Funktionsumfang

| Kanal | Version | Bedeutung |
| --- | --- | --- |
| Stable | `v0.6.0` | Aktuelle stabile Version |
| Vorherige Stable | `v0.5.1` | Verfügbare Rollback-Version |
| Letzter Release Candidate | `v0.6.0-beta.6` | Vorangegangene Beta |

`v0.6.0` ist die aktuelle stabile Veröffentlichung. Sie enthält die aus Beta.6
übernommene verbesserte lokale Erkennung der sechs gebündelten Markenlogos und
die überarbeitete Dokumentation. Provider-Backend, Startup-Recovery und das
reguläre Polling entsprechen dem geprüften Beta.5/Beta.6-Stand.

Die Integration bietet unter anderem:

- Tankstellen im konfigurierten Suchradius anhand einer Tracker-Entity
- E5, E10, Diesel, LPG/Autogas und HVO100 als auswählbare Kraftstoffarten
- Mehrfachauswahl von Kraftstoffen, wenn die ausgewählten Provider diese Daten
  liefern
- Sortierung nach Entfernung oder dem Preis einer gewählten Kraftstoffart
- Stationssensoren mit Name, Adresse, Entfernung, Preisen, Preisalter und
  Öffnungsstatus
- automatische Provider-Auswahl und begrenzten Fallback nach Capability,
  Land, Zugang und Datenverfügbarkeit
- Startup-Recovery bei verspätetem GPS oder vorübergehend nicht verfügbarem
  Provider
- reguläres DataUpdateCoordinator-Polling und bewegungsabhängige Updates
- responsive Lovelace-Karte mit Navigation und Markenlogo-Fallback

## Installation über HACS

1. Öffne **HACS → Integrationen**.
2. Suche nach **Mobile Fuel Stations**. Falls das Repository nicht gelistet
   ist, füge `https://github.com/balronu/ha-mobile-fuel-stations` unter
   **Benutzerdefinierte Repositories** als Typ **Integration** hinzu.
3. Installiere die Integration.
4. Starte Home Assistant vollständig neu, wie von HACS verlangt.
5. Öffne **Einstellungen → Geräte & Dienste → Integration hinzufügen** und
   wähle **Mobile Fuel Stations**.

`v0.6.0` ist die stabile HACS-Version. Beta.6 bleibt als letzter Release
Candidate und Rollback-Referenz im GitHub-Archiv erhalten. Für einen Rücksprung
steht `v0.5.1` als vorherige Stable-Version zur Verfügung.

Die Lovelace-Karte wird von der Integration bereitgestellt und registriert. Die
versionierte Ressource lautet für Stable v0.6.0:

```text
/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.6.0
```

Bei einer bestehenden Installation können alte Ressourcen im Browser- oder
Frontend-Cache liegen; nach einem Update hilft ein vollständiger Home-Assistant-
Neustart und ein Neuladen des Browsers. Die technische Ladebeschreibung steht
in [docs/RESOURCE_LOADING.md](docs/RESOURCE_LOADING.md).

## Einrichtung und Konfiguration

Im Konfigurationsdialog werden typischerweise gewählt:

- eine Entity mit `latitude` und `longitude` (zum Beispiel ein Fahrzeug-Tracker)
- Suchradius und maximale Anzahl der Stationen (1 bis 10)
- eine oder mehrere Kraftstoffarten
- einer oder mehrere Provider beziehungsweise **Automatisch**
- Sortierung nach Entfernung oder Kraftstoffpreis
- Polling-Intervall sowie Bewegungsschwelle und Cooldown
- gewünschter Navigationsdienst der Karte

Die allgemeinen Optionen werden separat von den Zugangsdaten gespeichert.
Unter **Zugangsdaten verwalten** können Provider-Schlüssel ersetzt oder
ausdrücklich entfernt werden. Ein leeres Feld lässt einen vorhandenen Schlüssel
unverändert. Die Oberfläche zeigt nur nicht-sensitive Zugangsstatus, niemals
vollständige Schlüssel.

## Provider, Länder und Kraftstoffe

Die folgende Matrix beschreibt die im Code und in den Tests belegte
Implementierung. Externe API-Verträge, Quoten und Berechtigungen können die
tatsächliche Verfügbarkeit einschränken.

| Provider | Zugang | Belegte Abdeckung und Kraftstoffe |
| --- | --- | --- |
| [Tankerkönig](https://onboarding.tankerkoenig.de/) | API-Key | Deutschland; Diesel, E5 und E10; API-Radius maximal 25 km |
| [Petromap](https://developer.petromap.eu/) | API-Key und gegebenenfalls Freigabe | Stationspreise in Deutschland und Österreich für Diesel, E5 und LPG; weitere Länder beziehungsweise nationale Daten hängen von Petromap ab |
| [Nakordoni](https://nakordoni.eu/en/developers) | API-Key, Markt-/Zugangsfreigabe | Diesel, E5, E10 und LPG im implementierten API-Modell; Länder- und Live-Abdeckung ist konto- und marktabhängig |

Die auswählbaren Kraftstoffschlüssel sind `e5`, `e10`, `diesel`, `lpg` und
`hvo100`. Ein Provider wird nur dann für einen Kraftstoff verwendet, wenn seine
Capability und die konkrete Antwort dies erlauben. HVO100 ist auswählbar, wird
aber nicht pauschal als Diesel ausgegeben; Preise erscheinen nur bei verifizierter
Provider-/Länder-Capability.

Im Automatikmodus werden nur aktivierte und konfigurierte Provider betrachtet.
Die Auswahl berücksichtigt Land, Kraftstoff-Capability, Stationspreisabdeckung,
Zugang und Providerfehler. Ein deaktivierter oder nicht authentifizierter
Provider wird nicht stillschweigend als funktionierender Fallback verwendet.
E10 kann, sofern die Capability dies ausdrücklich erlaubt, als E5-Ersatz
angezeigt werden. Dieser Ersatz gilt nicht für Diesel, LPG oder HVO100.

## API-Schlüssel

Für jeden aktivierten Provider ist ein eigener Zugang erforderlich. Registrierung,
Freigabe, Quoten, Kosten und Nutzungsbedingungen werden ausschließlich vom
jeweiligen Anbieter festgelegt:

### Tankerkönig

1. Öffne das [Tankerkönig-Onboarding](https://onboarding.tankerkoenig.de/).
2. Beantrage den vorgesehenen API-Zugang und beachte die Anbieterbedingungen.
3. Trage den Schlüssel unter **Einstellungen → Geräte & Dienste → Mobile Fuel
   Stations → Konfigurieren → Zugangsdaten verwalten** ein.

### Petromap

1. Öffne die [Petromap-Developer-Seite](https://developer.petromap.eu/).
2. Beantrage Zugang und gegebenenfalls die erforderliche manuelle Freigabe.
3. Trage den Schlüssel im Credential-Dialog der Integration ein.

### Nakordoni

1. Öffne die [Nakordoni-Developer-Seite](https://nakordoni.eu/en/developers).
2. Beantrage Schlüssel und die für deinen Markt erforderliche Freigabe.
3. Trage den Schlüssel im Credential-Dialog ein und prüfe Quoten und Status.

Ein hinterlegter Schlüssel bedeutet nicht automatisch, dass ein Live-Zugang
erfolgreich geprüft wurde. Der Optionsdialog startet keine unnötigen
Provider-Anfragen. Zugangsdaten werden nicht in Git, Logs oder Diagnostics
ausgegeben.

## GPS, Polling und Startup-Recovery

Die Integration benötigt gültige Koordinaten der konfigurierten Entity. Nach
dem Start legt sie ihre Entities an und versucht einen normalen Coordinator-
Refresh. Wenn GPS beim Start noch fehlt, prüft die Startup-Recovery ungefähr
nach 3, 10 und 30 Sekunden erneut. Danach folgen langsame Prüfungen ungefähr
alle 60 Sekunden, bis GPS verfügbar ist oder die Integration entladen wird.

Ein passendes GPS-Ereignis kann den nächsten Versuch sofort auslösen. Die
zeitgesteuerten Prüfungen bleiben aktiv, damit reine Attributänderungen oder
verpasste `state_changed`-Ereignisse nicht zu einem Warten auf den nächsten
15-Minuten-Zyklus führen. Recovery-Trigger laufen durch einen deduplizierten
Pfad; Recovery und reguläres Polling führen keine parallelen Provider-Anfragen
aus.

Temporäre Providerfehler werden mit begrenztem exponentiellem Backoff und
Jitter behandelt. `Retry-After` und erkannte Rate-Limits haben Vorrang. Dauerhafte
Authentifizierungs- oder Konfigurationsfehler werden diagnostiziert und nicht
in einer schnellen Endlosschleife wiederholt. Bei temporären Fehlern bleiben
gültige Cachedaten erhalten und werden als veraltet kenntlich gemacht.

Nach erfolgreichem Abruf endet die Startup-Recovery. Das normale Polling bleibt
unverändert aktiv (standardmäßig etwa alle 15 Minuten), ebenso der separate
Movement-Refresh mit Schwelle und Cooldown. Timer, Tasks und GPS-Listener
werden beim Unload oder Reload abgebrochen und entfernt.

## Lovelace-Karte und Markenlogos

Beispiel:

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations
navigation: true
show_brand_logos: true
```

v0.6.0 erkennt die sechs mitgelieferten lokalen SVGs:

| Marke | Datei |
| --- | --- |
| Aral | `aral.svg` |
| Shell | `shell.svg` |
| JET | `jet.svg` |
| Total / TotalEnergies | `total.svg` |
| ORLEN / ORLEN Express | `orlen.svg` |
| OMV | `omv.svg` |

Die Erkennung normalisiert Groß-/Kleinschreibung, Unicode-Akzente, Leerzeichen
und Satzzeichen. Wenn das `brand`-Feld fehlt oder keinen Treffer liefert, wird
zusätzlich der Stationsname als Fallback geprüft. Unbekannte, leere oder nicht
ladbare Logos zeigen das generische Zapfsäulensymbol. `show_brand_logos: false`
deaktiviert die Anzeige. Die vorhandenen Logoquellen und Prüfsummen stehen in
[docs/BRAND_LOGOS.md](docs/BRAND_LOGOS.md).

Die Karte zeigt Stationsliste, Name, Adresse, Entfernung, Öffnungsstatus,
Preisalter, verfügbare Preise, E5/E10-Ersatzhinweise und eine Navigation. Eine
eigene lokale SVG kann unter `/config/www/fuel-logos/` abgelegt und über
`/local/fuel-logos/...` referenziert werden; externe URLs und unsichere
Pfadbestandteile werden abgelehnt. Fehler fallen auf das generische Symbol
zurück.

## Preise, Sortierung und Navigation

Standardmäßig werden Stationen nach Entfernung sortiert. Für Preissortierung
muss die Kraftstoffart eindeutig gewählt sein; Stationen ohne gültigen Preis
stehen am Ende. Unterschiedliche Kraftstoffarten werden nicht zu einer
gemeinsamen Rangliste vermischt. Fehlende Preise werden nicht durch einen
anderen Kraftstoff ersetzt.

Die Karte unterstützt je nach Konfiguration Apple Maps, Google Maps, Waze oder
eine automatische Auswahl. Die Entities bleiben stabil; die Anzahl der
Stationsplätze kann konfiguriert werden.

## Updates und Migration

Erstelle vor einem Update ein Home-Assistant-Backup. Aktualisiere anschließend
über HACS und starte Home Assistant vollständig neu. Bestehende Config Entries,
Zugangsdaten, Stationssensoren und kompatible Dashboard-Konfigurationen bleiben
erhalten. Prüfe nach einem größeren Versionssprung die versionierte Karten-
Ressource und lösche bei Bedarf einen veralteten Browser-Cache.

Für einen Rücksprung bleibt `v0.5.1` als vorherige Stable-Version verfügbar.
Die Beta-Releases, einschließlich `v0.6.0-beta.6`, bleiben im GitHub-Archiv
erhalten.

## Datenschutz und Einschränkungen

Je nach gewähltem Provider können Standortkoordinaten, Radius und
Kraftstoffauswahl an externe APIs übertragen werden. Lies vor der Aktivierung
die Datenschutz- und Nutzungsbedingungen des Providers. Die Integration sendet
keine Geräte-ID an Nakordoni, protokolliert keine vollständigen API-Schlüssel
und gibt keine exakten privaten Koordinaten in Diagnostics aus. Die sichtbare
Attribution **Data by nakordoni.eu** muss erhalten bleiben, wenn Nakordoni
verwendet wird.

Providerabdeckung, Preise, Öffnungszeiten, Quoten und Berechtigungen sind
externe Daten und können sich ändern. Nakordoni-Märkte und HVO100-Preise sind
nicht pauschal garantiert. Die Integration ersetzt keine verbindliche
Preis- oder Verfügbarkeitsauskunft.

## Fehlerbehebung und Diagnostics

- **Keine Tankstellen:** Entity, gültige Koordinaten, Radius, Providerwahl und
  Zugangsstatus prüfen.
- **GPS beim Start unavailable:** Die Recovery-Diagnostics zeigen Status,
  Versuchszähler und nächsten Termin; nach Verfügbarkeit wird ein Versuch
  beschleunigt ausgelöst.
- **Preis fehlt:** Für diese Station und Kraftstoffart liegt kein gültiger
  Providerpreis vor.
- **Providerfehler:** Authentifizierungs-/Konfigurationsfehler beheben; bei
  temporären Fehlern Cache und stale-Markierung beachten.
- **Karte zeigt das Zapfsäulensymbol:** `brand` und Stationsname prüfen,
  `show_brand_logos` aktivieren, Resource-Version und Browser-Cache prüfen.
- **Karte nach Update alt:** Home Assistant neu starten und den Browser-Cache
  neu laden.

Diagnostics enthalten Recovery-Status, Versuchszähler, letzten Trigger,
nächsten Retry-Termin, GPS-Ereignistyp/-zeitpunkt, In-Flight-Status und
Fehlerklassifikation, aber keine Koordinaten, Tokens oder vollständigen Keys.

## Entwicklung und Tests

Für Entwicklung und lokale Prüfungen:

```bash
python -m pytest
cd frontend && npm ci && npm test -- --run && npm run typecheck && npm run build
python -m compileall custom_components tests
```

Die CI prüft zusätzlich Home-Assistant-/Hassfest-Kompatibilität, Bundle- und
Diff-Synchronität, Markdown-/Versionskonsistenz und Secret-Scanning. Live-
Providerzugänge werden nicht als Tests vorausgesetzt; Provider- und
Recovery-Tests verwenden Mocks und Fixtures.

## Release-Archiv

Historische Release Notes liegen unverändert im
[Release-Archiv auf GitHub](https://github.com/balronu/ha-mobile-fuel-stations/tree/main/docs/releases/).
Die Stable-Release Notes stehen in
[`docs/releases/RELEASE_NOTES_v0.6.0.md`](docs/releases/RELEASE_NOTES_v0.6.0.md)
beschrieben. Weitere Projektinformationen stehen in [CONTRIBUTING.md](CONTRIBUTING.md),
der [Markendokumentation](docs/BRAND_LOGOS.md) und im
[GitHub-Release-Archiv](https://github.com/balronu/ha-mobile-fuel-stations/releases).
