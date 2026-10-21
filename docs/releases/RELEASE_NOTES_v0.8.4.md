# Mobile Fuel Stations v0.8.4 — Stable Release

## Deutsch

`v0.8.4` ist die stabile Veröffentlichung des vollständigen v0.8.4-Zyklus.

- Drei Lovelace-Darstellungen: **Ausführlich**, **Kompakt** und
  **Individuell**.
- Kartenbezogene Sortierung, Kraftstoff für die Preissortierung und sichtbare
  Tankstellenanzahl.
- Konfigurierbare Kopf- und Stationsfelder, Dichte und Trennlinien sowie das
  optionale Layout **Highlights + Liste**.
- Bestehende YAML-Karten, Config Entries, Provider-Abrufe und
  Aktualisierungslogik bleiben kompatibel.
- Leere Kopfbereich-Wrapper werden vermieden; zwischen zwei sichtbaren
  Kopfbereich-Sektionen erscheint maximal eine Trennlinie.
- Der Frontend-Cache-Key ist auf `v=0.8.4` gesetzt.

Die Release-Prüfungen umfassen Python, Frontend, Build, Metadaten, JSON,
Compileall und einen Chromium-Test mit berechneten CSS-Rahmen und Abständen.
Es wurde keine produktive Home-Assistant-Installation, VM 104, kein Dashboard,
Config Entry, Provider, OAuth-Zugang oder Backup verändert.

## English

`v0.8.4` is the stable release of the complete v0.8.4 cycle.

- Three Lovelace display modes: **Detailed**, **Compact**, and **Individual**.
- Per-card sorting, fuel selection for price sorting, and visible station count.
- Configurable header and station fields, density, dividers, and the optional
  **Highlights + list** layout.
- Existing YAML cards, Config Entries, provider fetching, and update behavior
  remain compatible.
- Empty header controls wrappers are avoided; at most one divider appears
  between two visible header sections.
- The frontend cache key is `v=0.8.4`.

Release checks cover Python, frontend, build, metadata, JSON, compileall, and a
Chromium regression check using computed CSS borders and spacing. No productive
Home Assistant installation, VM 104, dashboard, Config Entry, provider,
OAuth credential, or backup was changed.
