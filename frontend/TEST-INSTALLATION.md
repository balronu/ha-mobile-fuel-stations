# Testinstallation der Karte

Die gebaute Datei liegt nach `npm run build` unter:

`frontend/dist/mobile-fuel-stations-card.js`

## Testweise nach Home Assistant kopieren

Die Datei kann für einen isolierten Test als statische Lovelace-Ressource in das
`/config/www/`-Verzeichnis der Home-Assistant-Testinstanz kopiert werden, zum
Beispiel:

```sh
scp frontend/dist/mobile-fuel-stations-card.js \
  <ha-host>:/config/www/mobile-fuel-stations-card.js
```

Alternativ kann sie über den Datei-Editor oder die vorhandene
Home-Assistant-Dateiübertragung nach `/config/www/mobile-fuel-stations-card.js`
übertragen werden. Diese Anleitung führt die Installation nicht automatisch aus.

## Lovelace-Ressource

Unter **Einstellungen → Dashboards → Ressourcen** eine JavaScript-Ressource
anlegen:

- URL: `/local/mobile-fuel-stations-card.js`
- Ressourcentyp: `JavaScript-Modul`

Nach dem Laden der Ressource den Browser-Cache für den Test-Dashboard-Tab
aktualisieren.

## Minimales Karten-YAML

`<OVERVIEW_ENTITY>` muss durch den Overview-Sensor des gewünschten Config Entries
ersetzt werden:

```yaml
type: custom:mobile-fuel-stations-card
entity: <OVERVIEW_ENTITY>
```

Das produktive `dashboard_wohnmobil` wird durch diese Runde nicht verändert.
