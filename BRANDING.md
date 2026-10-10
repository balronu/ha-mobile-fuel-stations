# Branding

## Freigegebenes Original

Alle Varianten wurden ausschließlich aus dem freigegebenen Originalmotiv
`assets/branding/source-original.png` erzeugt. Das Motiv zeigt Wohnmobil,
Tankstelle, Standort-Pin mit Zapfsäule und E5, E10, Diesel, LPG sowie HVO100.
Es wurde kein neues Logo entworfen und das Seitenverhältnis wurde nicht
verzerrt.

## Dateien

### Home Assistant / Custom Integration

Home Assistant 2026.3 und neuer lädt Branding für Custom Integrations direkt
aus `custom_components/mobile_fuel_stations/brand/`:

- `icon.png` — 256 × 256
- `icon@2x.png` — 512 × 512
- `logo.png` — 256 × 256
- `logo@2x.png` — 512 × 512

Die vier Dateien sind identische, verlustarm skalierte 1x-/2x-Varianten des
quadratischen freigegebenen Motivs. Da das Original quadratisch ist, ist das
Logo ebenfalls quadratisch; dadurch bleiben Wohnmobil und Standort-Pin auch im
kleinen Icon sichtbar. Die vollständige Übersicht einschließlich 64- und
32-Pixel-Kontrolle ist [`assets/branding/preview.png`](assets/branding/preview.png).

### Offizielles Home-Assistant-Brands-Repository

Für einen späteren, manuell einzureichenden Brands-Pull-Request ist folgende
Struktur vorbereitet:

```text
custom_integrations/mobile_fuel_stations/
├── icon.png
├── icon@2x.png
├── logo.png
└── logo@2x.png
```

Die lokale Custom-Integration ist für Home Assistant ab 2026.3 bereits der
technisch bevorzugte Auslieferungsweg. Die offizielle Brands-Einbindung ist
erst nach Annahme und Merge des externen Pull Requests bestätigt; bis dahin
darf keine erfolgreiche CDN-Auslieferung behauptet werden.

## HACS-Abgrenzung

- **HACS-Repository-Darstellung:** HACS zeigt Repository-Metadaten und das
  GitHub-Repositorybild/Avatar. Dafür gibt es kein unterstütztes
  `hacs.json`-Brandingfeld; es wurde kein erfundenes Manifestfeld ergänzt.
- **Home-Assistant-Integrationssymbol:** Wird ab HA 2026.3 aus dem lokalen
  `brand/icon*.png` geladen.
- **Home-Assistant-Integrationslogo:** Wird ab HA 2026.3 aus dem lokalen
  `brand/logo*.png` geladen.
- **Social Preview:** Ein GitHub-Social-Preview kann sinnvoll sein, ist aber
  eine Repository-Einstellung und wurde deshalb nur als manueller Schritt
  vorgemerkt, nicht automatisch geändert.

## Manuelle Schritte

1. Diesen Branding-Commit auf dem Entwicklungsbranch prüfen und nach Wunsch in
   den HACS-Branch übernehmen.
2. Den vorbereiteten Inhalt aus `custom_integrations/mobile_fuel_stations/`
   in einen Fork von `home-assistant/brands` übernehmen und dort einen PR
   eröffnen. Dieser Schritt wurde aus Sicherheitsgründen nicht automatisch
   abgesendet.
3. Nach Merge des Brands-PR die CDN-URLs prüfen und die übliche Cache-Zeit
   berücksichtigen. Erst dann ist die offizielle Brands-Einbindung bestätigt.
4. Optional das GitHub-Social-Preview im Repository manuell setzen.

## Qualitätsstatus

Die automatisierte Prüfung umfasst PNG-Signatur, RGBA/Transparenz, exakte
Abmessungen, identische 1x-/2x-Quellvariante, verlustarme Lanczos-Skalierung,
Dateigrößen und Sichtprüfung bei 32 × 32 sowie 64 × 64 Pixeln. Die
Repository-Tests und der Produktions-Build bleiben vom Branding unverändert.
