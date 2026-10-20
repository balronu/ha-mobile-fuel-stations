# Mobile Fuel Stations v0.8.0-beta.3

## Praxis-Hotfix

- Der manuelle Abrufbutton bleibt bei aktivem, vom Backend gemeldetem
  Provider-Cooldown deaktiviert und zeigt die verbleibende Zeit als `m:ss`.
- Der Countdown verwendet die Backend-Angabe als Freigabegrundlage. Der
  Ablauf-Refresh aktualisiert nur den HA-Zustand und startet keinen
  Provideraufruf.
- Modussteuerung, manueller Abruf, Cooldown, Providerantwort, Kontingent,
  fehlende Standortdaten sowie Netzwerk-/Timeoutfehler werden getrennt
  dargestellt. Vorhandene Tankstellen bleiben bei Abruffehlern sichtbar.
- API-Abrufzeit und Alter der einzelnen Providerpreise werden getrennt
  behandelt. Alte Providerpreise bleiben als veraltet gekennzeichnet; ein
  erfolgreicher Abruf verspricht keine frischen Preise.
- Tankerkönig klassifiziert HTTP 401/403, 429, 5xx, ungültiges JSON,
  `ok=false` und fehlerhafte Stationslisten ohne API-Schlüssel oder Rohantwort
  offenzulegen.

## Grenzen und Diagnose

Die konkrete Ursache eines einzelnen Tankerkönig-`ProviderResponseError` aus
dem Praxistest ist ohne die zugehörigen, geheimnisfreien Providerdiagnosen
nicht nachgewiesen. Beta.3 verbessert die Klassifikation und Persistenz der
Diagnosedaten, führt aber keinen Live-Provider- oder OAuth-Aufruf aus.

Stable `v0.7.3` bleibt unverändert; Beta.2 bleibt als historische Pre-release
erhalten. Es wurden keine HA-VM-, Config-Entry-, Backup- oder Produktivdaten
geändert.
