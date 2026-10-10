# Mobile Fuel Stations

Mobile Fuel Stations ist eine Home-Assistant-Custom-Integration für nahe
gelegene Tankstellen anhand einer Fahrzeug- oder Geräte-Entity mit
`latitude`/`longitude`. Die Integration ist für Autos, Wohnmobile und andere
bewegliche Objekte geeignet.

## Versionen

| Kanal | Version | Zweck |
| --- | --- | --- |
| Stable | `v0.4.0` | Empfohlene Version für produktive Installationen |
| Pre-Release | `v0.5.0-beta.11` | Aktueller Beta-Stand mit getrenntem Credential-Manager und API-Status |

Beta-Versionen können sich ändern. Für produktive Systeme ist Stable die
sicherere Wahl.

## Funktionen

- E5, E10, Diesel, LPG/Autogas und HVO100 gleichzeitig auswählbar
- Eine Tankstellenkarte pro Station mit allen verfügbaren ausgewählten Preisen
- Fachlich getrennte Preisbewertung je Kraftstoffart; unterschiedliche
  Kraftstoffe werden niemals in einer Rangliste vermischt
- Nächste Tankstelle nach Entfernung und günstigste Tankstelle je Kraftstoff
- Zusammengeführte Highlight-Karten, wenn dieselbe Station sicher anhand ihrer
  stabilen Stations-ID identifiziert wird
- Sortierung nach Entfernung oder nach dem Preis einer ausdrücklich gewählten
  Kraftstoffart
- Kompakte responsive Dashboard-Karte für Smartphones, Tablets und Desktop
- Öffnungsstatus, Preisalter, fehlende Preise, E10/E5-Ersatzhinweise und
  Navigation zu einer Station
- Stabile Stations-Entities und konfigurierbare Anzahl von 1 bis 10 Slots
- Bewegungsupdates mit Schwelle und Cooldown
- Lokales Home-Assistant-Branding unter
  `custom_components/mobile_fuel_stations/brand/`
- Allgemeine Optionen werden unabhängig von der Zugangsdatenverwaltung gespeichert

## Datenanbieter und Abdeckung

Die Anbieter werden über offizielle Home-Assistant-Checkboxen ausgewählt. Ein
Anbieter wird direkt verwendet. Sind mindestens zwei Anbieter aktiviert, nutzt
die automatische Auswahl ausschließlich diese aktivierten und konfigurierten
Anbieter; deaktivierte oder nicht authentifizierte Anbieter werden nicht als
stiller Fallback verwendet.

