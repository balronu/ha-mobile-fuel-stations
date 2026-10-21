# Mobile Fuel Stations v0.8.4-beta.6

## Deutsch

Beta.6 korrigiert die verbliebene Kopfbereich-Trennlinie bei ausgeblendetem
Abrufmodus.

- Ursache war ein leerer `.controls`-Wrapper: `show_refresh: true` machte die
  Sektion sichtbar, obwohl im automatischen Modus kein Refresh-Button gerendert
  wurde.
- Der Wrapper wird jetzt nur noch gerendert, wenn der Abrufmodus sichtbar ist
  oder im manuellen Modus tatsächlich ein Aktualisieren-Button vorhanden ist.
- Der gemeinsame Stack setzt weiterhin höchstens eine `border-bottom`-Linie
  zwischen benachbarten sichtbaren Sektionen.
- Regressionen prüfen DOM-Grenzen, Rahmenregel und Abstände in Ausführlich,
  Kompakt und Individuell.
- Die funktionierenden Tankstellenzeilen, Logos, Abstände und
  Trennlinienoptionen bleiben unverändert.

`v0.8.3` bleibt Latest Stable. Diese Version ist ein GitHub-Pre-release; es
wurden keine produktiven Home-Assistant-Systeme, VM 104, Dashboards,
Config Entries, Provider, OAuth-Flows oder Backups verändert.

## English

Beta.6 fixes the remaining header separator issue when the fetch-mode control
is hidden.

- The cause was an empty `.controls` wrapper: `show_refresh: true` kept the
  section visible although automatic mode rendered no refresh button.
- The wrapper is now rendered only when fetch mode is visible or a real refresh
  button exists in manual mode.
- The shared stack continues to use at most one `border-bottom` between adjacent
  visible sections.
- Regression coverage checks DOM boundaries, border rules, and spacing in
  Detailed, Compact, and Individual modes.
- Existing station rows, logos, spacing, and divider options are unchanged.

`v0.8.3` remains Latest Stable. This is a GitHub pre-release; no productive
Home Assistant system, VM 104, dashboard, Config Entry, provider, OAuth flow,
or backup was changed.
