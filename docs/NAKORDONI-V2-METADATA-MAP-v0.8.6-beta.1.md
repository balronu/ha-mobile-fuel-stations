# NaKordoni-v2-Metadatenzuordnung

| Feld | Stand vor v0.8.6-beta.1 | Verwendung jetzt |
|---|---|---|
| `sparse_coverage`, `measured_at`, `fuel_type_note` | Provider-Antwort, nicht durchgereicht | Diagnoseattribute; dynamisch und optional |
| `markets_filtered`, `markets_notice` | Nicht verarbeitet | Diagnose; getrennt von Berechtigungen |
| `currency_symbol`, `local_name`, `label` | Nicht im gemeinsamen Stationsmodell | Additive stationsbezogene Attribute |
| `grades`, `freshest_age_hours`, Stations-`stale` | Nicht vollständig verarbeitet | Additive Stations-/Preisdiagnose |
| `anchor` und Fuel-Metadaten | Nicht durchgereicht | Übersicht/Diagnose, ohne Identitätsänderung |
| `confirmed_at`, `age_hours`, Preis-`stale`, `station_ref` | Bereits unterstützt | Unverändert beibehalten |

Kanonische Kraftstoffcodes, Preiswährungen, Empty-Reasons und Provider-Fallbacks
bleiben die maschinenlesbaren Verträge. Lokale Labels sind ergänzend. Coverage
ist keine dauerhafte Marktfreigabe; `measured_at` ist kein Preiszeitpunkt.
