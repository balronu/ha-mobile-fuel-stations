# v0.7.0-beta.6

## Nakordoni OAuth and market-aware Auto mode

- OAuth2 with PKCE S256 and the official Home Assistant redirect remains the preferred Nakordoni setup; manual API-key configuration remains supported.
- OAuth-only entries are recognized without exposing tokens. Existing config entries retain their schema and provider cooldown state.
- `markets_approved`, `markets_granted`, `markets_allowed`, `markets_available`, and `upgrade_url` are kept separate and reported without credentials.
- A missing market grant does not trigger a Nakordoni Auto request. HTTP `market_not_allowed` remains a permission outcome.
- Auto provider order is Tankerkönig → Nakordoni → suitable Petromap in Germany, Petromap → Nakordoni in Austria, and Nakordoni → suitable Petromap elsewhere when explicit market and fuel capability are known.
- HVO100 remains disabled for Nakordoni; the documented `hvo` name is not treated as proof that it means HVO100.
- Nakordoni attribution remains `Data by nakordoni.eu`.

No live OAuth login or provider API request is required by the test suite.
