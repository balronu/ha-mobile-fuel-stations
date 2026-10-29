# Mobile Fuel Stations v0.8.6

## Deutsch

Stable-Veröffentlichung der in `v0.8.6-beta.1` praktisch geprüften
NaKordoni-v2-Diagnoseverbesserungen. Der produktive Endpunkt bleibt
`/api/v2/data/fuel-stations`; es gibt keine Migration auf v3 oder v4.

### Änderungen

- Coverage-Diagnose: `sparse_coverage`, `measured_at` und `fuel_type_note`
  werden fehlertolerant übernommen und bleiben von Preisbestätigungen getrennt.
- `markets_filtered` und `markets_notice` werden defensiv und getrennt von
  Kontoberechtigungen diagnostiziert.
- `currency_symbol`, `local_name`, `label`, `grades`, `freshest_age_hours`,
  Stations-`stale` und dokumentierte Anchor-Metadaten werden ergänzend an
  Home Assistant durchgereicht.
- Kanonische Kraftstoffcodes, `station_ref`, Preis-/Währungslogik, Fallbacks,
  Config Entries, Entity IDs und Lovelace-Konfigurationen bleiben kompatibel.

### Kompatibilität und Grenzen

- Optionale fehlende Felder blockieren ältere v2-Antworten nicht.
- `fuel_type_note` ersetzt keine `empty_reason`-Werte.
- Coverage ist keine dauerhafte Länderfreigabe; `measured_at` ist kein
  Preiszeitpunkt.
- Keine zusätzlichen Live-API-Aufrufe oder Änderungen an Home Assistant VM 104.

## English

Stable release of the Nakordoni v2 diagnostic improvements practically tested
in `v0.8.6-beta.1`. The productive endpoint remains
`/api/v2/data/fuel-stations`; there is no v3 or v4 migration.

### Changes

- Coverage diagnostics tolerate `sparse_coverage`, `measured_at`, and
  `fuel_type_note`, keeping coverage measurement separate from price
  confirmation.
- `markets_filtered` and `markets_notice` are handled defensively and
  separately from account permissions.
- `currency_symbol`, `local_name`, `label`, `grades`, `freshest_age_hours`,
  station-level `stale`, and documented anchor metadata are exposed
  additively to Home Assistant.
- Canonical fuel codes, `station_ref`, price/currency logic, fallbacks, Config
  Entries, entity IDs, and Lovelace configuration remain compatible.

### Compatibility and limitations

- Missing optional fields do not reject older v2 responses.
- `fuel_type_note` does not replace `empty_reason` values.
- Coverage is not permanent country permission; `measured_at` is not a price
  timestamp.
- No additional live API calls or Home Assistant VM 104 changes were made.