| Anbieter | Schlüssel | Aktuelle Implementierungsabdeckung |
| --- | --- | --- |
| [Tankerkönig](https://creativecommons.tankerkoenig.de/) | Ja | Deutschland; Diesel, E5 und E10; API-Radius maximal 25 km |
| [Petromap v2](https://developer.petromap.eu/) | Ja | DE/AT mit Stationspreisen für Diesel, E5 und LPG; weitere Länder sind abhängig von der verifizierten Petromap-Abdeckung |
| [Nakordoni](https://nakordoni.dev/) | Ja | Implementiert für Diesel, E5, E10 und LPG; Marktfreigabe und Live-API-Zugang sind noch ausstehend |

HVO100 ist eine echte, auswählbare Kraftstoffart. Ob dafür Preise erscheinen,
hängt von einer tatsächlich verifizierten Provider- und Länder-Capability ab;
HVO100 wird nicht pauschal als grundsätzlich unmöglich dokumentiert und nie
still als Diesel ausgegeben.

### API-Schlüssel

Jeder verwendete Anbieter benötigt seinen eigenen Schlüssel. Die offiziellen
Bezugsquellen sind oben verlinkt. Schlüssel werden im Einrichtungs- oder
Options-Flow eingetragen und niemals vollständig in der Oberfläche, in Logs,
Diagnosen oder Git-Dateien angezeigt.

Im Options-Flow wird pro Anbieter ein nicht-sensibler Status angezeigt:

- Kein API-Schlüssel hinterlegt
- API-Schlüssel hinterlegt – noch nicht geprüft
- Zugang erfolgreich geprüft
- Authentifizierung fehlgeschlagen
- Zugang derzeit nicht prüfbar
- API-Freigabe ausstehend
- Nicht ausgewählt

„API-Schlüssel hinterlegt“ bedeutet ausdrücklich nicht „Zugang erfolgreich
geprüft“. Ein erfolgreicher Runtime-Provideraufruf setzt den Prüfstatus; beim
bloßen Öffnen des Options-Flows werden keine Netzwerkanfragen gestartet.

Die allgemeinen Einstellungen werden direkt gespeichert. Über **Zugangsdaten
verwalten** kann anschließend der separate Credential-Manager geöffnet werden.
Ein leeres Eingabefeld lässt einen vorhandenen Schlüssel unverändert; Ersetzen
erfolgt durch Eingabe eines neuen Werts, Entfernen nur über die ausdrückliche
Entfernen-Option. Status wird nach Schlüsseländerungen invalidiert. Die
gespeicherten Schlüssel werden bei einer Aktualisierung nicht neu erfunden oder
ungefragt überschrieben.

## Installation über HACS

1. **HACS → Integrationen** öffnen.
2. Nach **Mobile Fuel Stations** suchen. Falls das Repository nicht gelistet
   ist, unter **Benutzerdefinierte Repositories**
   `https://github.com/balronu/ha-mobile-fuel-stations` als **Integration**
   hinzufügen.
3. Installieren und Home Assistant vollständig neu starten.
4. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** die
   Integration einrichten.

Die Dashboard-Karte wird automatisch registriert. Beta.10 verwendet die
versionierte Resource-URL:

`/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.5.0-beta.11`

Das lokale Icon/Logo ist Home-Assistant-Branding. Ein HACS-Repository-Icon und
das Home-Assistant-Integrationsbranding sind getrennte Dinge; zusätzliche
Manifest-Felder sind dafür nicht erforderlich.

## Einrichtung

Im Flow werden gewählt:

- Standort-Entity des Fahrzeugs
- Suchradius von 1 bis 25 km
- eine oder mehrere Kraftstoffarten
- 1 bis 10 Tankstellenplätze
- Aktualisierungsintervall
- Bewegungsupdates, Bewegungsschwelle und Cooldown
- Sortierung nach Entfernung oder Kraftstoffpreis
- ein oder mehrere Datenanbieter

Die automatische Auswahl startet ab zwei aktivierten Anbietern. Sie berücksichtigt
Land, Kraftstoff-Capability, Stationspreis-Abdeckung und vorhandene Schlüssel.
Bei nur einem Anbieter wird ausschließlich dieser Anbieter verwendet.

E10 kann in Ländern ohne verifizierte E10-Abdeckung durch E5 ersetzt werden.
Die Karte kennzeichnet dies als **E5 statt E10**. Kein E5-Ersatz erfolgt für
Diesel, LPG oder HVO100 und auch nicht allein wegen eines temporären API- oder
Stationsfehlers.

## Preise, Karte und Navigation

Die Standardreihenfolge ist Entfernung aufsteigend. Für eine Preissortierung
muss die maßgebliche Kraftstoffart eindeutig gewählt werden; Stationen ohne
gültigen Preis dafür stehen am Ende. Bei mehreren Kraftstoffen konkurrieren
Diesel, E10, E5, LPG und HVO100 nicht miteinander.

Die Custom Card zeigt je Station Name, Adresse, Öffnungsstatus, Entfernung,
alle verfügbaren Preise, Ersatzhinweise und einen Navigationsbutton. Lange
Namen und Adressen umbrechen ohne horizontalen Überlauf. Navigation kann als
Apple Maps, Google Maps, Waze oder automatisch konfiguriert werden.

Eine aktuelle UI-Screenshot-Datei ist im Repository nicht vorhanden. Die
freigegebene Branding-Vorschau ist unter
[`assets/branding/preview.png`](assets/branding/preview.png) verfügbar.

## Aktualisierung bestehender Installationen

Vor dem Update ein Home-Assistant-Backup erstellen, über HACS aktualisieren und
Home Assistant vollständig neu starten. Bestehende Config Entries,
Credentials, Stations-Slots, Sensor-Entity-IDs, Dashboard-Ressourcen und
kompatible Sensorattribute bleiben erhalten. Alte einzelne Providerwerte werden
verlustfrei in die neue Anbieterauswahl übernommen.

## Datenschutz und Attribution

Je nach ausgewähltem Anbieter können Standortkoordinaten, Radius und
Kraftstoffauswahl an den Anbieter gesendet werden. Die Integration protokolliert
keine vollständigen API-Schlüssel und gibt keine exakten Standortdaten in
Diagnosen aus. Bei Nakordoni muss die sichtbare Attribution **Data by
nakordoni.eu** erhalten bleiben.

## Fehlerbehebung

- **Keine Tankstellen:** Standort-Entity, Koordinaten, Radius, Provider-Capability
  und API-Key prüfen.
- **Preis nicht verfügbar:** Das bedeutet, dass für genau diese Station und
  Kraftstoffart kein gültiger Preis vorliegt; es wird kein anderer Kraftstoff
  eingesetzt.
- **Provider nicht aktiv:** Prüfen, ob der Anbieter in der Checkbox-Auswahl
  aktiviert und ein Schlüssel hinterlegt ist.
- **Karte nach Update veraltet:** Home Assistant vollständig neu starten. Die
  versionierte Resource-URL verhindert normalerweise die Wiederverwendung
  alter Card-Skripte.
- **Nakordoni:** Live-Freigabe, Marktberechtigung und Quoten sind weiterhin
  externe Voraussetzungen und in beta.11 nicht als erfolgreich verfügbar
  behauptet.

## Bekannte Einschränkungen

- Nakordoni-Live-Freigabe ist noch ausstehend.
- Provider- und Länderabdeckung kann sich durch externe API-Verträge,
  Berechtigungen, Quoten und Stationsdaten ändern.
- HVO100 wird nur bei verifizierter Provider-/Länder-Capability mit Preisen
  angezeigt.

## Entwicklung und Tests

Die Beta.10-Prüfung umfasst Python-Tests, Frontend-Tests, Produktions-Build,
Hassfest, JSON-/Syntaxprüfung, Bundle-Diff und `git diff --check`. Provider-
und API-Tests verwenden zusätzlich Mocks und Fixtures; unbestätigte Live-
Zugänge werden nicht als erfolgreich simuliert.
