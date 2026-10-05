# Mobile Fuel Stations

[Deutsch](README.md) | [English](README.en.md)

Mobile Fuel Stations ist eine Home-Assistant-Custom-Integration, die anhand
einer konfigurierbaren Standort-Entity nahegelegene Tankstellen sucht. Der
erste unterstützte Anbieter ist [Tankerkönig](https://creativecommons.tankerkoenig.de/).
Die Integration eignet sich für Fahrzeuge, Wohnmobile und andere GPS-verfolgte
Objekte.

## Funktionen

- Einrichtung und Optionen über die Home-Assistant-Oberfläche.
- Konfigurierbare Standort-Entity mit `latitude`- und `longitude`-Attributen.
- Tankerkönig-Suche für `diesel`, `e5` oder `e10`.
- Konfigurierbarer Radius von 1 bis 100 km und 1 bis 10 Stations-Slots.
- Regelmäßige Abfragen, standardmäßig alle 15 Minuten.
- Optionale bewegungsabhängige Aktualisierung.
- Konfigurierbare Bewegungsschwelle und Mindest-Cooldown.
- Geöffnete Tankstellen zuerst, danach gültige Preise aufsteigend; fehlende
  Preise zuletzt.
- Name, Marke, Preis, Entfernung, Öffnungsstatus, Adresse und Koordinaten als
  Entity-Daten.
- Persistenter Referenzpunkt und Zeitstempel der letzten erfolgreichen Suche.
- Diagnostics ohne API-Key und ohne exakte Koordinaten.
- Englische und deutsche UI-Übersetzungen.

## Dashboard-Karte (`v0.2.0`)

Diese Beta ergänzt `custom:mobile-fuel-stations-card` in derselben HACS-
Integration. Das Bundle wird mit der Integration ausgeliefert. Nach
Installation und Neustart die Lovelace-Resource einmalig registrieren:

```text
/mobile_fuel_stations/mobile-fuel-stations-card.js
```

Minimale Karte:

```yaml
type: custom:mobile-fuel-stations-card
entity: <OVERVIEW_ENTITY>
```

Version 0.2.0 behebt außerdem den HTTP-500-Fehler beim Öffnen der Integrationsoptionen
über das Zahnrad und verwendet die aktuelle Home-Assistant-OptionsFlow-API.
Bestehende Config Entries benötigen keine Migration; der API-Key bleibt in den
Config-Entry-Daten geschützt.

Die Karte enthält einen visuellen Editor zur Auswahl des Overview-Sensors und
einen separaten Navigationsbutton pro Station. Navigation ist standardmäßig
aktiviert und kann mit `navigation: false` ausgeblendet werden. Der
Stationsblock öffnet weiterhin `more-info`; der Navigationsbutton verwendet
einen HTTPS-Maps-Link. Die Übergabe an Browser oder Karten-App ist
clientabhängig und garantiert keine bestimmte Karten-App. Anbieter sind
**Automatisch**, **Apple Karten**, **Google Maps** und **Waze**. Waze wird
ausschließlich explizit ausgewählt; AUTO verwendet weiterhin Apple auf
iOS/iPadOS und Google auf Android/Desktop.
Im visuellen Editor kann der Anbieter auf **Automatisch**, **Apple Karten**,
**Google Maps** oder **Waze** gestellt werden; `navigation_provider: auto|apple|google|waze` ist
auch per YAML möglich. Die versionslose Resource-URL bleibt bei HACS-Updates
gleich. Ein Browser-/Companion-Cache kann trotzdem einen Neuladevorgang
erfordern. Der Anzeigename eines Stations-Slots folgt dem aktuellen
Tankstellenname, während Entity-ID und Unique-ID stabil bleiben.

Bestehende Beta-2-Tester ändern ihre bisherige Resource einmalig von
`/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.2.0-beta.2` auf die
versionslose URL oben. Danach sind bei HACS-Updates keine Resource-Änderungen
mehr vorgesehen.

Waze-Beispiel:

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.<overview_entity>
navigation: true
navigation_provider: waze
```

Sygic ist nicht Bestandteil von v0.2.0.

## Voraussetzungen

- Home Assistant 2026.2 oder neuer.
- Ein eigener Tankerkönig-API-Key.
- Eine Entity mit numerischen `latitude`- und `longitude`-Attributen,
  normalerweise ein GPS-`device_tracker`.

## Installation

### HACS – benutzerdefiniertes Repository

Solange das Projekt noch nicht im offiziellen HACS-Standardverzeichnis liegt,
kann es als benutzerdefiniertes Repository installiert werden:

1. HACS → **Integrationen** öffnen.
2. Das Drei-Punkte-Menü öffnen und **Benutzerdefinierte Repositories** wählen.
3. `https://github.com/balronu/ha-mobile-fuel-stations` eintragen.
4. Als Typ/Kategorie **Integration** auswählen.
5. **Mobile Fuel Stations** installieren.
6. Home Assistant neu starten.

### Manuelle Installation

Den Ordner `custom_components/mobile_fuel_stations` nach

```text
/config/custom_components/mobile_fuel_stations
```

kopieren und Home Assistant anschließend neu starten.

## Einrichtung

Zu **Einstellungen → Geräte & Dienste → Integration hinzufügen** gehen und
**Mobile Fuel Stations** auswählen. Benötigt werden:

- **Tankerkönig-API-Key**: wird im Config Entry gespeichert und nicht als
  Entity-Attribut veröffentlicht.
- **Standort-Entity**: Entity mit aktuellen `latitude`- und `longitude`-Werten.
- **Radius**: 1–100 km, Standard 20 km.
- **Kraftstoffart**: `diesel`, `e5` oder `e10`.
- **Anzahl Stations-Slots**: 1–10, Standard 5.
- **Regelintervall**: mindestens 5 Minuten, Standard 15 Minuten.
- **Bewegungsupdates**: bewegungsabhängige Aktualisierungen aktivieren oder
  deaktivieren.
- **Bewegungsschwelle**: Standard 2 km seit der letzten erfolgreichen Suche.
- **Cooldown**: mindestens 5 Minuten zwischen API-Abfragen, Standard 5 Minuten.

Die ausgewählte Standort-Entity muss bereits gültige Koordinaten besitzen. Die
Integration stellt selbst kein GPS bereit und erstellt oder ersetzt keine
Standort-Entity.

### Optionen

Die Optionen können später am Integrationseintrag geändert werden. Ein
Bewegungsupdate wird erst ausgelöst, wenn die Bewegungsschwelle erreicht und
der Cooldown abgelaufen ist. Der Referenzpunkt wird nur nach einer
erfolgreichen Anbieterantwort verschoben. Ungültige GPS-Daten oder
Provider-Fehler lösen keine Abfrage mit ungültigen Koordinaten aus; die letzte
gültige Antwort bleibt soweit möglich erhalten.

## Standort-Entity

Als Quelle kommen Fahrzeugtracker, GPS-Tracker, Device Tracker oder eine andere
geeignete Home-Assistant-Entity mit `latitude` und `longitude` infrage.
Generisches Beispiel:

```yaml
device_tracker.my_vehicle:
  state: not_home
  attributes:
    latitude: 50.0000
    longitude: 8.0000
```

Die Beispielkoordinaten sind Platzhalter. Entity und Werte müssen durch die
eigene Standortquelle ersetzt werden.

## Erzeugte Entities

Die Entity IDs werden aus Config Entry und Standort-Entity gebildet und können
durch die Home-Assistant-Normalisierung leicht abweichen. Die tatsächlichen
IDs unter **Einstellungen → Geräte & Dienste → Entitäten** prüfen.

Für die generische Standort-Entity `device_tracker.my_vehicle` sehen die IDs
typischerweise so aus:

- `sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations`
- `sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1` bis
  `_station_5`

Die Beispiel-IDs müssen durch die auf dem eigenen System erzeugten IDs ersetzt
werden.

### Overview-Sensor

Der State des Overview-Sensors ist die Anzahl der aktuell gefundenen bzw.
angezeigten Tankstellen. Wichtige Attribute:

- `radius`: eingestellter Suchradius.
- `fuel_type`: Kraftstoffart.
- `location_entity`: verwendete Standort-Entity.
- `station_count`: konfigurierte Slot-Anzahl.
- `last_successful_update`: Zeitpunkt der letzten erfolgreichen Suche.
- `reference_latitude` und `reference_longitude`: Referenzpunkt der letzten
  erfolgreichen Suche.
- `distance_since_last_search`: aktuelle Entfernung seit diesem Referenzpunkt.

### Stations-Sensoren

Jeder Slot-Sensor enthält im State den aktuellen Kraftstoffpreis in `EUR/L`.
Die Stationsdaten stehen in den Attributen:

`station_id`, `station_name`, `brand`, `distance`, `is_open`, `street`,
`house_number`, `postcode`, `place`, `latitude` und `longitude`.

Die Slot-IDs bleiben stabil, aber die Station in einem Slot kann sich nach
einer Aktualisierung ändern. Ein leerer Slot wird als nicht verfügbar markiert.

## Dashboard-Beispiel – Standardkarten

Dieses Beispiel benötigt keine Custom Card. Die Beispiel-Entity-IDs müssen
durch die IDs des eigenen Home-Assistant-Systems ersetzt werden.

```yaml
type: entities
title: Tankstellen im Umkreis
entities:
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations
    name: Tankstellen gefunden
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1
    name: Tankstelle 1
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_2
    name: Tankstelle 2
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_3
    name: Tankstelle 3
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_4
    name: Tankstelle 4
  - entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_5
    name: Tankstelle 5
```

## Optionales Mushroom-Beispiel

Dieses Beispiel benötigt [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom).
Es verwendet die Stationsattribute direkt: kein JSON-Parsing, kein
JavaScript, keine CSS-Hacks, keine absolute Positionierung und keine negativen
Margins.

Für eine Sections-Ansicht kann der Header mit nativen Grid-Optionen vollbreit
angezeigt werden:

```yaml
type: custom:mushroom-template-card
entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations
primary: Tankstellen im Umkreis
secondary: >-
  {{ states('sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations') }} Tankstellen ·
  {{ state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations', 'radius') | int }} km ·
  {{ (state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_nearby_stations', 'fuel_type') or 'diesel') | title }}
multiline_secondary: true
layout: horizontal
fill_container: true
grid_options:
  columns: full
  rows: 2
```

Eine Stationskarte kann die nativen Attribute des Slots verwenden:

```yaml
type: custom:mushroom-template-card
entity: sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1
primary: >-
  {{ state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1', 'station_name') or 'Tankstelle nicht verfügbar' }}
secondary: >-
  {{ states('sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1') }} €/l ·
  {{ state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1', 'distance') }} km ·
  {{ 'geöffnet' if is_state_attr('sensor.mobile_fuel_stations_device_tracker_my_vehicle_station_1', 'is_open', true) else 'geschlossen' }}
multiline_secondary: true
layout: horizontal
fill_container: true
```

Für die Slots 2–5 die Entity ID ersetzen. Das Beispiel funktioniert vollständig
ohne Navigation.

## Navigation

Die Karte zeigt standardmäßig einen separaten Navigationsbutton, sofern gültige
Koordinaten vorhanden sind. Im visuellen Editor oder per YAML stehen
`navigation_provider: auto`, `apple` und `google` zur Verfügung. `auto` wählt
für iOS/iPadOS Apple Maps und verwendet für Android sowie Desktop den
Google-HTTPS-Weblink. Apple- und Google-Maps-Links können je nach Browser,
Companion-App und installierten Apps unterschiedlich behandelt werden; eine
bestimmte App wird nicht garantiert. `navigation: false` blendet den Button aus.

## Fehlerbehebung

### Keine Tankstellen gefunden

- Prüfen, ob die Standort-Entity existiert und numerische `latitude`-/
  `longitude`-Attribute liefert.
- Radius und Kraftstoffart prüfen.
- Tankerkönig-API-Key und Erreichbarkeit des Anbieters prüfen.

### Standort nicht verfügbar

Bei `unknown`, `unavailable` oder ungültigen Koordinaten sendet die Integration
keine Abfrage mit diesen Werten. Die letzte gültige Antwort bleibt soweit
möglich erhalten. GPS-Quelle wiederherstellen und nächste Aktualisierung
abwarten.

### Preise aktualisieren sich nicht

Regelintervall, Bewegungsupdates, Bewegungsschwelle und Cooldown prüfen.
Provider-Ratelimits und Preisaktualität liegen außerhalb der Integration.

### Dashboard findet Entity IDs nicht

Die tatsächlichen IDs unter **Einstellungen → Geräte & Dienste → Entitäten**
nachsehen. Sie enthalten die normalisierte Standort-Entity und können von den
Beispielen abweichen.

### API-Probleme

API-Key, Provider-Verfügbarkeit und Ratelimits prüfen. Keine API-Keys in Logs,
Screenshots oder GitHub-Issues veröffentlichen.

### Bewegungsupdate funktioniert scheinbar nicht

Ein Bewegungsupdate benötigt sowohl die konfigurierte Bewegungsschwelle als
auch einen abgelaufenen Cooldown. Das Regelintervall bleibt unabhängig davon
aktiv. Bei GPS-Fehlern oder einem noch laufenden Cooldown wird keine zusätzliche
Abfrage ausgelöst.

## Datenschutz und Sicherheit

- Der API-Key wird im Home-Assistant-Config-Entry gespeichert.
- API-Keys niemals in GitHub, Logs, Screenshots, Fixtures oder Issues ablegen.
- Die konfigurierte Standortposition wird für die Umkreissuche an Tankerkönig
  übertragen.
- Stationskoordinaten werden als Entity-Attribute bereitgestellt, weil sie
  Teil des Suchergebnisses sind.
- Diagnostics redigieren den API-Key und lassen exakte Koordinaten weg.
- Keine Diagnostics oder Logs mit privaten Standortdaten veröffentlichen.

## API und Attribution

Die Integration verwendet den Tankerkönig-Endpunkt für nahegelegene
Tankstellen mit dynamischer Position, Radius, Kraftstoffart und Preissortierung.
Nutzung und Attribution richten sich nach den Bedingungen und Ratelimits des
Anbieters. Nutzer benötigen und schützen ihren eigenen API-Key.

## Entwicklung und Beiträge

```bash
python -m pytest -q
```

Fixtures verwenden erfundene Daten und enthalten keine echten API-Keys oder
privaten GPS-Koordinaten. Bei Änderungen an benutzerrelevanter Dokumentation
`README.md` und `README.de.md` synchron halten. Siehe [CONTRIBUTING.md](CONTRIBUTING.md).

## Lizenz

MIT. Siehe [LICENSE](LICENSE).
