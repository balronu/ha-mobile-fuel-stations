# Mobile Fuel Stations

**[English version](README.en.md)**

Mobile Fuel Stations ist eine Home-Assistant-Custom-Integration für nahegelegene Tankstellen anhand einer frei wählbaren Standort-Entity. Sie eignet sich besonders für Fahrzeuge, Wohnmobile, GPS-Tracker und andere bewegliche Objekte.

Die Beta unterstützt **Tankerkönig**, **Petromap v2** und explizit **Nakordoni**.
Im Auto-Modus wird weiterhin nur die bestehende Tankerkönig-/Petromap-Policy
verwendet. Nakordoni-Zugriff hängt von API-Key, genehmigtem Markt und
Providerquoten ab.

## Stable und Pre-Release

- **Stable:** `v0.4.0` ist die stabile Version für normale Nutzer.
- **Beta:** `v0.5.0-beta.6` ist die aktuelle Pre-Release-Version mit den neuen
  Provider- und Diagnosefunktionen.

Wenn du die Beta testen möchtest, wähle in HACS bei Bedarf die **aktuelle
Pre-Release-Version**. Eine Pre-Release kann sich ändern und ist nicht für
produktive Installationen gedacht.

## Funktionen

- Einrichtung und Optionen über die Home-Assistant-Oberfläche
- frei wählbare Standort-Entity mit `latitude`- und `longitude`-Attributen
- Diesel, E5, E10 und LPG / Autogas
- HVO100 ist noch nicht auswählbar, weil kein verifizierter providerbezogener API-Selektor vorliegt.
- Nakordoni unterstützt in dieser Beta explizit Diesel, E5, E10 und LPG; HVO/HVO100 bleibt blockiert.
- Nakordoni begrenzt den Radius auf 25 km, verwendet eine Anfrage pro Refresh und verlangt sichtbare Attribution: **Data by nakordoni.eu**.
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

## Unterstützte Provider

