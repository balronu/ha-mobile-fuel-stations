# Mobile Fuel Stations v0.8.1 — Stable

## Kompakte Lovelace-Karte / Compact Lovelace card

- Neue Karten werden standardmäßig kompakt angelegt.
- Bestehende YAML-Karten ohne display_mode bleiben aus Kompatibilitätsgründen ausführlich.
- Kompakte Tankstellenzeilen zeigen Logo, einzeiligen Namen mit Ellipsis, Adresse, Öffnungsstatus, Entfernung, mehrere Kraftstoffpreise und Navigation.
- „Nächste“ und „Günstigste“ werden inline markiert; doppelte Sonderkarten entfallen im Kompaktmodus.
- Provider, Kontingente, Cooldowns und weitere Diagnoseinformationen bleiben im aufklappbaren Diagnosebereich verfügbar.
- Automatischer/manueller Abruf, Providerlogik, Entity-IDs, Config Entries, Credentials und Backend-Abfragen wurden nicht verändert.

## Prüfung / Validation

- Frontend-Testabdeckung für 1, 5 und 10 Stationen, lange Namen, fehlende Daten, geschlossene Stationen, mehrere Kraftstoffe, Navigation, Modi und Diagnosezustände.
- TypeScript-Prüfung, Produktions-Build und synchronisiertes HA-Bundle.
- Keine Live-Provider-Abfragen, produktiven OAuth-Tests oder Änderungen an VM 104, Dashboards, Config Entries oder Backups.
