# Mobile Fuel Stations – deutsche Dokumentation

Die vollständige deutsche Dokumentation befindet sich in [README.md](README.md).
Stable `v0.5.1` ergänzt das responsive Layout mit Container
Queries, eine einspaltige Tankstellenliste, die Anzeige der tatsächlichen
Datenquelle, Stale-Daten- und automatische Recovery-Zustände, verbesserte
Fehlerdiagnose sowie eine zusätzliche Custom-Element-Registrierung beim
Browser-`load`-Event. Der sporadische Edge-/iOS-Ladefehler ist in der
produktiven Home-Assistant-Umgebung noch nicht belastbar verifiziert und gilt
nicht als vollständig behoben.

## Markenlogos in v0.6.0-beta.1

Die Beta kann das vorhandene Stationsattribut `brand` provider-unabhängig auf
lokale Nutzerlogos abbilden. `show_brand_logos` ist standardmäßig `false`,
damit v0.5.1-Dashboards unverändert bleiben.

Es werden **keine fremden Markenbilder mitgeliefert**. Die MIT-Lizenz von
Referenz-Code überträgt nicht automatisch Markenrechte oder Bildlizenzen.
Unterstützte Aliase sind Aral, Shell, Esso, JET, Total/TotalEnergies, HEM,
AVIA/AVIA Express, ORLEN/ORLEN Express, OMV, Q1/Q 1 und Raiffeisen. Sie werden
aus `brand` mit normalisierter Groß-/Kleinschreibung, Unicode-Akzenten,
Leerzeichen und Satzzeichen erkannt; der Stationsname wird nicht als Quelle
für eine Zuordnung verwendet.

Eigene PNG-Dateien kommen nach `/config/www/fuel-logos/` und sind in HA unter
`/local/fuel-logos/` erreichbar. Das Dateischema ist `<alias>.png`, zum
Beispiel `shell.png`. `logo_path` akzeptiert nur lokale `/local/...`- oder
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
Funktion nicht, und HACS lädt keine Logos automatisch nach.
