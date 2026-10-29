# Mobile Fuel Stations v0.8.6-beta.1

## Deutsch

Diese Beta ergänzt ausschließlich die bestehende NaKordoni-v2-Verarbeitung. Der
produktive Endpunkt bleibt `/api/v2/data/fuel-stations`; es gibt keine Migration
auf v3 oder v4 und keine zusätzlichen API-Aufrufe.

### Änderungen

- Coverage-Diagnose: `sparse_coverage`, `measured_at` und `fuel_type_note` werden
  fehlertolerant übernommen. `measured_at` bleibt vom Preiszeitpunkt getrennt.
- Marktfilter: `markets_filtered` und `markets_notice` werden separat von
  Kontoberechtigungen und dynamischer Datenabdeckung diagnostiziert.
- Stationsdaten: `currency_symbol`, `local_name`, `label`, `grades`,
  `freshest_age_hours`, Stations-`stale` und die dokumentierten Anchor-
  Kraftstoff-/Standortmetadaten werden ergänzend verfügbar gemacht.
- Bestehende kanonische Kraftstoffcodes, Preis-Währungslogik, `station_ref`,
  Fallbacks, Config Entries, Entity IDs und Lovelace-Konfigurationen bleiben
  erhalten. Die Lovelace-Oberfläche bleibt unverändert; technische Details
  werden in Diagnoseattributen bereitgestellt.

### Kompatibilität und Grenzen

- Fehlende oder unbekannte optionale Felder bleiben unbekannt und blockieren
  keine ältere v2-Antwort.
- `fuel_type_note` ersetzt keine maschinenlesbaren `empty_reason`-Werte.
- Coverage-Messzeitpunkte sind keine Preisbestätigungen und keine dauerhafte
  Länderfreigabe.
- Diese Beta enthält ausschließlich Fixture-/Mock-basierte Prüfungen; keine
  Live-Abfrage und keine Änderung an Home Assistant VM 104.

## English

This beta only extends the existing NaKordoni v2 processing. The productive
endpoint remains `/api/v2/data/fuel-stations`; there is no v3 or v4 migration
and no additional API request.

### Changes

- Coverage diagnostics now tolerate and expose `sparse_coverage`, `measured_at`,
  and `fuel_type_note`, while keeping coverage measurement separate from price
  confirmation.
- `markets_filtered` and `markets_notice` are reported separately from account
  permissions and dynamic data coverage.
- Additive station metadata includes `currency_symbol`, `local_name`, `label`,
  `grades`, `freshest_age_hours`, station-level `stale`, and documented anchor
  fuel/location fields.
- Canonical fuel codes, currency-safe price logic, `station_ref`, fallbacks,
  Config Entries, entity IDs, and Lovelace configuration remain unchanged.
  The Lovelace surface is unchanged; technical details are diagnostic data.

### Compatibility and limitations

- Missing or unknown optional fields remain unknown and do not reject older v2
  responses.
- `fuel_type_note` does not replace machine-readable `empty_reason` values.
- Coverage measurement timestamps are not price confirmations or permanent
  country permissions.
- This beta uses fixtures/mocks only; no live API call or Home Assistant VM 104
  change was performed.
