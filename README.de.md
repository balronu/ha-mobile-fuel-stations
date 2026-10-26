# Mobile Fuel Stations

🇩🇪 **Deutsch** | [🇬🇧 English](README.en.md)

<p align="center"><img src="assets/branding/logo.png" alt="Mobile Fuel Stations" width="220"></p>

<p align="center">
  <a href="https://github.com/balronu/ha-mobile-fuel-stations/releases/tag/v0.8.5"><img src="https://img.shields.io/badge/Stable-v0.8.5-16a34a" alt="Stable v0.8.5"></a>
  <a href="https://www.home-assistant.io/integrations/"><img src="https://img.shields.io/badge/Home%20Assistant-Custom%20integration-41bdf5" alt="Home Assistant custom integration"></a>
  <a href="https://www.hacs.xyz/docs/faq/custom_repositories/"><img src="https://img.shields.io/badge/HACS-Custom%20repository-18a999" alt="HACS custom repository"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-0f766e" alt="MIT License"></a>
  <a href="https://github.com/balronu/ha-mobile-fuel-stations/actions/workflows/tests.yml"><img src="https://github.com/balronu/ha-mobile-fuel-stations/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests workflow"></a>
</p>

**Dynamische Tankstellensuche und Preisvergleich für Home Assistant** –
GPS-basiert, providerübergreifend und mit Navigation direkt aus der Lovelace-
Karte. Die Integration folgt der Position deines Fahrzeugs, Wohnmobils oder
anderen Trackers und liefert Tankstellen, Kraftstoffpreise, Entfernung,
Öffnungsstatus und Zielnavigation.

### Auf einen Blick

- **GPS entlang der Route:** Tankstellen werden anhand der aktuellen Position
  einer frei wählbaren Entity gesucht.
- **Mehrere Datenquellen:** Tankerkönig, Petromap und Nakordoni mit
  capability-basierter Provider-Auswahl.
- **Kraftstoffpreise:** E5, E10, Diesel, LPG/Autogas und HVO100 mit
  Entfernungs- oder Preis-Sortierung.
- **Lovelace für unterwegs:** Responsive Karte, Erkennung vieler
  Markenschreibweisen, 60 lokale Markenlogos und direkte Navigation zum
  ausgewählten Ziel.

### Vorschau

<p align="center"><img src="docs/assets/mobile-fuel-stations-mobile.jpg" alt="Mobile Lovelace-Karte mit Tankstellen in der Nähe, Kraftstoffpreisen, Entfernungen und Navigation" width="320"></p>

### Schnellstart

