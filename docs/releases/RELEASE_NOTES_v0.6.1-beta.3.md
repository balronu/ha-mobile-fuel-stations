# Mobile Fuel Stations v0.6.1-beta.3

## Deutsch

Diese Beta behebt den Startup-/Reload-Cooldown-Fehler aus Beta.2. Die letzte
gültige Stationsliste wird im bestehenden Home-Assistant-Store gespeichert,
bei einem passenden Reload als veraltet (`data_stale=true`) wiederhergestellt
und nach Ablauf des Provider-Cooldowns automatisch aktualisiert. Ungültige,
unvollständige oder zu einem anderen Query-Kontext beziehungsweise Standort
gehörende Cache-Daten werden verworfen. API-Schlüssel und zusätzliche private
GPS-Daten werden nicht gespeichert.

Adaptive Aktualisierung bleibt standardmäßig deaktiviert und verwendet dieselbe
Recovery- und Parallelitätsabsicherung wie die Legacy-Aktualisierung.

## English

This beta fixes the Beta.2 startup/reload cooldown race. The last validated
station result is stored in the existing Home Assistant Store, restored as
visible stale data (`data_stale=true`) for a matching reload, and refreshed
automatically after the provider cooldown. Malformed, incomplete, or cached
data belonging to a different query context or location is discarded. API
keys and additional private GPS data are not stored.

Adaptive updates remain disabled by default and use the same recovery and
single-provider-flight safeguards as legacy updates.

Stable `v0.6.0` remains unchanged. This is a GitHub pre-release for controlled
testing; no live Home Assistant installation is modified by this release.
