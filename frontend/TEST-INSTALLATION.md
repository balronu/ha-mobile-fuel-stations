# Testinstallation der Karte über HACS

HACS installiert die Integration einschließlich des produktiven Bundles unter
`custom_components/mobile_fuel_stations/frontend/mobile-fuel-stations-card.js`.
Die Build-Quelle liegt unter `frontend/`; das Bundle wird beim Build automatisch
in die Integration kopiert. Eine manuelle Kopie nach `/config/www` ist nicht
erforderlich.

Die stabile URL nach dem Home-Assistant-Neustart ist:

`/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.2.0-beta.2`

## Einmalige Lovelace-Ressource

Die Integration stellt den statischen Pfad automatisch bereit. Home Assistant
bietet für Custom Integrations jedoch keine öffentliche, robuste API zur
automatischen Änderung der Lovelace-Resource-Registry. Deshalb einmalig unter
**Einstellungen → Dashboards → Ressourcen** anlegen:

- URL: `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.2.0-beta.2`
- Ressourcentyp: `JavaScript-Modul` bzw. `module`

Bei einem späteren Release wird die Versionsnummer im URL-Query deterministisch
erhöht; den eigenen Resource-Eintrag dann einmal auf die neue URL aktualisieren.

## Minimales Karten-YAML

`<OVERVIEW_ENTITY>` muss durch den Overview-Sensor des gewünschten Config Entries
ersetzt werden:

```yaml
type: custom:mobile-fuel-stations-card
entity: <OVERVIEW_ENTITY>
```

Das produktive `dashboard_wohnmobil` wird durch diese Runde nicht verändert.
