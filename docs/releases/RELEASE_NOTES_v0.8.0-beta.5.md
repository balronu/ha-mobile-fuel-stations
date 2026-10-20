# Mobile Fuel Stations v0.8.0-beta.5

## Status, Kontingent und Startup

- Provider-Cooldowns werden je konfiguriertem Provider mit einer backendseitig berechneten absoluten Endzeit bereitgestellt. Die Lovelace-Karte zählt diese Endzeit lokal herunter, ohne Provider- oder Usage-Aufrufe auszulösen.
- Der manuelle Abrufbutton bleibt aktiv, wenn ein anderer konfigurierter und berechtigter Provider den Abruf übernehmen kann. Sind alle zulässigen Provider blockiert, bleibt er serverseitig gesperrt.
- Nakordoni-Kontingente verwenden ausschließlich die vorhandenen Account-Usage-Daten. Tankerkönig und Petromap zeigen bei fehlender belastbarer Providerinformation „Kontingent nicht verfügbar“.
- Usage-Daten und ihr letzter erfolgreicher Aktualisierungszeitpunkt werden geheimnisfrei persistiert und nach einem Neustart nicht als frisch ausgegeben, wenn sie veraltet sind.
- Stationscache und Zeitstempel des letzten erfolgreichen Abrufs werden beim Start berücksichtigt. Ein frischer automatischer Cache löst keinen vorzeitigen Providerabruf aus.
- Fällige Startup-Abrufe werden kontrolliert verzögert und zusammen mit Timer-, GPS- und Recovery-Auslösern dedupliziert. Der manuelle Modus löst beim Start weiterhin keinen Abruf aus.

## Grenzen

- Es werden keine Kontingente geschätzt und keine zusätzlichen Provider- oder Usage-Aufrufe allein für die Darstellung ausgelöst.
- Die Beta.4-Fallback-Regeln sowie die zuvor korrigierte Nakordoni-Marktberechtigungs-Synchronisierung bleiben erhalten.
- Keine produktiven HA-, Config-Entry-, Backup-, Provider- oder OAuth-Änderungen.
