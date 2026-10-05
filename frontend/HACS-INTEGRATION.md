# HACS-Auslieferung der Lovelace-Karte

- HACS bleibt ein einziges Repository mit der Kategorie `integration`.
- Das kanonische Frontend liegt unter `frontend/src/`.
- `npm run build` erzeugt `frontend/dist/mobile-fuel-stations-card.js` und kopiert
  exakt dieses Artefakt nach
  `custom_components/mobile_fuel_stations/frontend/mobile-fuel-stations-card.js`.
- Home Assistant registriert beim Integrations-Setup den statischen Pfad
  `/mobile_fuel_stations` über `async_register_static_paths`.
- Die versionslose Resource-URL ist `/mobile_fuel_stations/mobile-fuel-stations-card.js`.

Die Integration registriert die Karte automatisch über die unterstützte
Home-Assistant-Frontend-API. Bei Neuinstallationen ist daher kein manueller
Lovelace-Resource-Eintrag erforderlich. Mehrere Config Entries erzeugen trotzdem
nur einen statischen Pfad. Die URL muss bei HACS-Updates nicht geändert werden.
Die öffentliche HA-API garantiert allerdings keinen sofortigen Cache-Flush in
jedem Browser/Companion-Client. Bestehende v0.2.x-Installationen dürfen ihren
alten manuellen Resource-Eintrag nach erfolgreichem Update, Neustart und
Funktionstest über die Home-Assistant-Oberfläche entfernen. `.storage` darf
nicht manuell bearbeitet werden.