| Provider | Einsatz | API-Key | Kraftstoffe in MFS | Hinweise |
| --- | --- | --- | --- | --- |
| [Tankerkönig](https://creativecommons.tankerkoenig.de/) | Deutschland | Ja | Diesel, E5, E10 | LPG ist im Tankerkönig-Adapter nicht unterstützt; Radius maximal 25 km. |
| [Petromap](https://developer.petromap.eu/) | Länder- und Preisabdeckung gemäß dem aktuellen Petromap-Vertrag | Ja | Diesel, E5, LPG | Abdeckung und Preisqualität unterscheiden sich je Land; E10 ist im aktuellen MFS-Petromap-Modus nicht als expliziter Kraftstoff verfügbar. |
| [Nakordoni](https://nakordoni.dev/) | Explizit auswählbarer Provider in beta.6 | Ja | Diesel, E5, E10, LPG | Nicht Bestandteil von Auto; maximal 25 km; Marktfreigabe und Quoten können erforderlich sein; sichtbare Attribution ist Pflicht. |

HVO und HVO100 werden derzeit von MFS nicht unterstützt. HVO wird nicht
stillschweigend als Diesel behandelt.

## Voraussetzungen

- Home Assistant mit HACS oder Zugriff auf eine manuelle Custom-Integration-Installation
- eine Standort-Entity mit `latitude` und `longitude`
- ein Tankerkönig-, Petromap-v2- oder Nakordoni-API-Key je nach Provider-Modus

## Installation

### HACS (Custom Repository)

1. Öffne **HACS → Integrationen**.
2. Öffne das Drei-Punkte-Menü und wähle **Benutzerdefinierte Repositories**.
3. Füge `https://github.com/balronu/ha-mobile-fuel-stations` als Repository mit der Kategorie **Integration** hinzu.
4. Installiere **Mobile Fuel Stations**.
5. Starte Home Assistant vollständig neu.
6. Füge die Integration unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** hinzu.

Die Dashboard-Karte wird automatisch registriert. Die automatisch registrierte
Frontend-URL `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.5.0-beta.6`
enthält die Integrationsversion. Jede Integrationsversion erhält dadurch eine
eigene Resource-URL, sodass veralteter Card-JavaScript-Code aus Caches bei
einem Versionswechsel nicht weiterverwendet wird. Nach einem HACS-Update
genügt ein vollständiger Home-Assistant-Neustart; ein manuelles Leeren des
Browser-Caches oder Ändern der Lovelace-Resource ist bei aktuellen
Installationen nicht erforderlich.

### Manuelle Installation

Lade das Repository herunter und kopiere den Ordner `custom_components/mobile_fuel_stations` nach `config/custom_components/`. Starte Home Assistant anschließend vollständig neu und richte die Integration über **Einstellungen → Geräte & Dienste** ein.

## Einrichtung

Wähle die Standort-Entity, den Radius, den Kraftstofftyp und die Anzahl der Stations-Slots. Wähle anschließend Tankerkönig, Petromap, Nakordoni oder Auto und hinterlege die dafür benötigten Credentials. Bei der ersten Aktivierung von Petromap bzw. Nakordoni wird die jeweilige Privacy-Erklärung angezeigt. Config Flow und Options Flow bleiben network-free; der erste Provider-Aufruf erfolgt im normalen Runtime-Refresh.

Die Provider-Auswahl und die übrigen Einstellungen werden im Config Flow bzw.
später im Options Flow von Home Assistant vorgenommen. Die Integration liest
die gewählte Standort-Entity, den Radius, den Kraftstoff und die Stationszahl
aus dieser Konfiguration. Es gibt keine YAML-Konfiguration für die
Integration.

### API-Schlüssel

Die Schlüssel werden direkt im Home-Assistant-Dialog eingegeben. Sie gehören
nicht in YAML, README, GitHub oder Logs.

- **Tankerkönig:** Einen persönlichen Schlüssel kannst du über das
  [offizielle Onboarding](https://onboarding.tankerkoenig.de/) beantragen. Die
  [offizielle API-Dokumentation](https://creativecommons.tankerkoenig.de/?page=info)
  beschreibt die Nutzung und die Bedingungen.
- **Petromap:** Developer-Zugang und API-Key werden über das
  [offizielle Petromap-Developer-Portal](https://developer.petromap.eu/)
  beantragt bzw. verwaltet. Die [API-Dokumentation](https://developer.petromap.eu/docs/v2)
  und der [Developer Agreement](https://developer.petromap.eu/terms) gelten für
  die Nutzung.
- **Nakordoni:** Erstelle bzw. verwalte den Zugang über das
  [offizielle Developer-Portal](https://nakordoni.dev/), die
  [Dokumentation](https://nakordoni.dev/de/docs) und – sofern für deinen
  Account verfügbar – das [Dashboard](https://nakordoni.dev/de/dashboard).
  Der benötigte Markt kann eine separate Freigabe erfordern. MFS verwendet den
  Schlüssel nur im normalen Runtime-Refresh.

Provider-spezifische Schlüssel werden getrennt gespeichert. Ein Wechsel des
Providers löscht die bereits gespeicherten Schlüssel der anderen Provider
nicht; beim Zurückwechseln muss ein vorhandener Schlüssel normalerweise nicht
erneut eingegeben werden. Eine Reauthentifizierung ersetzt nur den Schlüssel
des betroffenen Providers.

### Provider wechseln

Provider werden im Options Flow gewechselt. Tankerkönig, Petromap, Nakordoni
und Auto sind getrennte Modi. Beim erstmaligen Aktivieren von Petromap oder
Nakordoni wird die jeweilige Datenschutzbestätigung angezeigt. Fehlende
Credentials werden anschließend nur für den gewählten Modus abgefragt.

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

## Nakordoni

Nakordoni überträgt für die Tankstellensuche Standortkoordinaten, Suchradius
und Kraftstofftyp an den externen Anbieter; eine Device-ID wird von dieser
Integration nicht übertragen. Die Daten können abhängig von Account und Markt
verzögert oder unvollständig sein. Preise behalten den Provider-Zeitstempel und
das Stale-/Qualitätsmerkmal. Die Karte zeigt bei Nakordoni-Daten die klickbare
Attribution **[Data by nakordoni.eu](https://nakordoni.eu)**. Eine Nakordoni-
Credential wird niemals in Options, Entity-Attributen, Diagnostics oder
Frontend-Code gespeichert.

Bei Providerfehlern stellt beta.6 sichere technische Diagnosedaten bereit,
beispielsweise Provider, HTTP-Status, normalisierten Fehlercode,
`Retry-After` sowie Quota-Limit und Remaining. Credentials, Authorization-
Header, exakte Koordinaten, Request-URLs und rohe Providerantworten werden
nicht in diesen Diagnosen gespeichert.

## Upgrade von älteren Versionen

Für das Upgrade auf v0.5.0-beta.6 genügt ein Update über HACS und ein vollständiger Home-Assistant-Neustart. Beta.6 ergänzt sichere Nakordoni-Fehlerdiagnostik für Rate-/Quota-/Berechtigungsfehler; es werden keine zusätzlichen Providerrequests ausgeführt und keine Credentials oder Standortdaten protokolliert.

Für das Upgrade auf v0.5.0-beta.5 genügt ein Update über HACS und ein vollständiger Home-Assistant-Neustart. Beta.5 ergänzt den expliziten Nakordoni-Provider; bestehende beta.4-Entries bleiben ohne Migration kompatibel.

Für das Upgrade von v0.5.0-beta.2 auf v0.5.0-beta.3 genügt ein Update über HACS und ein vollständiger Home-Assistant-Neustart. Bestehende Tankerkönig-Konfigurationen bleiben kompatibel. Der Tankerkönig-Radius ist auf 25 km begrenzt; bestehende Konfigurationen mit einem höheren gespeicherten Wert werden beim API-Aufruf defensiv auf 25 km begrenzt.

Bei älteren v0.2.x-Installationen kann noch der frühere manuelle Lovelace-Resource-Eintrag `/mobile_fuel_stations/mobile-fuel-stations-card.js` vorhanden sein. Aktualisiere zuerst die Integration, starte Home Assistant neu und prüfe Karte und Card Picker. Entferne den alten Eintrag anschließend über die Home-Assistant-Oberfläche und lade Browser oder Companion-App vollständig neu. Bearbeite `.storage` niemals manuell.

## Standort-Entity

Die Standort-Entity muss die numerischen Attribute `latitude` und `longitude` bereitstellen. Bei Bewegungsupdates werden die Suche und der Cooldown anhand der konfigurierten Bewegungsschwelle gesteuert.

## Auto-Modus

Auto wählt anhand von Land und Kraftstoff nach der aktuellen MFS-Policy. Für
Deutschland wird Tankerkönig bevorzugt, wenn die Kombination unterstützt wird;
Petromap kann für dafür geeignete Länder und Kraftstoffe verwendet werden.
Nakordoni ist in beta.6 **nicht** Bestandteil des Auto-Modus. Auto fragt nicht
automatisch alle Provider parallel ab und führt keine unnötigen Fallback-
Requests für nicht unterstützte Kombinationen aus.

Eine spätere Multi-Provider-Auswahl ist nur geplant und in beta.6 nicht
vorhanden.

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

Die Tankstellendaten stammen vom konfigurierten Provider. Beachte die
jeweiligen Nutzungsbedingungen, Berechtigungen, Quoten und API-Limits.
Petromap-Runtime-Unterstützung ist in der Beta enthalten; der reale Zugriff
hängt von den Berechtigungen des konfigurierten Developer-Keys und der
Länderabdeckung ab.

Für Nakordoni zeigt die Karte bei Nakordoni-Daten sichtbar und klickbar
**[Data by nakordoni.eu](https://nakordoni.eu/)** an. Für Petromap gelten der
aktuelle [Developer Agreement](https://developer.petromap.eu/terms) und die
jeweiligen Providerbedingungen; eine separate Petromap-Attribution wird von
MFS derzeit nicht in der Karte dargestellt.

## Entwicklung und Beiträge

Entwicklungs- und Testhinweise stehen in [CONTRIBUTING.md](CONTRIBUTING.md). Die deutsche und englische Dokumentation werden als separate README-Dateien gepflegt.

## Lizenz

Siehe [LICENSE](LICENSE).
