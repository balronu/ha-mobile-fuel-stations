# HACS-Auslieferung der Lovelace-Karte

- HACS bleibt ein einziges Repository mit der Kategorie `integration`.
- Das kanonische Frontend liegt unter `frontend/src/`.
- `npm run build` erzeugt `frontend/dist/mobile-fuel-stations-card.js` und kopiert
  exakt dieses Artefakt nach
  `custom_components/mobile_fuel_stations/frontend/mobile-fuel-stations-card.js`.
- Home Assistant registriert beim Integrations-Setup den statischen Pfad
  `/mobile_fuel_stations` über `async_register_static_paths`.
- Die automatisch registrierte JavaScript-URL enthält die Integrationsversion,
  zum Beispiel `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.8.0-beta.4`.
- Der physische StaticPath und die ausgelieferte Datei bleiben
  `/mobile_fuel_stations/mobile-fuel-stations-card.js`.

Die Integration registriert die Karte automatisch über die unterstützte
Home-Assistant-Frontend-API. Bei Neuinstallationen ist daher kein manueller
Lovelace-Resource-Eintrag erforderlich. Mehrere Config Entries erzeugen trotzdem
nur einen statischen Pfad. Die Versionsnummer erzeugt bei HACS-Updates
automatisch eine neue Cache-URL.

## Mehrere Fahrzeuge und Overview-Entities

Für jedes Fahrzeug wird ein eigener Config Entry mit eigener Overview-Entity
angelegt. Wähle im visuellen Karteneditor die Overview-Entity des jeweiligen
Fahrzeugs; ab v0.7.1 werden auch integrationszugehörige Entities mit Zustand
`unavailable` zur Auswahl angeboten. Bestehende YAML-Karten mit einer direkt
eingetragenen Entity-ID bleiben kompatibel. Die automatische Registrierung der
Lovelace-Ressource bleibt aktiv; eine manuelle Resource-URL ist nicht nötig.

Ab v0.7.2 berücksichtigen die Karten-Highlights auch Stationen mit unbekanntem
Öffnungsstatus. Explizit geschlossene Stationen bleiben ausgeschlossen; ein
unbekannter Status wird weiterhin nicht als „Geöffnet“ dargestellt.

Ab v0.7.3 werden Nakordoni-E10-Preise auch bei Einzelkraftstoff-Abfragen für
das günstigste Highlight normalisiert. Strukturierte und formatierte Adressen
werden übernommen, sofern der Provider sie liefert; fehlende Adressen bleiben
leer.

Die Beta `v0.8.0-beta.4` ergänzt einen pro Config Entry
persistierten Abrufmodus. Im Modus **Manuell** bleiben Cache und letzter
erfolgreicher Abruf sichtbar, während Zeitplan, GPS, Recovery und Reload keine
Providerabfrage auslösen. **Jetzt abrufen** ist ein admin-geschützter Service;
Benutzer ohne Adminrechte behalten lesenden Zugriff ohne Steuerung.
Der Button spricht genau den gewählten Config Entry an und respektiert
Provider-Cooldowns sowie Kontingente. Die Beta.2 behebt zusätzlich die
fehlerhafte Backend-Synchronisierung beim Umschalten und hält vorhandene
Stationsdaten bei Steuerungsfehlern sichtbar. Die Beta ist als GitHub-
Pre-Release-Kandidat vorbereitet;
produktive HA-/Browser- und vollständige Live-Provider-/OAuth-Tests bleiben
ausdrücklich außerhalb dieses Beta-Scope.

Der automatische Provider-Fallback ist auf DNS-/Netzwerkfehler, Timeouts,
HTTP 5xx und HTTP 429 begrenzt. Authentifizierungs-, Berechtigungs-, Kontingent-,
Payload- und Konfigurationsfehler werden nicht durch einen stillen Wechsel
verdeckt; Nakordoni benötigt nachgewiesene Marktberechtigung.

Die öffentliche HA-API garantiert allerdings keinen sofortigen Cache-Flush in
jedem Browser/Companion-Client. Bestehende v0.2.x-Installationen dürfen ihren
alten manuellen Resource-Eintrag nach erfolgreichem Update, Neustart und
Funktionstest über die Home-Assistant-Oberfläche entfernen. `.storage` darf
nicht manuell bearbeitet werden.
