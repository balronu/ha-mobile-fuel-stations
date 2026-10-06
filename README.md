# Mobile Fuel Stations

**[English version](README.en.md)**

Mobile Fuel Stations ist eine Home-Assistant-Custom-Integration für nahegelegene Tankstellen anhand einer frei wählbaren Standort-Entity. Sie eignet sich besonders für Fahrzeuge, Wohnmobile, GPS-Tracker und andere bewegliche Objekte.

Die Beta unterstützt **Tankerkönig** und **Petromap v2**. Im Auto-Modus wird
der Provider anhand des bestätigten Landes gewählt. Petromap-Zugriff hängt von
den Berechtigungen des konfigurierten Developer-Keys ab.

## Funktionen

- Einrichtung und Optionen über die Home-Assistant-Oberfläche
- frei wählbare Standort-Entity mit `latitude`- und `longitude`-Attributen
- Diesel, E5, E10 und LPG / Autogas
- HVO100 ist noch nicht auswählbar, weil kein verifizierter providerbezogener API-Selektor vorliegt.
- Suchradius von 1 bis 25 km
- 1 bis 10 stabile Stations-Slots
- regelmäßige Aktualisierung und optionale Bewegungsupdates
- Bewegungsschwelle und Cooldown
- preisorientierte Stationsliste sowie separate Ermittlung der nächsten und günstigsten offenen Tankstelle
- Overview-Sensor mit Stationsdaten und Suchstatus
- Diagnostics ohne API-Key oder exakte Standortdaten
- Deutsch und Englisch
- mitgelieferte Dashboard-Karte mit Visual Editor
- automatische Frontend-Registrierung
- Navigation mit Apple Maps, Google Maps oder Waze
- Highlights für die nächste und günstigste offene Tankstelle
- Auto-Provider-Auswahl mit getrennten Tankerkönig- und Petromap-Credentials

## Voraussetzungen

- Home Assistant mit HACS oder Zugriff auf eine manuelle Custom-Integration-Installation
- eine Standort-Entity mit `latitude` und `longitude`
- ein Tankerkönig-API-Key, ein Petromap-v2-API-Key oder beide je nach Provider-Modus

## Installation

### HACS (Custom Repository)

1. Öffne **HACS → Integrationen**.
2. Öffne das Drei-Punkte-Menü und wähle **Benutzerdefinierte Repositories**.
3. Füge `https://github.com/balronu/ha-mobile-fuel-stations` als Repository mit der Kategorie **Integration** hinzu.
4. Installiere **Mobile Fuel Stations**.
5. Starte Home Assistant vollständig neu.
6. Füge die Integration unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** hinzu.

Die Dashboard-Karte wird automatisch registriert. Die automatisch registrierte
Frontend-URL `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.5.0-beta.2`
enthält die Integrationsversion. Jede Integrationsversion erhält dadurch eine
eigene Resource-URL, sodass veralteter Card-JavaScript-Code aus Caches bei
einem Versionswechsel nicht weiterverwendet wird. Nach einem HACS-Update
genügt ein vollständiger Home-Assistant-Neustart; ein manuelles Leeren des
Browser-Caches oder Ändern der Lovelace-Resource ist bei aktuellen
Installationen nicht erforderlich.

### Manuelle Installation

Lade das Repository herunter und kopiere den Ordner `custom_components/mobile_fuel_stations` nach `config/custom_components/`. Starte Home Assistant anschließend vollständig neu und richte die Integration über **Einstellungen → Geräte & Dienste** ein.

## Einrichtung

Wähle die Standort-Entity, den Radius, den Kraftstofftyp und die Anzahl der Stations-Slots. Wähle anschließend Tankerkönig, Petromap oder Auto und hinterlege die dafür benötigten Credentials. Konfiguriere danach die Aktualisierungs- und Bewegungsoptionen. Die Beta validiert Petromap-Credentials nicht beim Setup; der erste benötigte Runtime-Aufruf ist maßgeblich.

## Dashboard-Karte

### Über den Card Picker

Nach Installation und Neustart:

1. Öffne das Dashboard und wähle **Bearbeiten → Karte hinzufügen**.
2. Suche nach **Mobile Fuel Stations**.
3. Wähle die Karte aus.
4. Wähle die Overview-Entity aus oder übernimm den Vorschlag.
5. Speichere die Karte.

### YAML-Minimalbeispiel

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.<overview_entity>
```

### Optionen

| Option | Typ | Standard | Beschreibung |
| --- | --- | --- | --- |
| `entity` | Entity-ID | erforderlich | Overview-Sensor der Integration |
| `navigation` | Boolean | `true` | Separaten Navigationsbutton anzeigen |
| `navigation_provider` | `auto`, `apple`, `google`, `waze` | `auto` | Kartendienst für den Navigationsbutton |

Der Stationsblock öffnet weiterhin More Info. Navigation wird ausschließlich über den separaten Button gestartet.

### Nächste und günstigste Tankstelle

Die Karte zeigt oberhalb der Stationsliste zwei optionale Highlights: **Nächste** und **Günstigste**. Beide werden aus der vollständigen Tankerkönig-Ergebnismenge bestimmt, bevor die Liste auf die konfigurierten Stations-Slots begrenzt wird. Die nächste Station benötigt keinen gültigen Preis; bei fehlendem Preis wird „Preis nicht verfügbar“ angezeigt. Wenn keine passende offene Station vorhanden ist, wird das jeweilige Highlight nicht angezeigt.

Die bestehenden Stations-Slots bleiben preisorientiert und ihre Entity-IDs
bleiben unverändert. Wenn ein Highlight nicht in den sichtbaren Slots enthalten
ist, bleibt die Navigation verfügbar; More Info wird nur geöffnet, wenn eine
sichere Zuordnung zu einer sichtbaren Stations-Entity existiert.

### Navigation

Bei `navigation_provider: auto` gilt:

- iOS/iPadOS: Apple Maps
- Android: Google Maps
- Desktop und andere Geräte: Google Maps

Mit `apple`, `google` oder `waze` kann der Provider explizit gewählt werden. Waze wird nicht automatisch ausgewählt. `navigation: false` blendet den Button aus.

Die Navigation startet nur durch Nutzeraktion. Die Karte schreibt keine feste Startposition in die URL; Browser, Companion-App und Betriebssystem entscheiden über die tatsächliche Übergabe an eine installierte Karten-App. Sygic wird derzeit nicht unterstützt.

Beispiel für Waze:

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.<overview_entity>
navigation: true
navigation_provider: waze
```

