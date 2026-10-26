# Mobile Fuel Stations v0.8.5-beta.1

## Deutsch

### Zusammenfassung

Diese Beta erweitert den Nakordoni-v2-Provider um den dokumentierten
Kraftstoff- und Antwortvertrag und macht Preisfrische, leere Ergebnisse,
Währungen und API-Grenzen sichtbar und sicher.

### Änderungen

- Unterstützung für `diesel`, `e5`, `e10`, `superplus`, `super100`, `premdiesel`,
  `truckdiesel`, `hvo`, `lpg`, `cng`, `adblue`, `e85` und `lng`.
- Preisalter basiert auf `confirmed_at`, `age_hours` und `stale`; `updated_at`
  wird nicht allein zur Frischebewertung verwendet.
- Preise ohne frische Bestätigung werden nicht als günstigster Preis gewählt;
  bekannte Nakordoni-Cachepreise über 90 Tage werden nicht fortgeführt.
- Preise mit unterschiedlichen expliziten Währungen werden nicht verglichen.
- Empty-Reasons, Hinweise, Suchentfernungen, Notices und dynamische Coverage
  erscheinen als Diagnose; der Radius wird nicht automatisch vergrößert.
- Nakordoni begrenzt Requests auf 25 km und maximal 20 Stationen. Andere
  Provider und ihre Grenzen bleiben unverändert.

### Installation und Einschränkungen

Bestehende Config Entries und Karten bleiben kompatibel. Diese Beta führt keine
produktiven Home-Assistant- oder OAuth-Aufrufe aus; die tatsächliche
Stationsabdeckung hängt von API-Zugang und dynamischer Provider-Coverage ab.

Vollständige technische Details: [Nakordoni API audit](../NAKORDONI-API-AUDIT-v0.8.5-beta.1.md).

## English

### Summary

This beta extends the Nakordoni v2 provider contract and makes freshness,
empty results, currencies, and API limits safe and visible.

### Changes

- Supports the documented fuel keys listed above.
- Freshness uses `confirmed_at`, `age_hours`, and `stale`; `updated_at` alone
  is never treated as proof of a fresh price.
- Stale prices are excluded from cheapest highlights, and known Nakordoni cache
  prices older than 90 days are not continued.
- Explicitly different currencies are never compared numerically.
- Empty reasons, suggestions, search distances, notices, and measured coverage
  are exposed as diagnostics without automatic radius expansion.
- Nakordoni requests are capped at 25 km and 20 stations; other providers keep
  their existing limits.

### Installation and limitations

Existing Config Entries and cards remain compatible. The beta performs no
productive Home Assistant or OAuth calls; coverage depends on API access and
dynamic provider coverage.

Full technical details: [Nakordoni API audit](../NAKORDONI-API-AUDIT-v0.8.5-beta.1.md).
