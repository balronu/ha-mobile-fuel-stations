# Mobile Fuel Stations – Deutsche Anleitung

Mobile Fuel Stations ist eine Home-Assistant-Custom-Integration für
Tankstellen in der Nähe. Sie liest gültige Koordinaten eines Fahrzeug- oder
Geräte-Trackers, fragt den Provider ab und stellt stabile Entities sowie eine
optionale responsive Lovelace-Karte bereit.

## Versionsstand

- **Stable:** `v0.5.1`, empfohlen für produktive Installationen.
- **Veröffentlichte Beta:** `v0.6.0-beta.5` mit Startup-GPS-Recovery und
  begrenzten Wiederholungen temporärer Providerfehler.
- **Entwicklungsziel:** `v0.6.0-beta.6`; noch nicht veröffentlicht.

Stable bleibt unverändert, Beta.5 bleibt als Rollback erhalten. Ein echter
produktiver HA-Neustarttest steht noch aus; ein sporadischer Browser-Ladefehler
wird daher nicht als behoben behauptet.

## Voraussetzungen und Installation

Installiere die Integration über **HACS → Integrationen**, suche nach **Mobile
Fuel Stations**, oder füge
`https://github.com/balronu/ha-mobile-fuel-stations` als benutzerdefiniertes
Integration-Repository hinzu. Für Produktion Stable, für kontrollierte Tests
Pre-Releases wählen. Danach Home Assistant neu starten und unter **Einstellungen
→ Geräte & Dienste → Integration hinzufügen** einrichten.

Benötigt wird eine Tracker-Entity mit gültigen `latitude` und `longitude`.
Jeder aktive Provider benötigt einen eigenen API-Key und ggf. Freigaben.

## Einrichtung und Kraftstoffe

Wählbar sind Standort-Entity, Radius 1–25 km, 1–10 Tankstellenplätze, E5, E10,
Diesel, LPG oder HVO100, Sortierung, Intervall, Bewegungsschwelle/Cooldown und
Provider. Mehrere Kraftstoffe bleiben eine Entity mit mehreren Preiszeilen;
Rankings erfolgen je Kraftstoff. E10 darf nur bei deklarierter Fähigkeit auf
E5 zurückfallen. Diesel, LPG und HVO100 werden nicht still ersetzt.

## Provider- und Länder-/Kraftstoff-Matrix

Dies ist die im Code deklarierte Fähigkeit, keine Garantie für jedes Konto oder
jede Station.