## Upgrade von älteren Versionen

Für das Upgrade von v0.5.0-beta.1 auf v0.5.0-beta.2 genügt ein Update über HACS und ein vollständiger Home-Assistant-Neustart. Bestehende Tankerkönig-Konfigurationen bleiben kompatibel. Der Tankerkönig-Radius ist auf 25 km begrenzt; bestehende Konfigurationen mit einem höheren gespeicherten Wert werden beim API-Aufruf defensiv auf 25 km begrenzt.

Bei älteren v0.2.x-Installationen kann noch der frühere manuelle Lovelace-Resource-Eintrag `/mobile_fuel_stations/mobile-fuel-stations-card.js` vorhanden sein. Aktualisiere zuerst die Integration, starte Home Assistant neu und prüfe Karte und Card Picker. Entferne den alten Eintrag anschließend über die Home-Assistant-Oberfläche und lade Browser oder Companion-App vollständig neu. Bearbeite `.storage` niemals manuell.

## Standort-Entity

Die Standort-Entity muss die numerischen Attribute `latitude` und `longitude` bereitstellen. Bei Bewegungsupdates werden die Suche und der Cooldown anhand der konfigurierten Bewegungsschwelle gesteuert.

## Erzeugte Entities

Der Overview-Sensor stellt unter anderem folgende Attribute bereit:

`radius`, `fuel_type`, `location_entity`, `station_count`, `station_entities`, `last_successful_update`, `reference_latitude`, `reference_longitude`, `distance_since_last_search`, `nearest_station`, `cheapest_station`

Die Stations-Slots stellen unter anderem bereit:

`station_id`, `station_name`, `brand`, `price`, `distance`, `is_open`, `street`, `house_number`, `postcode`, `place`, `latitude`, `longitude`

Die Slot-Entity-ID und Unique-ID bleiben stabil. Die Tankstelle in einem Slot kann sich nach einer Aktualisierung ändern; der Anzeigename folgt der aktuellen Tankstelle. Ein leerer Slot ist `unavailable`. Preiswerte verwenden `EUR/L`.

## Alternative Dashboard-Beispiele

Die mitgelieferte Mobile Fuel Stations Card ist der empfohlene Standardweg. Alternativ können die erzeugten Sensoren mit normalen Home-Assistant-Karten dargestellt werden. Mushroom Cards sind eine optionale zusätzliche Custom-Card-Abhängigkeit.

## Fehlerbehebung

- **Keine Tankstellen:** Standort, Radius, Kraftstofftyp und API-Zugang prüfen.
- **Standort nicht verfügbar:** Prüfen, ob die Standort-Entity aktuelle `latitude`- und `longitude`-Attribute liefert.
- **Preise aktualisieren sich nicht:** Overview-Sensor, letzte erfolgreiche Aktualisierung und Home-Assistant-Logs prüfen.
- **Card Picker zeigt die Karte nicht:** Integration aktualisieren, Home Assistant vollständig neu starten, Browser oder Companion-App vollständig neu laden und prüfen, ob der Overview-Sensor existiert. Ein manueller Resource-Eintrag ist bei aktuellen Installationen nicht erforderlich.
- **API-Probleme:** Tankerkönig-API-Key und Fehlermeldungen in den Logs prüfen.
- **Bewegungsupdates:** Bewegungsschwelle und Cooldown kontrollieren.
- **Entity-IDs:** Die erzeugten Entity-IDs in **Einstellungen → Geräte & Dienste → Entitäten** prüfen.

Wenn der Fehler bleibt, prüfe Frontend-Logs und Browser-Konsole und erstelle ein GitHub Issue mit relevanten, redigierten Logs.

## Datenschutz und Sicherheit

Provider-Credentials werden im Config Entry gespeichert und dürfen nicht veröffentlicht werden. Der konfigurierte Standort wird für die Tankstellensuche an den ausgewählten Provider übertragen. Diagnostics sollten vor dem Teilen auf sensible Daten geprüft werden. Veröffentliche keine exakten Standortdaten oder Zugangsdaten in Issues.

## API und Attribution

Die Tankstellendaten stammen vom konfigurierten Tankerkönig- oder Petromap-Dienst. Beachte die jeweiligen Nutzungsbedingungen, Berechtigungen und API-Limits. Petromap-Runtime-Unterstützung ist in der Beta enthalten; der reale Zugriff hängt von den Berechtigungen des konfigurierten Developer-Keys ab.

## Entwicklung und Beiträge

Entwicklungs- und Testhinweise stehen in [CONTRIBUTING.md](CONTRIBUTING.md). Benutzerrelevante Änderungen werden in `README.md` und `README.en.md` synchron gehalten.

## Lizenz

Siehe [LICENSE](LICENSE).
