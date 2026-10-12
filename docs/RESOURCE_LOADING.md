# Mobile Fuel Stations resource loading

## v0.5.1-beta.1 loading path

The integration serves the versioned module through Home Assistant's supported
`add_extra_js_url` API and serves the file through
`async_register_static_paths`. The static path uses `cache_headers=False`; the
URL contains the integration version (`?v=0.5.1-beta.1`). Registration is idempotent.

The bundle registers immediately and retries registration once on the browser
`load` event. This covers the observed case where Home Assistant imports an
extra module before replacing the Custom Element registry. It does not poll,
reload the page, or add a second script URL.

## Why the integration does not write a Lovelace resource automatically

Home Assistant has separate resource collections for YAML and storage modes.
Storage resources are managed through the Lovelace resource WebSocket/UI, while
YAML resources are declared in dashboard configuration. There is no stable
integration API that safely writes one resource to both modes. The integration
therefore must not edit `.storage` files or maintain a second automatic
registration path.

Adding the same URL manually while this automatic path is active is not a
supported migration: it creates two module load paths, even though the custom
element guard prevents duplicate `define()` calls.

For a future release that deliberately switches to explicit resources, the
manual storage-mode migration is:

1. Open **Settings → Dashboards → Resources**.
2. Add `/mobile_fuel_stations/mobile-fuel-stations-card.js?v=<release>` as a
   `module` resource.
3. Confirm the old automatic path has been removed in that release before
   testing the dashboard.
4. Reload dashboard resources through the HA UI.

No such switch is made by v0.5.1-beta.1; existing dashboard configurations remain
unchanged.
