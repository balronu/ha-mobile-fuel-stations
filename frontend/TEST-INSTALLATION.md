# Testinstallation der Karte über HACS

HACS installiert die Integration einschließlich des produktiven Bundles unter
`custom_components/mobile_fuel_stations/frontend/mobile-fuel-stations-card.js`.
Die Build-Quelle liegt unter `frontend/`; das Bundle wird beim Build automatisch
in die Integration kopiert. Eine manuelle Kopie nach `/config/www` ist nicht
erforderlich.

Die versionslose URL nach dem Home-Assistant-Neustart ist:

`/mobile_fuel_stations/mobile-fuel-stations-card.js`

## Einmalige Lovelace-Ressource

Die Integration stellt den statischen Pfad automatisch bereit. Home Assistant
bietet für Custom Integrations jedoch keine öffentliche, robuste API zur
automatischen Änderung der Lovelace-Resource-Registry. Deshalb einmalig unter
**Einstellungen → Dashboards → Ressourcen** anlegen:

- URL: `/mobile_fuel_stations/mobile-fuel-stations-card.js`
- Ressourcentyp: `JavaScript-Modul` bzw. `module`

Die URL bleibt bei späteren HACS-Updates unverändert. Der statische HA-Pfad wird
ohne zusätzliche Cache-Header registriert; Browser oder Companion-Clients können
bei Bedarf trotzdem einen Frontend-Neuladen bzw. Cache-Refresh benötigen. Alte
versionierte Beta-URLs bleiben als Query-Varianten des gleichen Pfads erreichbar.

Navigation kann im visuellen Editor zwischen Automatisch, Apple Karten und Google
Maps gewählt werden. Automatisch nutzt iOS/iPadOS Apple Maps und Android bzw.
Desktop den Google-Weblink; die konkrete Übergabe ist clientabhängig.

## Minimales Karten-YAML

`<OVERVIEW_ENTITY>` muss durch den Overview-Sensor des gewünschten Config Entries
ersetzt werden:

```yaml
type: custom:mobile-fuel-stations-card
entity: <OVERVIEW_ENTITY>
```

Das produktive `dashboard_wohnmobil` wird durch diese Runde nicht verändert.
