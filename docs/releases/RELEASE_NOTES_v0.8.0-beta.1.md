# Mobile Fuel Stations v0.8.0-beta.1

## Deutsch

Diese Beta ergänzt einen pro Fahrzeug beziehungsweise Config Entry gespeicherten
Abrufmodus für Tankstellendaten:

- Umschaltung zwischen automatischem und manuellem Tankstellenabruf direkt in der Lovelace-Karte.
- Manueller Abruf über einen Button für den gewählten Config Entry.
- Keine automatischen Provider-Abfragen im manuellen Modus.
- Persistente Einstellungen pro Fahrzeug beziehungsweise Config Entry.
- Stationsdaten bleiben nach Neustart durch den persistenten, kontextgeprüften Cache erhalten.
- Anzeige des letzten erfolgreichen Abrufs.
- Schutz durch Cooldown, Kontingent und Berechtigungen.
- Rückwärtskompatibilität für bestehende Installationen; bestehende Einträge starten im Automatikmodus.

**Beta-Hinweis:** Es wurde kein produktiver Home-Assistant-/Browser-Praxistest und
kein vollständiger Live-Provider-/OAuth-Test durchgeführt.

## English

This beta adds a persisted station-fetch mode per vehicle or Config Entry:

- Switch between automatic and manual station fetching directly in the Lovelace card.
- Fetch manually with a button for the selected Config Entry.
- No automatic provider requests in manual mode.
- Persistent settings per vehicle or Config Entry.
- Station data survives restarts through the persistent, context-checked cache.
- Display of the last successful fetch.
- Cooldown, quota, and permission protection.
- Backward compatibility for existing installations; existing entries start in automatic mode.

**Beta note:** No productive Home Assistant/browser practice test and no complete
live provider/OAuth test were performed.
