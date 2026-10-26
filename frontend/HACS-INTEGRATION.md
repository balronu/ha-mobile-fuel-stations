# HACS-Auslieferung der Lovelace-Karte

- HACS bleibt ein einziges Repository mit der Kategorie `integration`.
- Das kanonische Frontend liegt unter `frontend/src/`.
- `npm run build` erzeugt `frontend/dist/mobile-fuel-stations-card.js` und kopiert
  exakt dieses Artefakt nach
  `custom_components/mobile_fuel_stations/frontend/mobile-fuel-stations-card.js`.
- Home Assistant registriert beim Integrations-Setup den statischen Pfad
  `/mobile_fuel_stations` über `async_register_static_paths`.
- Die automatisch registrierte JavaScript-URL enthält die Integrationsversion,
  zum Beispiel `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.8.5`.
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

Die Stable-Version `v0.8.3` priorisiert die vollständige Tankstellenliste in beiden Ansichten; die
lokale Ländererkennung aus `v0.8.0` bleibt enthalten. Bei später
eintreffenden GPS-Positionen im manuellen Modus, ohne Provider- oder
Usage-Abfragen auszulösen. Die v0.8.0-Erweiterungen umfassen außerdem einen pro
Config Entry
persistierten Abrufmodus. Im Modus **Manuell** bleiben Cache und letzter
erfolgreicher Abruf sichtbar, während Zeitplan, GPS, Recovery und Reload keine
Providerabfrage auslösen. **Jetzt abrufen** ist ein admin-geschützter Service;
Benutzer ohne Adminrechte behalten lesenden Zugriff ohne Steuerung.
Der Button spricht genau den gewählten Config Entry an und respektiert
Provider-Cooldowns sowie belastbare Kontingentdaten. Ein frischer automatischer
Cache löst beim Start keinen vorzeitigen Providerabruf aus; ein manueller Start
bleibt providerfrei. Die historische Beta.2 behebt zusätzlich die
fehlerhafte Backend-Synchronisierung beim Umschalten und hält vorhandene
Stationsdaten bei Steuerungsfehlern sichtbar. Die Stable-Prüfung verwendet
Tests und CI mit Mocks und Fixtures; Live-Provider-/OAuth-Tests wurden nicht
ausgeführt.

Der automatische Provider-Fallback ist auf DNS-/Netzwerkfehler, Timeouts,
HTTP 5xx und HTTP 429 begrenzt. Authentifizierungs-, Berechtigungs-, Kontingent-,
Payload- und Konfigurationsfehler werden nicht durch einen stillen Wechsel
verdeckt; Nakordoni benötigt nachgewiesene Marktberechtigung.

Die Beta `v0.8.4-beta.5` ergänzt Ausführlich, Kompakt und Individuell sowie
kartenspezifische Sortierung und Anzeigeoptionen. Die Integrationseinstellungen
bleiben als Legacy-Fallback erhalten. Ein bereits ausgeführtes JavaScript-Modul
kann im offenen Browser-Tab nicht sicher ersetzt werden; der neue Resource-Key
verhindert jedoch das Wiederverwenden derselben alten Bundle-URL. Je nach
Home-Assistant-Frontend oder Companion-App kann ein einmaliges Dashboard-
Neuladen erforderlich bleiben; ein automatischer Hard-Reload wird nicht
versprochen.

Die öffentliche HA-API garantiert allerdings keinen sofortigen Cache-Flush in
jedem Browser/Companion-Client. Bestehende v0.2.x-Installationen dürfen ihren
alten manuellen Resource-Eintrag nach erfolgreichem Update, Neustart und
Funktionstest über die Home-Assistant-Oberfläche entfernen. `.storage` darf
nicht manuell bearbeitet werden.