| Provider | Länder-/Preisabdeckung im Code | Kraftstoffe | Schlüssel und Limits |
| --- | --- | --- | --- |
| [Tankerkönig](https://onboarding.tankerkoenig.de/) | Deutschland (`DE`), je Station | Diesel, E5, E10 | API-Key; maximal 25 km; Providerbedingungen und Antwort-Limits gelten |
| [Petromap](https://developer.petromap.eu/) | `DE`/`AT` je Station; `BG`/`PL`/`SK` national; `ME`/`RS` ohne Preise | Diesel, E5, LPG | API-Key/Freigabe; Antwort kann Credits-, Rate- und Retry-Informationen enthalten |
| [Nakordoni](https://nakordoni.eu/de/developers/docs) | Konto-/Marktfreigabeabhängig; keine feste Allowlist behauptet | Diesel, E5, E10, LPG | Bearer-Key und ggf. Marktfreigabe; offizielle Explorer-Doku nennt derzeit 2 QPS und 1.000 Standardaufrufe/Tag, abhängig von Planänderungen |

HVO100 ist auswählbar, aber keine allgemeine HVO100-Preisabdeckung wird
behauptet. Provider-Limits ändern sich; Retry-After-/Rate-Limit-Metadaten werden
beachtet.

### API-Keys

Unter **Einstellungen → Geräte & Dienste → Mobile Fuel Stations → Konfigurieren
→ Zugangsdaten verwalten** nur den passenden Schlüssel eintragen. Der Status
unterscheidet fehlend, gespeichert/nicht geprüft, erfolgreich,
Authentifizierungsfehler, temporär nicht verfügbar und Freigabe ausstehend.
Optionen öffnen startet keine Anfrage; Schlüssel erscheinen nicht in Logs oder
Diagnostics.

## Startup-Recovery, Polling und Fehler

Nach dem Start läuft zunächst der normale erste Refresh. Bei fehlendem GPS plant
Beta.5 Prüfungen ungefähr nach 3, 10 und 30 Sekunden und danach etwa alle 60
Sekunden. GPS-Events können den nächsten Versuch vorziehen; Timer fangen
verpasste Events und reine Attributänderungen ab. Bei gültigen Koordinaten läuft
genau ein deduplizierter Provider-Refresh.

Das normale DataUpdateCoordinator-Polling bleibt aktiv (standardmäßig 15
Minuten), Bewegungs-Updates behalten Schwelle und Cooldown. Recovery, Bewegung
und Polling teilen einen deduplizierten Request-Pfad. Temporäre Netzwerk-,
Timeout- und Rate-Limit-Fehler nutzen begrenzten exponentiellen Backoff mit
Jitter und Retry-After. Permanente Auth-/Konfigurationsfehler stoppen
aggressive Wiederholungen. Gültige Daten bleiben bei temporären Fehlern
erhalten und werden als veraltet markiert. Beim Entladen werden Timer, Tasks und
Listener beendet.

## Lovelace-Karte und Markenlogos

```yaml
type: custom:mobile-fuel-stations-card
entity: sensor.mobile_fuel_stations_device_tracker_auto_nearby_stations
navigation: true
show_brand_logos: true
logo_path: /mobile_fuel_stations/logos/
```

Enthalten sind sechs lokale SVGs für Aral, Shell, JET, TotalEnergies, ORLEN und
OMV. Die Zuordnung normalisiert Groß-/Kleinschreibung, Akzente, Satzzeichen und
Leerzeichen. Beta.6 erkennt eine unterstützte Marke zusätzlich im Stationsnamen,
wenn `brand` fehlt oder ausführlich ist, z. B. `Aral Tankstelle` oder `Total
Energies`. Unbekannte Marken, leere Felder, fehlende Dateien und Ladefehler
zeigen das generische Zapfsäulensymbol.

Eigene SVGs gehören nach `/config/www/fuel-logos/` und werden als
`/local/fuel-logos/` referenziert. Nur sichere `/local/...`- und
`/hacsfiles/...`-Pfade sind erlaubt; externe URLs, Query-Strings, Backslashes
und Traversal werden abgelehnt. Quellen, Hashes und Rechtehinweise stehen in
[`BRAND_LOGOS.md`](BRAND_LOGOS.md); externe Logos werden nicht geladen.

## Diagnostics, Datenschutz und Fehlerbehebung

Diagnostics enthalten nur Refreshstatus, letzte erfolgreiche Aktualisierung,
Stale-/Fehlerklassifikation, GPS-/Recoverystatus und Retry-Termine. API-Keys,
Tokens und exakte Koordinaten fehlen absichtlich.

- **Keine Stationen nach Start:** Koordinaten, Provider-Land/Kraftstoff, Key und
  Freigabe prüfen.
- **Stale-Daten:** Fehlerklassifikation und Providerstatus prüfen; temporäre
  Fehler behalten die letzte erfolgreiche Antwort.
- **Kein Preis:** kein gültiger Preis für genau diesen Kraftstoff; kein stiller
  Ersatz außer dokumentiertem E10→E5.
- **Generisches Logo:** unbekannte Marke oder nicht ladbares Asset; statischen
  Logo-Pfad und Browser-Cache prüfen.
- **Nakordoni:** Marktfreigabe, Produktberechtigung, Quoten und Autorisierung
  sind externe Voraussetzungen.

Der ausgewählte Provider erhält Standort, Radius und Kraftstoffabfrage.
Providerbedingungen und Datenschutz beachten. Providerabdeckung, Preise,
Quoten, Freigaben und API-Verhalten können sich ändern. Ein produktiver
HA-Neustarttest wurde nicht durchgeführt.

## Links

- [Repository](https://github.com/balronu/ha-mobile-fuel-stations)
- [Issues](https://github.com/balronu/ha-mobile-fuel-stations/issues)
- [Releases](https://github.com/balronu/ha-mobile-fuel-stations/releases)
- [Changelog](CHANGELOG.md)
- [English guide](README.en.md)
