# Mobile Fuel Stations v0.8.4-beta.4

## Deutsch

Beta.4 ist ein reines Fehleraudit- und Layoutkorrektur-Release. Es fügt keine
Provider-, Backend- oder Integrationsfunktionen hinzu.

### Sieben geprüfte Punkte

1. **Doppelte Entfernung:** Ursache war die parallele Verwendung des allgemeinen
   Preis-Grids und der individuellen Metazeile. Die individuelle Station besitzt
   jetzt eine gemeinsame Primär-/Preis-/Metazeilenstruktur; ein Frontend-Test
   zählt die sichtbare Distanz exakt einmal. Chromium bestätigt eine Distanz pro
   Zeile.
2. **Trennlinien:** Der Modus-Selektor wird nun direkt auf `.station` angewandt;
   `border-top` misst bei deaktivierten Trennlinien `0px`. Test und Screenshot
   decken die konfigurierte Liste sowie Kacheln + Liste ab.
3. **Abrufmodus:** Das Label wird nur noch gerendert, wenn der Abrufmodus selbst
   aktiviert ist. Sind Abrufmodus und Aktualisieren aus, existiert kein Controls-
   Container. Editor- und Render-Test prüfen beide Zustände.
4. **Kompakte Zeilen:** Preise stehen neben dem Namen, Adresse darunter und
   Status/Entfernung/Provider in einer Metazeile. Kompakt reduziert die gleiche
   Testkarte von ca. 834px normal auf ca. 653px.
5. **Preis/Entfernung:** Beide Werte haben im individuellen Layout feste,
   kollisionsfreie Bereiche; die Entfernung bleibt ausschließlich in der
   Metazeile. Chromium prüft Textvorkommen und horizontalen Überlauf.
6. **Kacheln + Liste:** Die normalen Listeneinträge verwenden denselben
   korrigierten Renderer und dieselben Separator-/Dichte-Regeln. Kacheln bleiben
   bei 390px zweispaltig und stapeln unter 360px.
7. **Kartentitel:** Ein leeres Titel-Feld erhält einen verständlichen Hinweis
   („Standard: Tankstellen in der Nähe / Default: Nearby fuel stations“), ohne
   eine bestehende Konfiguration zu verändern.

### Vergleich unter identischen Bedingungen

| Bundle | normal, 390px | kompakt, 390px |
| --- | ---: | ---: |
| beta.2 | 948px | 790px |
| beta.3 | 873px | 715px |
| beta.4 | 834px | 653px |

Alle Messungen verwenden dieselben fünf Mock-Tankstellen, denselben Header und
denselben Abrufmodus. Screenshots liegen unter
`docs/releases/assets/v0.8.4-beta.4/`.

Die versionierte Resource-URL lautet:

```text
/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.8.4-beta.4
```

Ein bereits ausgeführtes JavaScript-Modul kann im offenen HA-Tab weiterhin nicht
sicher ersetzt werden; ein einmaliges Dashboard-Neuladen kann je nach Frontend
oder Companion-App erforderlich sein. Es gibt keinen automatischen Hard-Reload.

## English

Beta.4 is a focused visual-audit and layout-correction release. It adds no
provider, backend, or integration features.

The individual renderer now places price beside the station name, address below,
and status/distance/provider in one metadata row. Divider-off removes all list
`border-top` rules, the fetch-mode label disappears with its controls, and an
empty custom title field shows a non-persisted default hint. The same renderer
is used by all individual sublayouts.

Under identical five-station mock data, the measured card heights at 390px were:

| Bundle | normal | compact |
| --- | ---: | ---: |
| beta.2 | 948px | 790px |
| beta.3 | 873px | 715px |
| beta.4 | 834px | 653px |

The versioned resource URL is
`/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.8.4-beta.4`.
An already executed module may still require one dashboard reload; no automatic
hard reload is claimed.
