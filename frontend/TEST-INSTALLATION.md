# Testinstallation der Karte über HACS

HACS installiert die Integration einschließlich des produktiven Bundles unter
`custom_components/mobile_fuel_stations/frontend/mobile-fuel-stations-card.js`.
Die Build-Quelle liegt unter `frontend/`; das Bundle wird beim Build automatisch
in die Integration kopiert. Eine manuelle Kopie nach `/config/www` ist nicht
erforderlich.

Die versionslose URL nach dem Home-Assistant-Neustart ist:

`/mobile_fuel_stations/mobile-fuel-stations-card.js`

## Automatische Registrierung

Die Integration registriert die Karte automatisch über die unterstützte
Home-Assistant-Frontend-API. Bei einer Neuinstallation ist kein manueller
Lovelace-Resource-Eintrag erforderlich. Die URL bleibt bei späteren HACS-Updates
unverändert. Browser oder Companion-Clients können bei Bedarf trotzdem einen
Frontend-Neuladen bzw. Cache-Refresh benötigen.

Bei einem Upgrade von v0.2.x darf ein bereits vorhandener manueller Resource-
Eintrag erst nach erfolgreichem Update, vollständigem Neustart und Funktionstest
über die Home-Assistant-Oberfläche entfernt werden. `.storage` niemals manuell
bearbeiten.

Navigation kann im visuellen Editor zwischen Automatisch, Apple Karten, Google
Maps und Waze gewählt werden. Automatisch nutzt iOS/iPadOS Apple Maps und
Android bzw. Desktop den Google-Weblink; die konkrete Übergabe ist
clientabhängig. Waze wird nur bei expliziter Auswahl verwendet.

## Minimales Karten-YAML

`<OVERVIEW_ENTITY>` muss durch den Overview-Sensor des gewünschten Config Entries
ersetzt werden:

```yaml
type: custom:mobile-fuel-stations-card
entity: <OVERVIEW_ENTITY>
```

Das produktive `dashboard_wohnmobil` wird durch diese Runde nicht verändert.
