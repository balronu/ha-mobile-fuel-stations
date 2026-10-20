# Mobile Fuel Stations v0.8.0-beta.2

## Deutsch

### Praxis-Hotfix

- Der Service `mobile_fuel_stations.set_fetch_mode` verwendet jetzt den
  tatsächlichen Home-Assistant-Servicekontext. Umschalten zwischen
  **Automatisch** und **Manuell** wird dadurch korrekt persistiert und löst
  keinen `name 'hass' is not defined`-Fehler mehr aus.
- Die Lovelace-Karte zeigt während einer Änderung weiterhin den bestätigten
  Backend-Modus. Bei einem Fehler wird die Auswahl nicht optimistisch geändert
  und auf dem bestätigten Zustand belassen.
- Fehler beim Umschalten oder beim manuellen Abruf werden kompakt innerhalb
  der Karte angezeigt; vorhandene Tankstellendaten bleiben sichtbar.
- Nach einer erfolgreichen Aktion wird der lokale Steuerungsfehler entfernt.
  Mehrere Karten desselben Config Entries beziehen ihren Modus weiterhin aus
  dem gemeinsamen HA-Entity-Zustand.
- Ein erfolgreicher manueller Abruf wird nicht allein wegen des manuellen
  Modus als veraltet markiert. Das Alter des letzten erfolgreichen API-Abrufs
  bleibt vom providerseitigen Preisalter getrennt.

### Qualitätssicherung

- 356 Python-Tests bestanden.
- 51 Frontend-Tests bestanden.
- TypeScript-Prüfung, Produktions-Build und Bundle-Kopie bestanden.
- Hassfest-/Validate- und Secret-Scan-Läufe sind für den PR auszuführen.
- Keine Live-Provider- oder OAuth-Aufrufe, keine produktive HA-Änderung und
  keine Änderung an Stable `v0.7.3`.

## English

### Practice-test hotfix

- `mobile_fuel_stations.set_fetch_mode` now uses the actual Home Assistant
  service context, so automatic/manual mode changes persist without the
  `name 'hass' is not defined` error.
- The Lovelace card keeps showing the confirmed backend mode while a change is
  pending. Failed changes do not optimistically switch the selection.
- Mode and manual-refresh errors are shown inside the card while existing
  station data remains visible.
- A successful action clears the local control error. Multiple cards for one
  Config Entry continue to follow the shared HA entity state.
- A successful manual fetch is not marked stale solely because manual mode is
  active; API-result age remains separate from provider price age.

### Validation

- 356 Python tests passed.
- 51 frontend tests passed.
- TypeScript check, production build, and bundle copy passed.
- Hassfest/Validate and secret scanning are required PR gates.
- No live provider/OAuth calls, productive Home Assistant changes, or Stable
  `v0.7.3` changes are included.
