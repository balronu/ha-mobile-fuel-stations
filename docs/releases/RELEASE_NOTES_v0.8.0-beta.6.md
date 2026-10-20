# Mobile Fuel Stations v0.8.0-beta.6

## Nakordoni-Berechtigungen und Provider-Verfügbarkeit

- Explizite `markets_approved`-Länder aus dokumentierten Nakordoni-Usage-Daten werden für die Auto-Auswahl synchronisiert.
- Numerisches `markets.allowed` wird nicht als Länderberechtigung interpretiert.
- Unvollständige Usage-Antworten löschen keine zuvor bestätigten Marktberechtigungen.
- API-Key- und OAuth2-Zugänge verwenden dieselbe geheime-freie Verfügbarkeitsentscheidung.
- Ein bestätigtes Kontingent von null sperrt den Provider; unbekannte oder veraltete Kontingente werden nicht als erschöpft angenommen.
- Tankerkönig-Cooldown und Nakordoni-Marktabdeckung werden getrennt bewertet. Ein zulässiger Nakordoni-Fallback hält den manuellen Abruf frei.
- Providerbezogene Sperrgründe werden an die Lovelace-Karte übertragen.
- Ein globaler Countdown erscheint nur, wenn sein Ablauf einen zulässigen Provider freischalten kann; unabhängige Sperrgründe bleiben sichtbar.
- Persistierte Markt-/Usage-Daten werden beim Start vor der ersten Auto-Auswahl wiederhergestellt, ohne zusätzliche Provider- oder Usage-Aufrufe.

## Grenzen

- Keine Live-Provider- oder OAuth-Aufrufe im Entwicklungs- und Testlauf.
- Keine Änderungen an produktiven Home-Assistant-Config-Entries, Dashboards, VM 104 oder Backups.
- Beta.6 wird als Kandidat vorbereitet; Merge, Tag und Release benötigen eine separate Freigabe.
