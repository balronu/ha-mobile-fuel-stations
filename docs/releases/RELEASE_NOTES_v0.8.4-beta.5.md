# Mobile Fuel Stations v0.8.4-beta.5

## Deutsch

Beta.5 korrigiert ausschließlich den Kopfbereich der Lovelace-Karte. Die
Tankstellenzeilen aus beta.4 wurden nicht funktional verändert.

- Sichtbare Kopfbereich-Sektionen werden in einem gemeinsamen Stack gerendert.
- Zwischen benachbarten sichtbaren Sektionen gibt es höchstens eine Trennlinie.
- Deaktivierte Titel-/Metadaten-, Abrufmodus-, Diagnose- und Aktualisieren-Bereiche
  hinterlassen keinen leeren Wrapper und keinen zusätzlichen Rand.
- Das Verhalten ist in Ausführlich, Kompakt und Individuell identisch.
- Die Resource-URL lautet `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.8.4-beta.5`.

Die Beta ist ein Pre-release. `v0.8.3` bleibt Latest Stable. Ein bereits
ausgeführtes JavaScript-Modul kann weiterhin ein einmaliges Dashboard-Neuladen
erfordern; es gibt keinen riskanten automatischen Hard-Reload.

## English

Beta.5 is a focused header-layout correction. The station rows from beta.4 are
otherwise unchanged.

- Visible header sections are rendered in one shared stack.
- At most one separator is rendered between adjacent visible sections.
- Disabled title/metadata, fetch-mode, diagnostics, and refresh sections leave no
  empty wrapper or extra border.
- The behavior is consistent across Detailed, Compact, and Individual modes.
- The resource URL is `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=0.8.4-beta.5`.

This is a pre-release; `v0.8.3` remains Latest Stable. An already executed
JavaScript module may still require one dashboard reload.
