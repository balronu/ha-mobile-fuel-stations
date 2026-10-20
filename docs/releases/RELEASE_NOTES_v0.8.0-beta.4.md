# Mobile Fuel Stations v0.8.0-beta.4

## Provider-Fallback und Fehlerbehandlung

- Der automatische Wechsel von Tankerkönig zu einem weiteren **konfigurierten und berechtigten** Provider ist jetzt auf transiente Fehler begrenzt: DNS-/Netzwerkfehler, Timeouts, HTTP 5xx und HTTP 429.
- API-Key-/Authentifizierungsfehler, fehlende Berechtigungen, Kontingentfehler, ungültige Payloads und Konfigurationsfehler werden nicht durch einen stillen Providerwechsel verdeckt.
- Provider-Cooldowns werden vor jedem Fallback-Kandidaten geprüft; dadurch entstehen keine unnötigen Abrufe.
- Persistierte Nakordoni-Marktmetadaten werden nach einem HA-Neustart wieder in die automatische Provider-Auswahl geladen.
- Die Integration veröffentlicht Fallback-Versuch, Ergebnis und Überspringgründe ausschließlich geheimnisfrei in Diagnose- und Entity-Attributen.
- Die Lovelace-Karte kann einen erfolgreichen Ersatzanbieter und fehlende Marktberechtigung verständlich anzeigen; Stationsdaten und der Beta.3-Cooldown-Countdown bleiben erhalten.

## Grenzen

- Die konkrete Ursache des ursprünglichen Wohnmobil-Fehlers bleibt ohne produktive, redigierte HA-Logs und ohne Live-Providerzugriff unbestätigt.
- Nakordoni wird weiterhin nicht allein aufgrund eines API-Keys als für einen Markt berechtigt angenommen.
- Kein Live-Provider-/OAuth-Aufruf, keine Änderung an HA VM 104, Config Entries oder Backups.
- `v0.7.3` bleibt Stable; Beta.4 ist nur als unveröffentlichter Entwicklungsstand vorbereitet.
