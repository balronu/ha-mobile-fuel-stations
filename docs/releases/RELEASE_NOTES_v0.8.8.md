# Mobile Fuel Stations v0.8.8 — Stable

## Deutsch

v0.8.8 behebt den iPhone-Erstkonfigurationsfehler bei der Kraftstoffauswahl.
Die Sortierkraftstoff-Auswahl folgt jetzt in einem eigenen Formularschritt und
enthält nur E5, Diesel oder die tatsächlich mehrfach ausgewählten Kraftstoffe.
Ungültige gespeicherte Sortierwerte werden automatisch auf den ersten gültigen
Kraftstoff korrigiert; bestehende Config Entries und Options bleiben kompatibel.

Die Datenschutzkorrektur aus PR #65 ist enthalten: Nakordoni-Diagnosen geben
keine präzisen `lat`-/`lng`-Koordinaten aus. `radius_km`, Provider-Anfragen und
die tatsächliche Standortberechnung bleiben unverändert.

Dies ist ein reguläres Stable-Release. Nach dem Update sollte die Integration
über HACS neu geladen bzw. Home Assistant nach den üblichen lokalen Richtlinien
neu gestartet werden; eine automatische Installation wird nicht ausgelöst.

## English

v0.8.8 fixes the iPhone first-configuration fuel-selection issue. Price-sorting
fuel is now selected in a dedicated form step and contains only E5, diesel, or
the fuels actually selected in a multi-fuel choice. Invalid stored sorting values
are automatically repaired to the first valid fuel; existing Config Entries and
options remain compatible.

The privacy correction from PR #65 is included: Nakordoni diagnostics no longer
export precise `lat`/`lng` coordinates. `radius_km`, provider requests, and the
actual location calculation remain unchanged.

This is a regular Stable release. After updating, reload the integration or
restart Home Assistant according to the local maintenance policy; no automatic
installation is performed.
