# Stable-Readiness-Bewertung für v0.8.0

## Ergebnis

**NO-GO für Stable auf Basis von Beta.5.** Beta.5 ist ein Review-Kandidat; die Bewertung ist noch keine Freigabe für Merge, Tag oder Stable-Release.

## Abgedeckte technische Bereiche

- Rückwärtskompatible Provider-/Abrufmodi und getrennte Config Entries
- Persistierter Stationscache und Zeitstempel des letzten erfolgreichen Abrufs
- Startup-Verhalten für frischen, veralteten und fehlenden Cache
- Manuelle und automatische Abrufe ohne automatische Provideranfrage im manuellen Modus
- Provider-Fallback, Cooldowns, Retry-After und Cache-Erhalt
- Providerbezogene Status- und Kontingentdarstellung ohne Schätzwerte oder Secrets
- Lovelace-Countdown ohne zusätzliche API-Aufrufe

## Offene Freigaberisiken

- Kein produktiver HA-VM-104-Test und keine Live-Provider-/OAuth-Abfrage.
- Die konkrete ursprüngliche Tankerkönig-Störung ist weiterhin nicht durch produktive Logs bestätigt.
- Stable benötigt zusätzlich einen erfolgreichen Beta.5-PR mit Main-/Tag-CI und eine gezielte HA-Praxisprüfung nach separater Freigabe.
