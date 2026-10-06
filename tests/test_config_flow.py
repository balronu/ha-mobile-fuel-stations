import asyncio
from types import SimpleNamespace

from mobile_fuel_stations.config_flow import MobileFuelStationsConfigFlow
from mobile_fuel_stations.const import (
    CONF_API_KEY,
    CONF_COOLDOWN,
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_MOVEMENT_THRESHOLD,
    CONF_MOVEMENT_UPDATES,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    CONF_UPDATE_INTERVAL,
    DEFAULT_COOLDOWN,
    DEFAULT_MOVEMENT_THRESHOLD,
    DEFAULT_MOVEMENT_UPDATES,
    DEFAULT_RADIUS,
    DEFAULT_STATION_COUNT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    CONF_PROVIDER_MODE,
    PROVIDER_AUTO,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
)


def _entry(data, options=None):
    return SimpleNamespace(
        entry_id="entry-a",
        data=data,
        options=options or {},
    )


def _flow(entry):
    flow = MobileFuelStationsConfigFlow.async_get_options_flow(entry)
    # OptionsFlow derives its public ``config_entry`` property from the
    # handler set by Home Assistant's flow manager.  Do not assign the
    # read-only ``_config_entry_id`` implementation detail directly.
    flow.handler = entry.entry_id
    flow.hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_get_known_entry=lambda entry_id: entry,
            async_get_entry=lambda entry_id: entry,
            async_update_entry=lambda current, data: current.data.update(data),
        )
    )
    return flow


def _data():
    return {
        CONF_API_KEY: "secret-not-for-options",
        CONF_LOCATION_ENTITY: "device_tracker.vehicle",
        CONF_RADIUS: 20.0,
        CONF_FUEL_TYPE: "diesel",
        CONF_STATION_COUNT: 5,
        CONF_UPDATE_INTERVAL: 15,
        CONF_MOVEMENT_UPDATES: True,
        CONF_MOVEMENT_THRESHOLD: 2.0,
        CONF_COOLDOWN: 5,
    }


def test_existing_entry_options_flow_starts_without_config_entry_setter_error():
    entry = _entry(_data())
    flow = _flow(entry)

    result = asyncio.run(flow.async_step_init())

    assert result["type"] == "form"
    values = result["data_schema"]({})
    assert values[CONF_LOCATION_ENTITY] == "device_tracker.vehicle"
    assert values[CONF_RADIUS] == 20.0
    assert values[CONF_FUEL_TYPE] == "diesel"
    assert values[CONF_STATION_COUNT] == 5
    assert CONF_API_KEY not in str(result["data_schema"].schema)


def test_options_override_data_and_missing_values_use_defaults():
    entry = _entry(
        {CONF_LOCATION_ENTITY: "device_tracker.old", CONF_RADIUS: 10.0},
        {CONF_LOCATION_ENTITY: "device_tracker.vehicle", CONF_FUEL_TYPE: "e10"},
    )
    flow = _flow(entry)

    result = asyncio.run(flow.async_step_init())
    values = result["data_schema"]({})

    assert values[CONF_LOCATION_ENTITY] == "device_tracker.vehicle"
    assert values[CONF_RADIUS] == 10.0
    assert values[CONF_FUEL_TYPE] == "e10"
    assert values[CONF_STATION_COUNT] == DEFAULT_STATION_COUNT
    assert values[CONF_UPDATE_INTERVAL] == DEFAULT_UPDATE_INTERVAL
    assert values[CONF_MOVEMENT_UPDATES] is DEFAULT_MOVEMENT_UPDATES
    assert values[CONF_MOVEMENT_THRESHOLD] == DEFAULT_MOVEMENT_THRESHOLD
    assert values[CONF_COOLDOWN] == DEFAULT_COOLDOWN


def test_options_save_preserves_api_key_in_data_and_excludes_it_from_options():
    entry = _entry(_data())
    flow = _flow(entry)
    submitted = {key: value for key, value in _data().items() if key != CONF_API_KEY}
    submitted[CONF_RADIUS] = 25.0

    result = asyncio.run(flow.async_step_init(submitted))

    assert result["type"] == "create_entry"
    assert result["data"][CONF_RADIUS] == 25.0
    assert CONF_API_KEY not in result["data"]
    assert entry.data[CONF_API_KEY] == "secret-not-for-options"


def test_legacy_entry_with_empty_options_gets_a_complete_form():
    entry = _entry(
        {
            CONF_API_KEY: "legacy-secret",
            CONF_LOCATION_ENTITY: "sensor.vehicle",
        },
        {},
    )
    flow = _flow(entry)

    result = asyncio.run(flow.async_step_init())
    values = result["data_schema"]({})

    assert values[CONF_LOCATION_ENTITY] == "sensor.vehicle"
    assert values[CONF_RADIUS] == DEFAULT_RADIUS
    assert values[CONF_FUEL_TYPE] == "diesel"
    assert values[CONF_STATION_COUNT] == DEFAULT_STATION_COUNT


def test_legacy_radius_above_provider_limit_is_loaded_defensively():
    entry = _entry({**_data(), CONF_RADIUS: 50.0}, {})
    flow = _flow(entry)
    result = asyncio.run(flow.async_step_init())
    values = result["data_schema"]({})
    assert values[CONF_RADIUS] == 25.0


def test_options_provider_switch_tankerkoenig_to_petromap_requires_privacy_and_key():
    entry = _entry(
        {
            **_data(),
            CONF_PROVIDER_MODE: PROVIDER_TANKERKOENIG,
        }
    )
    flow = _flow(entry)
    submitted = {
        key: value
        for key, value in {**_data(), CONF_PROVIDER_MODE: PROVIDER_PETROMAP}.items()
        if key != CONF_API_KEY
    }

    privacy = asyncio.run(flow.async_step_init(submitted))
    assert privacy["step_id"] == "options_petromap_privacy"
    credentials = asyncio.run(flow.async_step_options_petromap_privacy({}))
    assert credentials["step_id"] == "provider_credentials"
    result = asyncio.run(
        flow.async_step_provider_credentials({CONF_API_KEY: "petromap-new"})
    )

    assert result["type"] == "create_entry"
    assert entry.data[CONF_PROVIDER_MODE] == PROVIDER_PETROMAP
    assert entry.data[CONF_API_KEY] == "petromap-new"
    assert CONF_API_KEY not in result["data"]


def test_options_provider_switch_petromap_to_auto_preserves_pm_and_requires_tk():
    entry = _entry(
        {
            **_data(),
            CONF_PROVIDER_MODE: PROVIDER_PETROMAP,
            CONF_API_KEY: "pm-old",
        }
    )
    flow = _flow(entry)
    submitted = {**_data(), CONF_PROVIDER_MODE: PROVIDER_AUTO}

    credentials = asyncio.run(flow.async_step_init(submitted))
    assert credentials["step_id"] == "provider_credentials"
    result = asyncio.run(
        flow.async_step_provider_credentials(
            {CONF_TANKERKOENIG_API_KEY: "tk-new"}
        )
    )

    assert result["type"] == "create_entry"
    assert entry.data[CONF_PROVIDER_MODE] == PROVIDER_AUTO
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "tk-new"
    assert entry.data[CONF_PETROMAP_API_KEY] == "pm-old"
    assert CONF_API_KEY not in entry.data
    assert CONF_API_KEY not in result["data"]
