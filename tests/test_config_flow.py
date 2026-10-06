import asyncio
from types import SimpleNamespace

import pytest

import mobile_fuel_stations as integration
from mobile_fuel_stations.config_flow import MobileFuelStationsConfigFlow
from mobile_fuel_stations.const import (
    CONF_API_KEY,
    CONF_COOLDOWN,
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_MOVEMENT_THRESHOLD,
    CONF_MOVEMENT_UPDATES,
    CONF_PETROMAP_API_KEY,
    CONF_PETROMAP_PRIVACY_ACCEPTED,
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

    def async_update_entry(current, *, data, options=None):
        current.data = dict(data)
        if options is not None:
            current.options = dict(options)
        return True

    flow.hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_get_known_entry=lambda entry_id: entry,
            async_get_entry=lambda entry_id: entry,
            async_update_entry=async_update_entry,
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


def test_options_save_preserves_tankerkoenig_key_in_data_and_excludes_credentials_from_options():
    entry = _entry(_data())
    flow = _flow(entry)
    submitted = {key: value for key, value in _data().items() if key != CONF_API_KEY}
    submitted[CONF_RADIUS] = 25.0

    result = asyncio.run(flow.async_step_init(submitted))

    assert result["type"] == "create_entry"
    assert result["data"][CONF_RADIUS] == 25.0
    assert CONF_API_KEY not in result["data"]
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "secret-not-for-options"
    assert CONF_API_KEY not in entry.data
    assert entry.options[CONF_RADIUS] == 25.0


def test_options_save_updates_data_and_options_in_one_entry_update():
    entry = _entry(_data())
    calls = []

    class ConfigEntries:
        def async_get_known_entry(self, entry_id):
            return entry

        def async_get_entry(self, entry_id):
            return entry

        def async_update_entry(self, current, *, data, options):
            calls.append((dict(data), dict(options)))
            current.data = dict(data)
            current.options = dict(options)
            return True

    flow = MobileFuelStationsConfigFlow.async_get_options_flow(entry)
    flow.handler = entry.entry_id
    flow.hass = SimpleNamespace(config_entries=ConfigEntries())
    submitted = {**_data(), CONF_FUEL_TYPE: "lpg"}

    result = asyncio.run(flow.async_step_init(submitted))

    assert result["type"] == "create_entry"
    assert len(calls) == 1
    assert calls[0][0][CONF_TANKERKOENIG_API_KEY] == "secret-not-for-options"
    assert CONF_API_KEY not in calls[0][0]
    assert calls[0][1][CONF_FUEL_TYPE] == "lpg"
    assert entry.options[CONF_FUEL_TYPE] == "lpg"


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
    assert entry.data[CONF_PETROMAP_API_KEY] == "petromap-new"
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "secret-not-for-options"
    assert entry.data[CONF_PETROMAP_PRIVACY_ACCEPTED] is True
    assert CONF_API_KEY not in result["data"]


def test_options_provider_switch_petromap_to_auto_preserves_pm_and_requires_tk():
    entry = _entry(
        {
            **_data(),
            CONF_PROVIDER_MODE: PROVIDER_PETROMAP,
            CONF_API_KEY: "pm-old",
            CONF_PETROMAP_PRIVACY_ACCEPTED: True,
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
    assert entry.options[CONF_FUEL_TYPE] == "diesel"


@pytest.mark.parametrize(
    ("source", "target", "source_credentials", "new_credentials", "expected"),
    [
        (
            PROVIDER_TANKERKOENIG,
            PROVIDER_PETROMAP,
            {CONF_API_KEY: "tk-old"},
            {CONF_PETROMAP_API_KEY: "pm-new"},
            {
                CONF_TANKERKOENIG_API_KEY: "tk-old",
                CONF_PETROMAP_API_KEY: "pm-new",
            },
        ),
        (
            PROVIDER_PETROMAP,
            PROVIDER_TANKERKOENIG,
            {CONF_API_KEY: "pm-old"},
            {CONF_TANKERKOENIG_API_KEY: "tk-new"},
            {
                CONF_TANKERKOENIG_API_KEY: "tk-new",
                CONF_PETROMAP_API_KEY: "pm-old",
            },
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
            {
                CONF_TANKERKOENIG_API_KEY: "tk-old",
                CONF_PETROMAP_API_KEY: "pm-old",
            },
        ),
        (
            PROVIDER_AUTO,
            PROVIDER_PETROMAP,
            {
                CONF_TANKERKOENIG_API_KEY: "tk-old",
                CONF_PETROMAP_API_KEY: "pm-old",
            },
            {},
            {
                CONF_TANKERKOENIG_API_KEY: "tk-old",
                CONF_PETROMAP_API_KEY: "pm-old",
            },
        ),
        (
            None,
            PROVIDER_PETROMAP,
            {CONF_API_KEY: "legacy-tk"},
            {CONF_PETROMAP_API_KEY: "pm-new"},
            {
                CONF_TANKERKOENIG_API_KEY: "legacy-tk",
                CONF_PETROMAP_API_KEY: "pm-new",
            },
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
    if source in (PROVIDER_PETROMAP, PROVIDER_AUTO):
        source_data[CONF_PETROMAP_PRIVACY_ACCEPTED] = True
    entry = _entry(source_data)
    flow = _flow(entry)
    submitted = {
        key: value
        for key, value in {**_data(), CONF_PROVIDER_MODE: target}.items()
        if key
        not in {CONF_API_KEY, CONF_TANKERKOENIG_API_KEY, CONF_PETROMAP_API_KEY}
    }

    result = asyncio.run(flow.async_step_init(submitted))
    if target in (PROVIDER_PETROMAP, PROVIDER_AUTO) and not source_data.get(
        CONF_PETROMAP_PRIVACY_ACCEPTED, False
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
    if target in (PROVIDER_PETROMAP, PROVIDER_AUTO) or CONF_PETROMAP_API_KEY in expected:
        assert entry.data[CONF_PETROMAP_PRIVACY_ACCEPTED] is True
    assert not credential_keys.intersection(result["data"])
    assert entry.data[CONF_LOCATION_ENTITY] == "device_tracker.vehicle"
    assert result["data"][CONF_RADIUS] == 20.0
    assert entry.options[CONF_RADIUS] == 20.0


def test_options_reuses_known_inactive_provider_key_without_credential_form():
    entry = _entry(
        {
            **_data(),
            CONF_PROVIDER_MODE: PROVIDER_TANKERKOENIG,
            CONF_TANKERKOENIG_API_KEY: "tk-known",
            CONF_PETROMAP_API_KEY: "pm-known",
            CONF_PETROMAP_PRIVACY_ACCEPTED: True,
        }
    )
    flow = _flow(entry)
    result = asyncio.run(
        flow.async_step_init({**_data(), CONF_PROVIDER_MODE: PROVIDER_PETROMAP})
    )

    assert result["type"] == "create_entry"
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "tk-known"
    assert entry.data[CONF_PETROMAP_API_KEY] == "pm-known"
    assert CONF_API_KEY not in entry.data
    assert not {
        CONF_API_KEY,
        CONF_TANKERKOENIG_API_KEY,
        CONF_PETROMAP_API_KEY,
    }.intersection(entry.options)


def _run_provider_switch(entry, target, credentials=None):
    flow = _flow(entry)
    submitted = {**_data(), CONF_PROVIDER_MODE: target}
    result = asyncio.run(flow.async_step_init(submitted))
    if result["type"] == "form" and result["step_id"] == "options_petromap_privacy":
        result = asyncio.run(flow.async_step_options_petromap_privacy({}))
    if result["type"] == "form":
        result = asyncio.run(flow.async_step_provider_credentials(credentials or {}))
    assert result["type"] == "create_entry"
    return entry


@pytest.mark.parametrize(
    ("source", "first_target", "second_target", "initial", "first_credentials"),
    [
        (
            PROVIDER_TANKERKOENIG,
            PROVIDER_PETROMAP,
            PROVIDER_TANKERKOENIG,
            {CONF_API_KEY: "tk-sequence"},
            {CONF_PETROMAP_API_KEY: "pm-sequence"},
        ),
        (
            PROVIDER_PETROMAP,
            PROVIDER_TANKERKOENIG,
            PROVIDER_PETROMAP,
            {CONF_API_KEY: "pm-sequence", CONF_PETROMAP_PRIVACY_ACCEPTED: True},
            {CONF_TANKERKOENIG_API_KEY: "tk-sequence"},
        ),
        (
            PROVIDER_TANKERKOENIG,
            PROVIDER_AUTO,
            PROVIDER_TANKERKOENIG,
            {CONF_API_KEY: "tk-sequence"},
            {CONF_PETROMAP_API_KEY: "pm-sequence"},
        ),
        (
            PROVIDER_PETROMAP,
            PROVIDER_AUTO,
            PROVIDER_PETROMAP,
            {CONF_API_KEY: "pm-sequence", CONF_PETROMAP_PRIVACY_ACCEPTED: True},
            {CONF_TANKERKOENIG_API_KEY: "tk-sequence"},
        ),
        (
            PROVIDER_AUTO,
            PROVIDER_TANKERKOENIG,
            PROVIDER_AUTO,
            {
                CONF_TANKERKOENIG_API_KEY: "tk-sequence",
                CONF_PETROMAP_API_KEY: "pm-sequence",
                CONF_PETROMAP_PRIVACY_ACCEPTED: True,
            },
            {},
        ),
        (
            PROVIDER_AUTO,
            PROVIDER_PETROMAP,
            PROVIDER_AUTO,
            {
                CONF_TANKERKOENIG_API_KEY: "tk-sequence",
                CONF_PETROMAP_API_KEY: "pm-sequence",
                CONF_PETROMAP_PRIVACY_ACCEPTED: True,
            },
            {},
        ),
    ],
)
def test_provider_switch_sequences_reuse_both_known_credentials(
    source, first_target, second_target, initial, first_credentials
):
    entry = _entry({**_data(), **initial, CONF_PROVIDER_MODE: source})
    _run_provider_switch(entry, first_target, first_credentials)
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "tk-sequence"
    assert entry.data[CONF_PETROMAP_API_KEY] == "pm-sequence"
    assert entry.data[CONF_PETROMAP_PRIVACY_ACCEPTED] is True

    _run_provider_switch(entry, second_target)
    assert entry.data[CONF_PROVIDER_MODE] == second_target
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "tk-sequence"
    assert entry.data[CONF_PETROMAP_API_KEY] == "pm-sequence"
    assert not {
        CONF_API_KEY,
        CONF_TANKERKOENIG_API_KEY,
        CONF_PETROMAP_API_KEY,
    }.intersection(entry.options)


def test_legacy_migration_maps_generic_key_to_tankerkoenig_without_loss():
    entry = SimpleNamespace(
        version=1,
        data={CONF_API_KEY: "legacy-tk", CONF_LOCATION_ENTITY: "device_tracker.vehicle"},
    )
    updates = []

    def async_update_entry(current, *, data):
        updates.append(dict(data))
        current.data = dict(data)

    hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_update_entry=async_update_entry)
    )
    assert asyncio.run(integration.async_migrate_entry(hass, entry)) is True
    assert len(updates) == 1
    assert entry.data[CONF_PROVIDER_MODE] == PROVIDER_TANKERKOENIG
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "legacy-tk"
    assert CONF_API_KEY not in entry.data
    assert entry.data[CONF_LOCATION_ENTITY] == "device_tracker.vehicle"


def test_explicit_petromap_migration_sets_privacy_marker_and_preserves_data():
    entry = SimpleNamespace(
        version=1,
        data={
            CONF_API_KEY: "legacy-pm",
            CONF_PROVIDER_MODE: PROVIDER_PETROMAP,
            CONF_LOCATION_ENTITY: "device_tracker.vehicle",
        },
    )

    def async_update_entry(current, *, data):
        current.data = dict(data)

    hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_update_entry=async_update_entry)
    )
    assert asyncio.run(integration.async_migrate_entry(hass, entry)) is True
    assert entry.data[CONF_PETROMAP_API_KEY] == "legacy-pm"
    assert entry.data[CONF_PETROMAP_PRIVACY_ACCEPTED] is True
    assert CONF_API_KEY not in entry.data
    assert entry.data[CONF_LOCATION_ENTITY] == "device_tracker.vehicle"


def test_ambiguous_generic_key_is_retained_during_migration():
    entry = SimpleNamespace(
        version=1,
        data={
            CONF_API_KEY: "ambiguous",
            CONF_PROVIDER_MODE: PROVIDER_AUTO,
            CONF_TANKERKOENIG_API_KEY: "tk-known",
            CONF_PETROMAP_API_KEY: "pm-known",
        },
    )
    updates = []

    def async_update_entry(current, *, data):
        updates.append(dict(data))
        current.data = dict(data)

    hass = SimpleNamespace(
        config_entries=SimpleNamespace(async_update_entry=async_update_entry)
    )
    assert asyncio.run(integration.async_migrate_entry(hass, entry)) is True
    assert entry.data[CONF_API_KEY] == "ambiguous"
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "tk-known"
    assert entry.data[CONF_PETROMAP_API_KEY] == "pm-known"
    assert entry.data[CONF_PETROMAP_PRIVACY_ACCEPTED] is True
