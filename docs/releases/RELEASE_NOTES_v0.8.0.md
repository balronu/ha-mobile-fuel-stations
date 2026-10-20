# Mobile Fuel Stations v0.8.0 — Stable

## Deutsch

### Neuerungen und Korrekturen

- Automatischer und manueller Abrufmodus pro Config Entry.
- API-sparende Startup-, Cache- und Recovery-Steuerung mit persistiertem
  Stationscache und letztem erfolgreichen Abruf.
- Providerbezogene Verfügbarkeitsprüfung mit Mindestintervallen,
  Retry-/Rate-Limit-Cooldowns, Marktberechtigungen, Kontingenten und
  begrenztem Fallback.
- Korrigierte Ländererkennung: später eintreffende gültige GPS-Positionen
  aktualisieren auch im manuellen Modus den lokalen Länder-Kontext.
- Nakordoni-Kontingentanzeige mit Datenalter sowie getrennten API-Key- und
  OAuth2-Zugängen.
- Aussagekräftigere Sperrgründe, Countdown- und Lovelace-Statusanzeigen.
- Bestehende Tankstellenliste, Preise, Navigation und lokale Markenlogos
  bleiben erhalten.

### Kompatibilität und Grenzen

- Bestehende Config Entries, Abrufmodi, Cache-Daten und Zugangsdaten werden
  ohne destruktive Migration weiterverwendet.
- Tankerkönig, Nakordoni und Petromap werden nur entsprechend ihrer
  konfigurierten Zugangsdaten, Marktberechtigungen und tatsächlichen
  Providerabdeckung verwendet.
- Die Release-Prüfung nutzt Tests, Mocks, Fixtures, Hassfest und GitHub-CI.
  Es wurden keine Live-Provider- oder OAuth-Aufrufe durchgeführt.
- Preise, Öffnungszeiten, Quoten, Marktberechtigungen und HVO100-Abdeckung
  hängen von den jeweiligen Providern und Konten ab.

## English

### Improvements and fixes

- Per-config-entry automatic and manual fetch modes.
- API-conscious startup, cache, and recovery control with persisted station
  cache and last successful fetch.
- Provider-specific availability checks covering minimum intervals,
  retry/rate-limit cooldowns, market permissions, quotas, and bounded fallback.
- Fixed country detection: later valid GPS positions update the local country
  context in manual mode as well.
- Nakordoni quota display with data age and separate API-key and OAuth2 paths.
- More informative blocking reasons, countdowns, and Lovelace status updates.
- Existing station lists, prices, navigation, and local station logos remain
  available.

### Compatibility and limitations

- Existing config entries, fetch modes, cache data, and credentials are reused
  without destructive migrations.
- Tankerkönig, Nakordoni, and Petromap are used only according to configured
  credentials, market permissions, and actual provider coverage.
- Release validation uses tests, mocks, fixtures, Hassfest, and GitHub CI. No
  live provider or OAuth calls were performed.
- Prices, opening hours, quotas, market permissions, and HVO100 coverage
  depend on the respective providers and accounts.
