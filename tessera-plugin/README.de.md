# Mobile Fuel Stations für Tessera (Beta)

Dieses **Beta-Plugin** zeigt die nächste und günstigste Tankstelle aus der vorhandenen Home-Assistant-Integration [Mobile Fuel Stations](https://github.com/balronu/ha-mobile-fuel-stations).

**Voraussetzungen:** Tessera-Entwicklerversion mit Plugin-API 0.24 und die Integration Mobile Fuel Stations in Home Assistant.

## Architektur

Das Plugin liest die Stations-, Kraftstoff- und Aktualitätsattribute des Übersichtssensors von Mobile Fuel Stations. Es ruft Tankerkönig, Petromap oder Nakordoni **nicht direkt** auf und greift niemals auf Provider-Zugangsdaten zu. API-Kontingente und GPS-Aktualisierungen bleiben vollständig unter der Kontrolle von Home Assistant.

Die Kachel passt sich an Größen von 1×1 bis 4×4 an. Ein Tippen auf jede unterstützte Größe öffnet die offizielle Tessera-Detailkarte mit nächster und günstigster Tankstelle, Adresse, Öffnungsstatus, Kraftstoffauswahl und Datenaktualität. Die Kraftstoffauswahl bleibt lokal auf dem Display und ändert weder die Home-Assistant-Konfiguration noch löst sie eine weitere Anfrage aus.

## Einrichtung

Installiere diese lesende Beta ohne zusätzlichen Template-Sensor in Home Assistant.

1. Öffne in Tessera die Seite **Plugins** und wähle **Mit Link hinzufügen**.
2. Verwende die Plugin-Ordner-URL: `https://github.com/balronu/ha-mobile-fuel-stations/tree/main/tessera-plugin`.
3. Wenn Tessera **Branch testen** anbietet, trage `feature/tessera-display-plugin-prototype` in das Branch-Feld ein. Der Ordner ist bereits in der URL enthalten; der Branchname mit Schrägstrich gehört nicht in den URL-Pfad.
4. Prüfe die Plugin-Details und füge es nur einem Testdisplay hinzu. Der Build eines Tessera-Plugins kompiliert die Display-Firmware neu.
5. Füge die Kachel **Nächste und günstigste Tankstelle** hinzu und wähle den Übersichtssensor von Mobile Fuel Stations.

Das Plugin benötigt einen Tessera-Build mit Plugin-API **0.24**. Wenn die installierte Tessera-Version diese API nicht unterstützt, darf die Installation nicht erzwungen werden.

## Bekannte Einschränkungen

- Der Entity-Picker zeigt grundsätzlich Sensoren an; ausgewählt werden muss der Übersichtssensor von Mobile Fuel Stations.
- Das Plugin verwendet vorhandene Daten und führt keine manuellen Provider-Abfragen, Navigation oder Preisübermittlung aus.
- Die Beta ist ein Entwicklungsstand und kein veröffentlichtes GitHub-Release oder offizieller Tessera-Katalogeintrag.
- Der strikte Guition-Preview deckt Offline-Daten ab; reale Displaygrößen, Gerätesprache und produktive HA-Daten müssen separat auf Hardware geprüft werden.
