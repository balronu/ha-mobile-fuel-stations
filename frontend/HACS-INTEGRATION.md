# HACS-Auslieferung der Lovelace-Karte

- HACS bleibt ein einziges Repository mit der Kategorie `integration`.
- Das kanonische Frontend liegt unter `frontend/src/`.
- `npm run build` erzeugt `frontend/dist/mobile-fuel-stations-card.js` und kopiert
  exakt dieses Artefakt nach
  `custom_components/mobile_fuel_stations/frontend/mobile-fuel-stations-card.js`.
- Home Assistant registriert beim Integrations-Setup den statischen Pfad
  `/mobile_fuel_stations` über `async_register_static_paths`.
- Die versionslose Resource-URL ist `/mobile_fuel_stations/mobile-fuel-stations-card.js`.

Die automatische Änderung der Lovelace-Resource-Registry wird bewusst nicht
implementiert: Dafür gibt es keine dokumentierte öffentliche API für Custom
Integrations. Das Bearbeiten von `.storage/lovelace_resources` wäre ein privates
und fragiles Verhalten. Daher ist genau ein manueller Resource-Eintrag nötig;
mehrere Config Entries erzeugen trotzdem nur einen statischen Pfad. Die URL muss
bei HACS-Updates nicht geändert werden. Die öffentliche HA-API garantiert
allerdings keinen sofortigen Cache-Flush in jedem Browser/Companion-Client.
