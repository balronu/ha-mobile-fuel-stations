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
    CONF_PETROMAP_API_KEY,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    CONF_TANKERKOENIG_API_KEY,
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


@pytest.mark.parametrize(
    ("source", "target", "source_credentials", "new_credentials", "expected"),
    [
        (
            PROVIDER_TANKERKOENIG,
            PROVIDER_PETROMAP,
            {CONF_API_KEY: "tk-old"},
            {CONF_API_KEY: "pm-new"},
            {CONF_API_KEY: "pm-new"},
        ),
        (
            PROVIDER_PETROMAP,
            PROVIDER_TANKERKOENIG,
            {CONF_API_KEY: "pm-old"},
            {CONF_API_KEY: "tk-new"},
            {CONF_API_KEY: "tk-new"},
        ),
        (
            PROVIDER_TANKERKOENIG,
            PROVIDER_AUTO,
            {CONF_API_KEY: "tk-old"},
            {CONF_PETROMAP_API_KEY: "pm-new"},
            {
                CONF_TANKERKOENIG_API_KEY: "tk-old",
                CONF_PETROMAP_API_KEY: "pm-new",
            },
        ),
        (
            PROVIDER_PETROMAP,
            PROVIDER_AUTO,
            {CONF_API_KEY: "pm-old"},
            {CONF_TANKERKOENIG_API_KEY: "tk-new"},
            {
                CONF_TANKERKOENIG_API_KEY: "tk-new",
                CONF_PETROMAP_API_KEY: "pm-old",
            },
        ),
        (
            PROVIDER_AUTO,
            PROVIDER_TANKERKOENIG,
            {
                CONF_TANKERKOENIG_API_KEY: "tk-old",
                CONF_PETROMAP_API_KEY: "pm-old",
            },
            {},
            {CONF_API_KEY: "tk-old"},
        ),
        (
            PROVIDER_AUTO,
            PROVIDER_PETROMAP,
            {
                CONF_TANKERKOENIG_API_KEY: "tk-old",
                CONF_PETROMAP_API_KEY: "pm-old",
            },
            {},
            {CONF_API_KEY: "pm-old"},
        ),
        (
            None,
            PROVIDER_PETROMAP,
            {CONF_API_KEY: "legacy-tk"},
            {CONF_API_KEY: "pm-new"},
            {CONF_API_KEY: "pm-new"},
        ),
        (
            None,
            PROVIDER_AUTO,
            {CONF_API_KEY: "legacy-tk"},
            {CONF_PETROMAP_API_KEY: "pm-new"},
            {
                CONF_TANKERKOENIG_API_KEY: "legacy-tk",
                CONF_PETROMAP_API_KEY: "pm-new",
            },
        ),
    ],
)
def test_provider_switch_rebuilds_canonical_credentials(
    source, target, source_credentials, new_credentials, expected
):
    source_data = {**_data(), **source_credentials}
    if source is not None:
        source_data[CONF_PROVIDER_MODE] = source
    entry = _entry(source_data)
    flow = _flow(entry)
    submitted = {
        key: value
        for key, value in {**_data(), CONF_PROVIDER_MODE: target}.items()
        if key
        not in {CONF_API_KEY, CONF_TANKERKOENIG_API_KEY, CONF_PETROMAP_API_KEY}
    }

    result = asyncio.run(flow.async_step_init(submitted))
    current_mode = source or PROVIDER_TANKERKOENIG
    if target in (PROVIDER_PETROMAP, PROVIDER_AUTO) and current_mode not in (
        PROVIDER_PETROMAP,
        PROVIDER_AUTO,
    ):
        assert result["step_id"] == "options_petromap_privacy"
        result = asyncio.run(flow.async_step_options_petromap_privacy({}))
    if result["type"] == "form":
        result = asyncio.run(flow.async_step_provider_credentials(new_credentials))

    assert result["type"] == "create_entry"
    assert entry.data[CONF_PROVIDER_MODE] == target
    assert {key: entry.data[key] for key in expected} == expected
    credential_keys = {
        CONF_API_KEY,
        CONF_TANKERKOENIG_API_KEY,
        CONF_PETROMAP_API_KEY,
    }
    assert {
        key: entry.data[key] for key in credential_keys if key in entry.data
    } == expected
    assert not credential_keys.intersection(result["data"])
