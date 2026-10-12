# Mobile Fuel Stations – deutsche Dokumentation

Die vollständige deutsche Dokumentation befindet sich in [README.md](README.md).
Stable `v0.5.1` ergänzt das responsive Layout mit Container
Queries, eine einspaltige Tankstellenliste, die Anzeige der tatsächlichen
Datenquelle, Stale-Daten- und automatische Recovery-Zustände, verbesserte
Fehlerdiagnose sowie eine zusätzliche Custom-Element-Registrierung beim
Browser-`load`-Event. Der sporadische Edge-/iOS-Ladefehler ist in der
produktiven Home-Assistant-Umgebung noch nicht belastbar verifiziert und gilt
nicht als vollständig behoben.

## Markenlogos in v0.6.0-beta.4

Die Beta kann das vorhandene Stationsattribut `brand` provider-unabhängig auf
lokale Nutzerlogos abbilden. Neue Karten versuchen Logos standardmäßig;
`show_brand_logos: false` bleibt der ausdrückliche Opt-out.

Beta.2 hält die Entities auch dann angelegt, wenn der GPS-Tracker beim
Home-Assistant-Start vorübergehend `unknown`, `unavailable` oder ohne gültige
Koordinaten ist. Der erste gültige Tracker-Zustand löst genau einen
ereignisgesteuerten Refresh aus. Vorübergehende Provider-/Netzwerkfehler werden
über den normalen Polling-Zyklus erneut versucht; ein echter Neustarttest in
der produktiven HA-Umgebung wurde nicht durchgeführt.

Beta.2 liefert sechs geprüfte SVGs für Aral, Shell, JET, TotalEnergies, ORLEN
und OMV mit. Quellen, SHA256-Prüfsummen und verbleibende Markenrechtsrisiken
stehen in [`BRAND_LOGOS.md`](BRAND_LOGOS.md). Es besteht keine Partnerschaft
oder Unterstützung durch die dargestellten Marken. Unterstützte Aliase sind
Aral, Shell, JET, Total/TotalEnergies, ORLEN/ORLEN Express und OMV. Sie werden
aus `brand` mit normalisierter Groß-/Kleinschreibung, Unicode-Akzenten,
Leerzeichen und Satzzeichen erkannt; der Stationsname wird nicht als Quelle
für eine Zuordnung verwendet.

Mitgelieferte Logos werden automatisch über HACS installiert. Eigene SVG-Dateien
kommen nach `/config/www/fuel-logos/` und sind in HA unter `/local/fuel-logos/`
erreichbar. Das Dateischema ist `<alias>.svg`, zum Beispiel `shell.svg`.
`logo_path` akzeptiert nur lokale `/local/...`- oder
`/hacsfiles/...`-Pfade; externe URLs und `..` werden abgelehnt. Unbekannte
Marken, fehlende Dateien und Bildladefehler zeigen das Zapfsäulen-Symbol.
Logos erscheinen in Liste, **Nächste** und **Günstigste**, mit fester Fläche,
erhaltenem Seitenverhältnis und Alt-Text.

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.mobile_fuel_stations_device_tracker_wohnmobil_zoe_nearby_stations
navigation: true
show_brand_logos: true
logo_path: /local/fuel-logos/
```

Es gibt derzeit keinen Screenshot im Repository; Beispiel und automatisierte
Render-Tests sind die geprüfte Darstellung. v0.5.1 Stable enthält diese Beta-
Funktion nicht; die sechs Beta.2-Logos werden mit der Integration installiert.
