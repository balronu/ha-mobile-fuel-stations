# Mobile Fuel Stations v0.6.1

## Deutsch

Diese Stable-Version ergänzt die adaptive GPS-Aktualisierung und behebt die
Reload-/Cooldown-Lücke aus Beta.2. Die adaptive Option bleibt standardmäßig
deaktiviert und kann über den Optionsdialog aktiviert werden. Bei gültiger,
aktueller GPS-Geschwindigkeit gelten die Zielintervalle 15 Minuten im
Stillstand, 5 Minuten bis 30 km/h, 2 Minuten über 30 bis 70 km/h und 1 Minute
über 70 km/h. Provider-Cooldowns, Rate-Limits und `Retry-After` haben immer
Vorrang.

Die letzte validierte Stationsliste wird im bestehenden Home-Assistant-Store
persistiert und nach einem passenden Reload sofort als `data_stale=true`
wiederhergestellt. Nach Ablauf des Cooldowns wird höchstens ein deduplizierter
Provider-Refresh ausgeführt. Bestehende Config Entries, Optionen, Provider,
Entities und die unabhängig versionierte Lovelace-Komponente `0.6.0` bleiben
rückwärtskompatibel.

Die bewegungsabhängigen Intervalle sind automatisiert getestet, wurden aber
nicht während einer echten Fahrt live bestätigt.

## English

This stable release adds adaptive GPS refresh and fixes the Beta.2
reload/cooldown gap. Adaptive updates remain disabled by default and can be
enabled through the Options flow. With valid, current GPS speed, the target
intervals are 15 minutes while stationary, 5 minutes up to 30 km/h, 2 minutes
above 30 to 70 km/h, and 1 minute above 70 km/h. Provider cooldowns,
rate-limits, and `Retry-After` always take precedence.

The last validated station result is persisted in the existing Home Assistant
Store and restored immediately after a matching reload as `data_stale=true`.
At most one deduplicated provider refresh is scheduled after cooldown expiry.
Existing config entries, options, providers, entities, and the independently
versioned `0.6.0` Lovelace component remain backward compatible.

The movement-dependent intervals are covered by automated tests but were not
live-confirmed during an actual drive.
