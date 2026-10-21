# Mobile Fuel Stations v0.8.4-beta.3

## Deutsch

Diese Beta korrigiert die im visuellen Home-Assistant-Karteneditor gefundenen
Darstellungsfehler. Die gemeinsame Priorisierung, die drei Kartenmodi und die
Kompatibilität bestehender YAML-/Storage-Karten bleiben erhalten.

### Korrekturen

- `show_dividers: false` entfernt nun die dekorativen Listenränder tatsächlich;
  eigenständige Rahmen der hervorgehobenen Kacheln bleiben erhalten.
- Individuelle Listen zeigen die Entfernung nur noch einmal in der Metazeile.
- Ausgeblendete Logos, Navigation und Preise entfernen ihre nicht benötigten
  Grid-Spalten und Container.
- Kraftstofflabels werden bei Deaktivierung nicht als leere Spans gerendert.
- Lange Namen bleiben über `title` zugänglich; die Kurzansicht verwendet Ellipsis.
- Die Frontend-Version und Resource-URL verwenden `v=0.8.4-beta.3`.

### Visuelle Abnahme

Die isolierte Chromium-Fixture nutzt fünf Mock-Tankstellen und prüft DOM,
berechnete Separator-CSS-Werte und Kartenhöhen. Bei einer Kartenbreite von
390px standen die beiden hervorgehobenen Kacheln mit jeweils ca. 191px
nebeneinander; unter 360px wechselten sie auf eine Spalte. Die kompakte
Ansicht blieb bei 65px pro Zeile. Die individuelle Liste maß normal ca. 769px
und kompakt ca. 611px mit denselben Testdaten. Ohne Trennlinien wurden für
alle fünf Zeilen `border-top: 0px` gemessen.

### Grenzen

Ein bereits ausgeführtes JavaScript-Modul kann im offenen HA-Tab nicht sicher
ersetzt werden. Der versionierte Resource-Key verhindert alte URL-Wieder-
verwendung; je nach HA-Frontend oder Companion-App kann weiterhin ein einmaliges
Dashboard-Neuladen erforderlich sein. Es gibt keinen automatischen Hard-Reload.

## English

This beta fixes the visual and editor issues found during the Home Assistant
card-editor audit. Shared prioritization, all three display modes, and existing
YAML/storage-card compatibility remain unchanged.

### Fixes

- `show_dividers: false` now removes decorative list separators while retaining
  the borders of standalone highlight tiles.
- Individual lists no longer render distance twice.
- Disabled logos, navigation, and prices no longer leave empty grid columns.
- Disabled fuel labels do not leave empty spans.
- Full names remain accessible through `title`; short names use ellipsis.
- Frontend version and resource URL use `v=0.8.4-beta.3`.

### Visual acceptance

The isolated Chromium fixture uses five mock stations and checks DOM,
computed separator CSS, and card heights. At a 390px card width, the two
highlight tiles rendered side by side at about 191px each; below 360px they
stacked. Compact rows remained 65px high. With identical data, the individual
list measured about 769px at normal density and 611px at compact density.
With dividers disabled, all five rows measured `border-top: 0px`.

### Limitations

An already executed JavaScript module cannot be safely replaced in an open HA
tab. The versioned resource key prevents reuse of the old URL, but one
dashboard reload may still be required depending on the HA frontend or
Companion app. No automatic hard reload is claimed.