1. Repository über [HACS](https://github.com/balronu/ha-mobile-fuel-stations)
   installieren oder als benutzerdefiniertes Repository hinzufügen.
2. Integration unter **Einstellungen → Geräte & Dienste** einrichten.
3. Eine Entity mit `latitude` und `longitude`, Kraftstoffarten, Suchradius und
   Provider auswählen.
4. Die vollständige Anleitung beginnt bei [Installation über HACS](README.md#installation-über-hacs).

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
| Stable | `v0.8.5` | Aktuelle stabile Version |
| Beta | `v0.8.5-beta.1` | Historische Nakordoni-v2-Beta |
| Vorherige Stable | `v0.8.4` | Verfügbare Rollback-Version |
| Historische Beta | `v0.8.0-beta.8` | Vorangegangene Pre-release |
| Frontend-Komponente | `v0.8.5` | Unabhängig versionierte Lovelace-Komponente |

`v0.8.3` war die vorherige stabile Veröffentlichung. Sie bündelt Tankerkönig,
Petromap und Nakordoni mit automatischer Provider-Auswahl, länder- und
marktberechtigtem Fallback, Quota-/Trip-Pass-Diagnose, OAuth2-PKCE und manuellen
API-Keys. Die feste Kartenpriorisierung zeigt die nächste Tankstelle, danach die günstigste unterschiedliche Tankstelle für den konfigurierten Kraftstoff; beide Ansichten verwenden dieselbe deterministische Reihenfolge. Die 60 lokalen PNG-Logos stammen aus der bereitgestellten ZIP; die
Ressource wird mit dem Cache-Key `v=0.8.3` automatisch registriert. Die
experimentelle Nakordoni-OAuth-Anmeldung wurde statisch geprüft, aber nicht
über einen Live-Callback bestätigt. Herkunft, fehlende Einzelbildlizenz und
verbleibende Markenrechtsrisiken sind in [BRAND_LOGOS.md](BRAND_LOGOS.md)
festgehalten; dies ist keine Markenlizenz oder Herstellerempfehlung.

`v0.8.5` ist die aktuelle stabile Veröffentlichung. Sie übernimmt die in der
Beta getestete Nakordoni-v2-Kompatibilität mit dokumentierten Kraftstoffarten,
bestätigungsbasierter Preisfrische, sicherem Währungsvergleich, stabiler
Stationsidentifikation und erweiterter Providerdiagnose. Bestehende
Konfigurationen und Karten bleiben kompatibel; `v0.8.4` bleibt als Rollback
verfügbar.

`v0.8.4` ergänzt
**Ausführlich**, **Kompakt** und **Individuell** sowie kartenbezogene
Sortierung, Kraftstoff für die Preissortierung, sichtbare Tankstellenanzahl,
Kopf- und Stationsfelder, Dichte, Trennlinien und das optionale Layout
**Highlights + Liste**. Sichtbare Kopfbereich-Sektionen erzeugen keine leeren
Wrapper und zwischen zwei sichtbaren Sektionen erscheint maximal eine
Trennlinie. Die Stable-Ressource verwendet `v=0.8.5`; bestehende YAML-Karten
und Config Entries bleiben kompatibel.

v0.7.1 verbesserte außerdem die Erkennung integrationszugehöriger Overview-
Sensoren im visuellen Lovelace-Editor. Auch vorübergehend `unavailable`-
Sensoren werden zur Auswahl angeboten. Mehrere Fahrzeuge beziehungsweise
Config Entries bleiben getrennt; pro Fahrzeug wird die eigene Overview-Entity
ausgewählt. Bestehende YAML-Karten mit direkt eingetragener Entity-ID bleiben
kompatibel.

v0.7.2 berücksichtigt für die Highlights „NÄCHSTE“ und „GÜNSTIGSTE“ auch
Stationen mit unbekanntem Öffnungsstatus. Explizit geschlossene Stationen
bleiben ausgeschlossen; ein unbekannter Status wird nicht als „Geöffnet"
dargestellt. Die Auswahl ist providerübergreifend und deterministisch.

v0.7.3 normalisiert Nakordoni-E10-Preise auch bei Einzelkraftstoff-Abfragen
für das günstigste Highlight. Strukturierte und formatierte Provider-Adressen
werden übernommen, sofern geliefert; fehlende Adressen bleiben leer. Explizit
veraltete Preise werden nicht als aktueller Bestpreis ausgewählt.

Die Version `v0.8.3` priorisiert die vollständige Tankstellenliste in beiden Ansichten; die lokale
Ländererkennung aus `v0.8.0` bleibt enthalten. Die
eintreffenden GPS-Positionen im manuellen Modus. Gültige Positionen aktualisieren
den Länder-Kontext und die Providerstatus ohne Provider- oder Usage-Abfrage.
Die Erweiterungen der v0.8.0-Betas bleiben enthalten: ein pro Config Entry
gespeicherter Abrufmodus. **Automatisch** nutzt weiterhin Zeitplan, GPS-Bewegung,
Recovery und Provider-Cooldowns; **Manuell** führt keine automatischen
Providerabfragen aus. Der Administrator kann in der Karte gezielt **Jetzt
abrufen** wählen. Benutzer ohne Home-Assistant-Adminrechte sehen die Karte
weiterhin lesend, aber keine Steuerung. Der letzte erfolgreiche Abruf und der
persistierte Stations-Cache bleiben nach einem Neustart sichtbar. Cooldowns und
verifizierte Nakordoni-Kontingente werden je Provider geheimnisfrei angezeigt;
Tankerkönig und Petromap werden ohne belastbare Kontingentdaten als unbekannt
ausgewiesen. Ein frischer automatischer Cache löst beim Start keinen vorzeitigen
Abruf aus. Beta.7 vereinheitlicht zusätzlich Länder-Kontext, Provider-
Verfügbarkeit und manuelle Abrufsperre; unbekannte Länder werden als eigener
Status diagnostiziert. Die Release-Prüfung verwendet Tests und CI mit Mocks und
Fixtures; ein Live-Provider- oder OAuth-Aufruf ist nicht Bestandteil der
Veröffentlichung.

Im automatischen Provider-Auswahlmodus erfolgt ein Fallback nur für DNS-/Netzwerk-,
Timeout-, HTTP-5xx- und HTTP-429-Fehler. Authentifizierungs-, Berechtigungs-,
Kontingent-, Payload- und Konfigurationsfehler werden nicht durch einen stillen
Providerwechsel verdeckt. Nakordoni wird nur verwendet, wenn der Provider für
den Markt nachweislich berechtigt ist; ein API-Key allein reicht nicht.

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
- optionale adaptive Aktualisierung anhand gültiger GPS-Geschwindigkeit
- pro Config Entry wählbarer automatischer oder manueller Abrufmodus mit
  admin-geschütztem Einzelabruf
- persistierter, kontextgeprüfter Stations-Cache mit sichtbarer Stale-Markierung
- responsive Lovelace-Karte mit Navigation und Markenlogo-Fallback

### Lovelace-Darstellungsmodi

Neue Karten werden im Modus compact angelegt: Tankstellen erscheinen als
platzsparende Zeilen mit Logo, Adresse, Öffnungsstatus, Entfernung,
nebeneinanderstehenden Preisen und Navigation. Die Kennzeichnungen für
„Nächste“ und „Günstigste“ bleiben inline; Provider-, Kontingent- und
Cooldown-Diagnose liegt im aufklappbaren Bereich.

Bestehende YAML-Karten ohne `display_mode` bleiben aus Kompatibilitätsgründen
im bisherigen ausführlichen Modus. Der visuelle Editor bietet alle drei Modi
und im individuellen Modus einfache Liste, Kacheln plus Liste sowie eine
konfigurierbare Liste. Sortierung, Preis-Kraftstoff, sichtbare Anzahl,
Kopfbereich, Stationsfelder, Dichte und Trennlinien werden pro Karte
gespeichert; bestehende Integrationsoptionen bleiben Legacy-Fallback.

## Installation über HACS

1. Öffne **HACS → Integrationen**.
2. Suche nach **Mobile Fuel Stations**. Falls das Repository nicht gelistet
   ist, füge `https://github.com/balronu/ha-mobile-fuel-stations` unter
   **Benutzerdefinierte Repositories** als Typ **Integration** hinzu.
3. Installiere die Integration.
4. Starte Home Assistant vollständig neu, wie von HACS verlangt.
5. Öffne **Einstellungen → Geräte & Dienste → Integration hinzufügen** und
   wähle **Mobile Fuel Stations**.

`v0.8.5` ist die aktuelle stabile HACS-Version. `v0.8.4` bleibt als
vorherige Stable-Rollback-Version verfügbar. Historische Betas bleiben im
GitHub-Archiv erhalten.

Die adaptive Aktualisierung ist standardmäßig deaktiviert und wird nur über
den Optionsdialog aktiviert. Sie verwendet ausschließlich gültige, aktuelle
GPS-Daten; künstliche Positionen werden nicht erzeugt.

Die Lovelace-Karte wird von der Integration bereitgestellt und automatisch
registriert. Die Frontend-Ressource lautet:

```text
/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.8.5
```

Der versionsabhängige Resource-Key verhindert dieselbe alte Bundle-URL. Eine
bereits ausgeführte JavaScript-Datei kann Home Assistant jedoch nicht sicher
im laufenden Tab ersetzen; je nach Frontend oder Companion-App kann ein
einmaliges Dashboard-Neuladen erforderlich bleiben. Es gibt keinen pauschalen
automatischen Hard Reload und keine Reload-Schleife. Die technische Ladebeschreibung steht
in [docs/RESOURCE_LOADING.md](docs/RESOURCE_LOADING.md).

## Einrichtung und Konfiguration

Im Konfigurationsdialog werden typischerweise gewählt:

- eine Entity mit `latitude` und `longitude` (zum Beispiel ein Fahrzeug-Tracker)
- Suchradius und maximale Anzahl der Stationen (1 bis 10)
- eine oder mehrere Kraftstoffarten
- einer oder mehrere Provider beziehungsweise **Automatisch**
- Sortierung nach Entfernung oder Kraftstoffpreis
- Polling-Intervall sowie Bewegungsschwelle und Cooldown
- optional adaptive Aktualisierung (standardmäßig deaktiviert)
- gewünschter Navigationsdienst der Karte

Die allgemeinen Optionen werden separat von den Zugangsdaten gespeichert.
Unter **Zugangsdaten verwalten** können Provider-Schlüssel ersetzt oder
ausdrücklich entfernt werden. Ein leeres Feld lässt einen vorhandenen Schlüssel
unverändert. Die Oberfläche zeigt nur nicht-sensitive Zugangsstatus, niemals
vollständige Schlüssel.

Bei aktivierter adaptiver Aktualisierung gelten diese Zielintervalle anhand
der zuletzt verifizierten Geschwindigkeit: Stillstand oder 0 km/h = 15 Minuten,
Stadtverkehr bis 30 km/h = 5 Minuten, Landstraße über 30 bis 70 km/h =
2 Minuten und Autobahn über 70 km/h = 1 Minute. Provider-Mindestabstände
haben Vorrang; das adaptive Intervall darf keine Provider-Quote umgehen.

## Provider, Länder und Kraftstoffe

Die folgende Matrix beschreibt die im Code und in den Tests belegte
Implementierung. Externe API-Verträge, Quoten und Berechtigungen können die
tatsächliche Verfügbarkeit einschränken.

| Provider | Zugang | Belegte Abdeckung und Kraftstoffe |
| --- | --- | --- |
| [Tankerkönig](https://onboarding.tankerkoenig.de/) | API-Key | Deutschland; Diesel, E5 und E10; API-Radius maximal 25 km |
| [Petromap](https://developer.petromap.eu/) | API-Key und gegebenenfalls Freigabe | Stationspreise in Deutschland und Österreich für Diesel, E5 und LPG; weitere Länder beziehungsweise nationale Daten hängen von Petromap ab |
| [Nakordoni](https://nakordoni.eu/en/developers) | OAuth2-PKCE oder API-Key, Markt-/Zugangsfreigabe | Diesel, E5, E10 und LPG; DE, AT, PL, CZ, SK, HU, SI, HR, IT, FR, BE, NL und LU werden nur bei bestätigter Marktfreigabe berücksichtigt |

Die auswählbaren Kraftstoffschlüssel sind `e5`, `e10`, `diesel`, `lpg` und
`hvo100`. Ein Provider wird nur dann für einen Kraftstoff verwendet, wenn seine
Capability und die konkrete Antwort dies erlauben. HVO100 ist auswählbar, wird
aber nicht pauschal als Diesel ausgegeben; Preise erscheinen nur bei verifizierter
Provider-/Länder-Capability.

Im Automatikmodus werden nur aktivierte, konfigurierte und marktberechtigte Provider betrachtet. Deutschland nutzt Tankerkönig vor Nakordoni, Österreich Petromap vor Nakordoni; in anderen unterstützten Ländern wird Nakordoni vor einer geeigneten Petromap-Alternative versucht. Die Felder `markets_approved`, `markets_granted`, `markets_allowed` und `markets_available` werden getrennt bewertet; fehlende Marktmetadaten geben Nakordoni keine automatische Freigabe.
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

### Nakordoni OAuth2-PKCE und Account Usage

Die Integration bietet die bevorzugte automatische Nakordoni-Anmeldung über den
Home-Assistant-Authorization-Code-Flow mit PKCE S256. Die registrierte
Redirect-URI ist exakt
`https://my.home-assistant.io/redirect/oauth`; ein Client Secret wird nicht
verwendet.

Die manuelle API-Key-Methode bleibt dauerhaft erhalten und bestehende Einträge
werden nicht erzwungen migriert. HVO100 bleibt für Nakordoni deaktiviert, bis
die Zuordnung des dokumentierten API-Felds `hvo` fachlich bestätigt ist.
Bestehende API-Key-Einträge werden weder migriert noch gelöscht und müssen
nicht auf OAuth umgestellt werden. OAuth-Tokens werden von der
Home-Assistant-OAuth2-Config-Entry-Infrastruktur gespeichert und aus
Diagnostics ausgeschlossen. OAuth ist erst vollständig, wenn Nakordoni die
benötigten Tokenfelder einschließlich `expires_in` liefert; nicht
dokumentierte Scopes oder Refresh-Parameter werden nicht angenommen.

Zusätzlich wird `GET /api/v2/account/usage` höchstens alle 15 Minuten
abgerufen. Die Sensoren zeigen Restabfragen, Quota-Reset und Trip-Pass-Status;
Quota-Klassen, Länderberechtigungen und offizielle Upgrade-Links stehen als
Attribute und in den geheimnisfreien Diagnostics bereit. `quota_exceeded`,
`market_not_allowed` und `integration_product_not_allowed` werden getrennt
klassifiziert. Es gibt keine eigene Zahlungsabwicklung.

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

Erfolgreiche Stationsdaten werden im HA-Store persistiert und beim passenden
Reload sofort wieder angezeigt. Der Cache wird nur bei identischem Provider-,
Kraftstoff-, Radius-, Sortier- und Stationskontext verwendet; ungültige oder
orts-/abfragefremde Daten werden verworfen. Während eines Provider-Cooldowns
bleiben passende Daten sichtbar und werden mit `data_stale=true` markiert.
Nach Ablauf des Cooldowns wird höchstens ein deduplizierter Refresh gestartet.

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

Bei mehreren Fahrzeugen gibt es pro Config Entry einen eigenen Overview-Sensor;
der visuelle Editor listet auch vorübergehend nicht verfügbare Mobile-Fuel-
Stations-Sensoren. Eine manuell eingetragene Entity-ID bleibt ebenfalls gültig.

Stable v0.7.2 erkennt die 60 lokal gebündelten PNG-Markenlogos aus dem
geprüften Archiv, darunter:

| Marke | Datei |
| --- | --- |
| Aral | `aral.png` |
| Shell | `shell.png` |
| JET | `jet.png` |
| Total / TotalEnergies | `total.png` |
| ORLEN / ORLEN Express | `orlen.png` |
| OMV | `omv.png` |

Die Erkennung normalisiert Groß-/Kleinschreibung, Unicode-Akzente, Leerzeichen
und Satzzeichen. Wenn das `brand`-Feld fehlt oder keinen Treffer liefert, wird
zusätzlich der Stationsname als Fallback geprüft. Unbekannte, leere oder nicht
ladbare Logos zeigen das generische Zapfsäulensymbol. Die gemeldeten Namen
`Eni (Agip Eni)` und `OIL! Tankstelle Sulzbach` werden über explizite Varianten
auf `agip-eni.png` beziehungsweise `oil.png` abgebildet; unsichere allgemeine
Teilstring-Treffer bleiben ausgeschlossen. `show_brand_logos: false`
deaktiviert die Anzeige. Die vorhandenen Logoquellen und Prüfsummen stehen in
[docs/BRAND_LOGOS.md](docs/BRAND_LOGOS.md).

Die bereitgestellte `gasstation_logos.zip` enthält 66 Dateien mit 63
eindeutigen Inhalten, drei Duplikatpaaren und mehreren technisch als JPEG
codierten Dateien mit `.png`-Endung. Alle 60 verwendeten Markenlogos wurden
als PNG normalisiert und lokal übernommen; `404.png`, `svg.png` und Duplikate
bleiben ausgeschlossen. Die Rechtebasis und das
verbleibende Markenrisiko sind in [BRAND_LOGOS.md](BRAND_LOGOS.md) dokumentiert.

Die Alias-Erkennung versteht nun deutlich mehr Markennamen und
Provider-Schreibweisen. Für alle gebündelten Marken werden die Dateien
zentral und ohne unsichere Teilstring-Suche zugeordnet. Unbekannte oder nicht
ladbare Marken bleiben beim neutralen Tankstellensymbol, während der
Markenname lesbar bleibt. Die vollständige Referenzinventur steht in
[docs/BRAND_LOGO_INVENTORY.md](docs/BRAND_LOGO_INVENTORY.md).

Lokale Benutzerlogos können weiterhin über die unterstützte `logo_path`-
Konfiguration aus `/local/...` oder `/hacsfiles/...` verwendet werden. Externe
Logo-URLs sind weder erforderlich noch zulässig. Marken werden ausschließlich
zur sachlichen Identifizierung tatsächlicher Tankstellen verwendet; es besteht
keine offizielle Verbindung zu den Markeninhabern. Markenrechte und konkrete
Bildnutzungsrechte werden getrennt dokumentiert und nicht pauschal freigegeben.

Die Karte zeigt Stationsliste, Name, Adresse, Entfernung, Öffnungsstatus,
Preisalter, verfügbare Preise, E5/E10-Ersatzhinweise und eine Navigation. Eine
eigene lokale SVG kann im lokalen Home-Assistant-`www`-Verzeichnis abgelegt
und über den zugehörigen `/local/...`-Pfad referenziert werden; externe URLs und
unsichere Pfadbestandteile werden abgelehnt. Fehler fallen auf das generische
Symbol zurück.

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

Für einen Rücksprung bleibt `v0.6.1` als vorherige Stable-Version verfügbar.
Historische Releases bleiben im GitHub-Archiv erhalten.

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

## Administrator-Diagnose für Nakordoni

Für einen gezielten, nicht produktiven Test steht der geschützte HA-Service
`mobile_fuel_stations.probe_nakordoni` zur Verfügung. Er ist nur für
authentifizierte Administratoren registriert und verwendet den bereits
gespeicherten Nakordoni-Zugang. Der Service führt genau eine Anfrage aus;
automatische Wiederholungen gibt es nicht. Mehrere parallele Diagnoseaufrufe
für denselben Config Entry werden abgewiesen.

Erforderlich sind `entry_id`, `latitude`, `longitude`, `radius_km` (0 bis 25)
und einer der verifizierten Kraftstoffschlüssel `diesel`, `e5`, `e10` oder
`lpg`. Die Response enthält nur Status, Quota, Latenz, Stations-/Preisanzahl,
Preisalter und sichere Coverage-Hinweise. Sie enthält weder API-Keys oder
Tokens noch Stationsnamen, Rohantworten oder vollständige Koordinaten.

Der Aufruf umgeht den Coordinator und den Automatikmodus; Stationscache,
Sensorzustände und Config Entry bleiben unverändert. OAuth2-Einträge nutzen
die bestehende Home-Assistant-OAuth2-Session. Die Funktion ist ausschließlich
für Diagnosezwecke vorgesehen und darf nicht als öffentlicher Feed verwendet
werden.

## Fehlerbehebung und Diagnostics

- **Overview-Sensor wird nicht im Karteneditor angezeigt:** Ab v0.7.1 werden
  auch nicht verfügbare, integrationszugehörige Overview-Sensoren im visuellen
  Editor erkannt und zur Auswahl angeboten. Bestehende YAML-Karten können ihre
  Entity-ID weiterhin direkt verwenden.
- **Overview-Sensor ist `unavailable`:** Die Auswahl im Editor bestätigt nur,
  dass die Entity erkannt wurde; sie bestätigt keine erfolgreiche
  Datenabfrage. Standort, Provider-Konfiguration, API-Key, Länderfreigaben
  und die vorhandenen Diagnostics prüfen.
- **Highlight fehlt trotz Stationsdaten:** Ab v0.7.2 werden Stationen mit
  unbekanntem Öffnungsstatus für „NÄCHSTE“ und „GÜNSTIGSTE“ berücksichtigt.
  Explizit geschlossene Stationen bleiben ausgeschlossen. Der unbekannte Status
  wird nicht als „Geöffnet“ angezeigt.
- **Bekannter Praxisfall Opel Grandland mit E10:** Bei einer Konfiguration
  führte Tankerkönig zu `ProviderResponseError` beziehungsweise einem
  Provider-Cooldown. Nach dem Entfernen von Tankerkönig und der Auswahl von
  Nakordoni funktionierte die Abfrage. Die konkrete Tankerkönig-Fehlerursache
  und ein allgemeines Fallback-Verhalten sind damit nicht abschließend
  bewertet oder als behoben bestätigt.
- **Keine Tankstellen:** Entity, gültige Koordinaten, Radius, Providerwahl und
  Zugangsstatus prüfen.
- **GPS beim Start unavailable:** Die Recovery-Diagnostics zeigen Status,
  Versuchszähler und nächsten Termin; nach Verfügbarkeit wird ein Versuch
  beschleunigt ausgelöst.
- **Preis fehlt:** Für diese Station und Kraftstoffart liegt kein gültiger
  Providerpreis vor.
- **Providerfehler:** Authentifizierungs-/Konfigurationsfehler beheben; bei
  temporären Fehlern Cache und stale-Markierung beachten. Eine erfolgreiche
  leere Antwort bedeutet null Stationen, während `None` für fehlendes GPS
  oder einen Fehler vor dem ersten verwertbaren Ergebnis steht.
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
Die adaptive Logik wird mit Geschwindigkeitsgrenzen, GPS-Ausreißern,
Provider-Mindestabständen, Cache-Reload, Cooldown und Unload-Abbruch geprüft.

## Release-Archiv

Historische Release Notes liegen unverändert im
[Release-Archiv auf GitHub](https://github.com/balronu/ha-mobile-fuel-stations/tree/main/docs/releases/).
Die Stable-Release Notes stehen in
[`docs/releases/RELEASE_NOTES_v0.8.5.md`](docs/releases/RELEASE_NOTES_v0.8.5.md)
und im [GitHub-Release v0.8.5](https://github.com/balronu/ha-mobile-fuel-stations/releases/tag/v0.8.5).
Die Beta-Release-Notes stehen in
[`docs/releases/RELEASE_NOTES_v0.8.0-beta.6.md`](docs/releases/RELEASE_NOTES_v0.8.0-beta.6.md).
Weitere Projektinformationen stehen in [CONTRIBUTING.md](CONTRIBUTING.md),
der [Markendokumentation](docs/BRAND_LOGOS.md) und im
[GitHub-Release-Archiv](https://github.com/balronu/ha-mobile-fuel-stations/releases).
