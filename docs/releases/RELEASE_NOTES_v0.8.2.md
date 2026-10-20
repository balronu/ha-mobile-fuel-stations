# Mobile Fuel Stations v0.8.2 — Compact station rows

## Änderung

v0.8.2 korrigiert die kompakte Lovelace-Karte für die vollständige normale Tankstellenliste. Jede Zeile verwendet jetzt ein eigenes dichtes Layout mit Markenlogo, einzeiligem Namen mit Ellipsis, Adresse, Öffnungsstatus, Entfernung, Kraftstoffpreisen und Navigation. Nächste und günstigste Tankstellen werden nur inline markiert; sie erscheinen nicht doppelt als Sonderkarten.

Die ausführliche Darstellung bleibt für bestehende YAML-Karten ohne `display_mode` erhalten. Neue Karten bleiben standardmäßig kompakt. Backend, Entity-IDs, Config Entries, Zugangsdaten und Providerabfragen wurden nicht geändert.

## Prüfung

- Frontend-Regressionstests für fünf kompakte Zeilen, fehlende/mehrere Preise, lange Namen, Status, Entfernung, Navigation, Tastaturbedienung und keine zusätzlichen Serviceaufrufe.
- Chromium-Prüfung bei ungefähr 390 CSS-Pixeln mit fünf normalen Tankstellen; die tatsächlichen Kartenhöhen werden im Release-Abschlussbericht dokumentiert.
- TypeScript, Produktions-Bundle, Python-/Hassfest- und CI-Prüfungen.
- Keine Live-Providerabfragen, produktiven OAuth-Tests oder Änderungen an Home Assistant, Dashboards, Config Entries, Backups oder VM 104.
