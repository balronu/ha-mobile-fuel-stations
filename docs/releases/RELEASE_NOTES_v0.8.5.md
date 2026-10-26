# Mobile Fuel Stations v0.8.5

## Deutsch

### Zusammenfassung

v0.8.5 übernimmt die in v0.8.5-beta.1 getestete Nakordoni-v2-Kompatibilität
als Stable. Die bestehenden Home-Assistant-Konfigurationen und Karten bleiben
kompatibel.

### Änderungen und Fehlerbehebungen

- Dokumentierte Nakordoni-v2-Kraftstofftypen einschließlich `diesel`, `e5`,
  `e10`, `superplus`, `super100`, `premdiesel`, `truckdiesel`, `hvo`, `lpg`,
  `cng`, `adblue`, `e85` und `lng`.
- Stabilere Stationsidentifikation über `id` beziehungsweise `station_ref`,
  einschließlich Duplikatvermeidung über mehrere Kraftstoffarten.
- Preisfrische verwendet `confirmed_at`, `age_hours` und `stale`; `updated_at`
  allein gilt nicht als Frischenachweis. Veraltete Preise werden nicht als
  aktueller Bestpreis hervorgehoben, und Nakordoni-Cachepreise über 90 Tage
  werden nicht künstlich fortgeführt.
- Preise mit unterschiedlichen Währungen werden nicht ungeprüft miteinander
  verglichen. Entfernungssortierung bleibt unabhängig davon verfügbar.
- Leere HTTP-200-Ergebnisse werden mit verständlichen Empty-Reasons,
  Vorschlägen, Entfernungen, Länderabdeckung und Provider-Hinweisen erklärt;
  der Suchradius wird nicht automatisch vergrößert.
- Nakordoni-spezifische Grenzen von 25 km und 20 Stationen werden transparent
  angewendet, ohne die Limits anderer Provider zu verändern.
- Die Kartenmodi Ausführlich, Kompakt und Individuell sowie bestehende
  Sortierung, Highlights, Layouts, Logos, Abstände und Trennlinien bleiben
  erhalten. Die doppelte Trennlinie im Kopfbereich ist behoben.

### Kompatibilität und Update

Bestehende Config Entries, gespeicherte Kraftstoffauswahlen und YAML-Karten
bleiben erhalten. Nach einem HACS-Update kann je nach Home-Assistant-Frontend
oder Companion-App ein einmaliges Dashboard-Neuladen erforderlich sein. Es
sind keine manuellen Änderungen an `.storage` erforderlich.

`v0.8.4` bleibt als vorherige Stable-Version für einen kontrollierten Rollback
verfügbar. Die tatsächliche Nakordoni-Abdeckung hängt von API-Zugang und der
dynamischen Provider-Coverage ab.

Vollständige technische Details: [Nakordoni API audit](../NAKORDONI-API-AUDIT-v0.8.5-beta.1.md).

## English

### Summary

v0.8.5 promotes the Nakordoni v2 compatibility tested in v0.8.5-beta.1 to
Stable. Existing Home Assistant configurations and cards remain compatible.

### Changes and fixes

- Supports the documented Nakordoni v2 fuel types, including `diesel`, `e5`,
  `e10`, `superplus`, `super100`, `premdiesel`, `truckdiesel`, `hvo`, `lpg`,
  `cng`, `adblue`, `e85`, and `lng`.
- Uses `id` or `station_ref` for stable station identity and avoids duplicates
  when a station offers multiple fuels.
- Price freshness uses `confirmed_at`, `age_hours`, and `stale`; `updated_at`
  alone is not treated as freshness proof. Stale prices are excluded from
  current cheapest highlights, and Nakordoni cached prices older than 90 days
  are not artificially continued.
- Explicitly different currencies are never compared numerically; distance
  sorting remains available independently.
- Empty HTTP-200 results expose understandable empty reasons, suggestions,
  distances, country coverage, and provider notices without automatic radius
  expansion.
- Nakordoni-specific limits of 25 km and 20 stations are applied
  transparently without changing other providers' limits.
- Detailed, Compact, and Individual card modes retain existing sorting,
  highlights, layouts, logos, spacing, and dividers. The duplicate header
  divider is fixed.

### Compatibility and update

Existing Config Entries, saved fuel selections, and YAML cards are preserved.
After a HACS update, a one-time dashboard reload may be needed depending on
the Home Assistant frontend or companion app. No manual `.storage` changes are
required.

`v0.8.4` remains available as the previous Stable version for a controlled
rollback. Actual Nakordoni coverage depends on API access and dynamic provider
coverage.

Full technical details: [Nakordoni API audit](../NAKORDONI-API-AUDIT-v0.8.5-beta.1.md).
