# Nakordoni API-Kompatibilitätsaudit – v0.8.5-beta.1

## Grundlage und Einschränkung

Die Integration verwendet `GET https://nakordoni.eu/api/v2/data/fuel-stations`.
Der öffentlich erreichbare Endpunkt antwortete während des Audits ohne
Anmeldedaten mit HTTP 401. Deshalb wurden keine Live-Datenabfragen mit
Credentials durchgeführt; die Prüfung nutzt den bereitgestellten API-Vertrag
und gemockte Antworten.

## Abweichungen

| Bereich | Ergebnis | Umsetzung/Risiko |
| --- | --- | --- |
| Request, Bearer-Auth, Einmalabfrage | korrekt | unverändert |
| `id`/`station_ref` und Deduplizierung | korrekt | `station_ref` bleibt primäre stabile Identität |
| Kraftstoffmapping | Anpassung erforderlich | alle dokumentierten v2-Schlüssel ergänzt; `hvo100` bleibt bewusst eine getrennte alte Auswahl |
| Preisfrische | Anpassung erforderlich | `confirmed_at`, `age_hours`, `stale`, 7-Tage-Grenze; `updated_at` allein ist nicht ausreichend |
| 90-Tage-Auslassung/Cache | Anpassung erforderlich | bekannte alte Nakordoni-Preise werden nach 90 Tagen gelöscht |
| Empty-Reasons und Hinweise | Anpassung erforderlich | lokalisierte UI-Meldungen, `suggestion`, Entfernungen und Notices ohne Radiusvergrößerung |
| Währungen | Anpassung erforderlich | explizite Währungen werden nicht gemeinsam sortiert oder hervorgehoben |
| Radius/Limit | Anpassung erforderlich | Nakordoni begrenzt auf 25 km/20; andere Provider bleiben unverändert |
| dynamische Coverage | Anpassung erforderlich | `station_countries`/`station_counts` werden als Messwerte diagnostiziert |
| Fallback-Priorität | korrekt | keine Änderung |
| Lovelace-Modi | korrekt/erweitert | Empty-Hinweis erscheint nur bei leerem Ergebnis; vorhandene Zeilen, Logos, Abstände und Divider bleiben unverändert |

## Rückwärtskompatibilität

Bestehende Provider ohne `confirmed_at`, `age_hours`, `stale` oder explizite
Währung bleiben unverändert. Bestehende Kraftstoffauswahlen werden nicht
umbenannt oder automatisch auf einen anderen Kraftstoff abgebildet.

