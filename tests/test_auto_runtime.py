"""Focused Auto runtime regression tests."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.config_entries import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

import mobile_fuel_stations as integration
from mobile_fuel_stations import coordinator as coordinator_module
from mobile_fuel_stations.const import (
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_PETROMAP_API_KEY,
    CONF_PROVIDER_MODE,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    CONF_TANKERKOENIG_API_KEY,
    PROVIDER_AUTO,
    PROVIDER_PETROMAP,
    PROVIDER_TANKERKOENIG,
)
from mobile_fuel_stations.coordinator import CountryAutoContext, MobileFuelStationsCoordinator
from mobile_fuel_stations.providers import ProviderRegistration, PROVIDER_REGISTRY
from mobile_fuel_stations.providers.base import (
    CountryPriceCoverage,
    FuelFallbackBlockedError,
    NoSuitableProviderError,
    ProviderAuthError,
    ProviderCapabilities,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    Station,
)
from mobile_fuel_stations.providers.petromap import PETROMAP_CAPABILITIES


class _Store:
    async def async_save(self, data):
        del data


class _Provider:
    def __init__(self, key, session, result=None, error=None):
        self.key = key
        self.session = session
        self.result = result or []
        self.error = error
        self.calls = []
        self.places_calls = 0
        self.usage_calls = 0

    async def async_search(self, query):
        self.calls.append(query)
        self.places_calls += 1
        if self.error:
            raise self.error
        return self.result

    async def async_usage(self):
        self.usage_calls += 1


async def _async_executor(func, *args):
    return func(*args)


def _assert_runtime_usage_zero(pm):
    """Runtime refreshes must never perform credential validation."""

    assert pm.usage_calls == 0


def _station(station_id="station-1"):
    return Station(
        station_id, "Demo", "Brand", 1.8, 1.0, True,
        "Street", "1", "12345", "Town", 49.2, 7.0,
    )


def _coordinator(monkeypatch, country, fuel="diesel", *, tk_error=None, pm_error=None):
    session = object()
    tk = _Provider("TK_SECRET_ONLY", session, [_station("tk")], tk_error)
    pm = _Provider("PM_SECRET_ONLY", session, [_station("pm")], pm_error)
    factory_keys = {}
    def make_tk(shared, key):
        factory_keys[PROVIDER_TANKERKOENIG] = (shared, key)
        return tk
    def make_pm(shared, key):
        factory_keys[PROVIDER_PETROMAP] = (shared, key)
        return pm
    monkeypatch.setitem(
        PROVIDER_REGISTRY,
        PROVIDER_TANKERKOENIG,
        ProviderRegistration(
            PROVIDER_TANKERKOENIG,
            make_tk,
            True,
            ProviderCapabilities(
                supported_countries=frozenset({"DE"}),
                supported_fuel_types=frozenset({"diesel", "e5", "e10"}),
                country_price_coverage={"DE": CountryPriceCoverage.PER_STATION},
            ),
        ),
    )
    monkeypatch.setitem(
        PROVIDER_REGISTRY,
        PROVIDER_PETROMAP,
        ProviderRegistration(
            PROVIDER_PETROMAP,
            make_pm,
            True,
            PETROMAP_CAPABILITIES,
        ),
    )
    entry = SimpleNamespace(
        entry_id="test-auto-entry",
        data={CONF_PROVIDER_MODE: PROVIDER_AUTO},
        async_start_reauth=Mock(),
    )
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator.hass = object()
    coordinator.entry = entry
    coordinator.options = {
        CONF_PROVIDER_MODE: PROVIDER_AUTO,
        CONF_LOCATION_ENTITY: "device_tracker.vehicle",
        CONF_RADIUS: 20.0,
        CONF_FUEL_TYPE: fuel,
        CONF_STATION_COUNT: 3,
        CONF_TANKERKOENIG_API_KEY: "TK_SECRET_ONLY",
        CONF_PETROMAP_API_KEY: "PM_SECRET_ONLY",
    }
    coordinator._session = session
    coordinator._providers = {}
    coordinator.client = None
    coordinator.stations = []
    coordinator.nearest_station = None
    coordinator.cheapest_station = None
    coordinator.last_successful_update = None
    coordinator.reference_position = None
    coordinator.last_request = None
    coordinator._store = _Store()
    coordinator.auto_runtime_state = None
    coordinator.factory_keys = factory_keys
    coordinator.country_auto_context = CountryAutoContext(
        fuel, resolver=lambda lat, lon: country() if callable(country) else country
    )
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))
    return coordinator, tk, pm


@pytest.mark.parametrize("fuel", ["diesel", "e5", "e10"])
def test_auto_de_uses_tankerkoenig_once_and_routes_secret(monkeypatch, fuel):
    coordinator, tk, pm = _coordinator(monkeypatch, "DE", fuel)

    result = asyncio.run(coordinator._async_update_data())

    assert result == [_station("tk")]
    assert len(tk.calls) == 1
    assert not pm.calls
    assert tk.key == "TK_SECRET_ONLY"
    assert coordinator.factory_keys[PROVIDER_TANKERKOENIG][1] == "TK_SECRET_ONLY"
    assert PROVIDER_PETROMAP not in coordinator.factory_keys
    assert tk.calls[0].fuel_type == fuel
    assert coordinator.auto_runtime_state.effective_provider == PROVIDER_TANKERKOENIG
    _assert_runtime_usage_zero(pm)


@pytest.mark.parametrize("fuel", ["diesel", "e5"])
def test_auto_at_uses_petromap_once_and_routes_secret(monkeypatch, fuel):
    coordinator, tk, pm = _coordinator(monkeypatch, "AT", fuel)

    asyncio.run(coordinator._async_update_data())

    assert not tk.calls
    assert pm.places_calls == 1
    assert pm.key == "PM_SECRET_ONLY"
    assert coordinator.factory_keys[PROVIDER_PETROMAP][1] == "PM_SECRET_ONLY"
    assert PROVIDER_TANKERKOENIG not in coordinator.factory_keys
    assert pm.calls[0].fuel_type == fuel
    assert coordinator.auto_runtime_state.effective_provider == PROVIDER_PETROMAP
    _assert_runtime_usage_zero(pm)


def test_auto_at_e10_uses_capability_declared_e5_fallback(monkeypatch):
    coordinator, tk, pm = _coordinator(monkeypatch, "AT", "e10")

    asyncio.run(coordinator._async_update_data())

    assert not tk.calls and len(pm.calls) == 1
    assert pm.calls[0].fuel_type == "e5"
    assert coordinator.auto_runtime_state.effective_provider == PROVIDER_PETROMAP
    assert coordinator.auto_runtime_state.fuel_resolution.fallback_used is True
    _assert_runtime_usage_zero(pm)


def test_auto_e10_border_preserves_last_valid_data_after_confirmed_at(monkeypatch):
    samples = iter(["DE", "AT", "AT", "AT"])
    coordinator, tk, pm = _coordinator(monkeypatch, lambda: next(samples), "e10")
    asyncio.run(coordinator._async_update_data())
    previous = list(coordinator.stations)

    for _ in range(2):
        asyncio.run(coordinator._async_update_data())
    asyncio.run(coordinator._async_update_data())

    assert coordinator.stations != previous
    assert coordinator.auto_runtime_state.confirmed_country == "AT"
    assert coordinator.auto_runtime_state.effective_provider == PROVIDER_PETROMAP
    _assert_runtime_usage_zero(pm)
    assert coordinator.auto_runtime_state.fuel_resolution.effective_fuel == "e5"
    assert coordinator.auto_runtime_state.fuel_resolution.fallback_used is True
    assert len(tk.calls) == 3
    assert len(pm.calls) == 1


@pytest.mark.parametrize("country", ["BG", "PL", "SK", "ME", "RS", "FR", None])
def test_auto_unsupported_coverage_is_mobile_unavailable_without_requests(monkeypatch, country):
    coordinator, tk, pm = _coordinator(monkeypatch, country)

    with pytest.raises(UpdateFailed) as caught:
        asyncio.run(coordinator._async_update_data())

    assert isinstance(caught.value.__cause__, NoSuitableProviderError)
    assert not tk.calls and not pm.calls
    assert coordinator.auto_runtime_state.effective_provider is None
    _assert_runtime_usage_zero(pm)


def test_auto_hysteresis_de_to_at_switches_only_on_third_sample(monkeypatch):
    samples = iter(["DE", "AT", "AT", "AT"])
    coordinator, tk, pm = _coordinator(monkeypatch, lambda: next(samples), "e5")

    for expected in [PROVIDER_TANKERKOENIG, PROVIDER_TANKERKOENIG, PROVIDER_TANKERKOENIG, PROVIDER_PETROMAP]:
        asyncio.run(coordinator._async_update_data())
        assert coordinator.auto_runtime_state.effective_provider == expected

    assert len(tk.calls) == 3
    assert len(pm.calls) == 1
    _assert_runtime_usage_zero(pm)


def test_auto_hysteresis_at_to_de_switches_only_on_third_sample(monkeypatch):
    samples = iter(["AT", "DE", "DE", "DE"])
    coordinator, tk, pm = _coordinator(monkeypatch, lambda: next(samples), "e5")

    for expected in [PROVIDER_PETROMAP, PROVIDER_PETROMAP, PROVIDER_PETROMAP, PROVIDER_TANKERKOENIG]:
        asyncio.run(coordinator._async_update_data())
        assert coordinator.auto_runtime_state.effective_provider == expected

    assert len(pm.calls) == 3
    assert len(tk.calls) == 1
    _assert_runtime_usage_zero(pm)


def test_auto_cache_reuses_concrete_instances_and_shared_session(monkeypatch):
    samples = iter(["DE", "DE", "AT", "AT", "AT", "AT"])
    coordinator, tk, pm = _coordinator(monkeypatch, lambda: next(samples), "e5")

    for _ in range(6):
        asyncio.run(coordinator._async_update_data())

    assert coordinator._providers == {
        PROVIDER_TANKERKOENIG: tk,
        PROVIDER_PETROMAP: pm,
    }
    assert tk.session is coordinator._session
    assert pm.session is coordinator._session
    assert coordinator.factory_keys[PROVIDER_TANKERKOENIG][1] == "TK_SECRET_ONLY"
    assert coordinator.factory_keys[PROVIDER_PETROMAP][1] == "PM_SECRET_ONLY"
    _assert_runtime_usage_zero(pm)


def test_auto_pm_failure_preserves_last_valid_data_without_tk_fallback(monkeypatch):
    samples = iter(["DE", "AT", "AT", "AT"])
    coordinator, tk, pm = _coordinator(
        monkeypatch, lambda: next(samples), "e5", pm_error=ProviderTimeoutError("timeout")
    )
    asyncio.run(coordinator._async_update_data())
    asyncio.run(coordinator._async_update_data())
    asyncio.run(coordinator._async_update_data())
    previous = coordinator.stations

    with pytest.raises(UpdateFailed):
        asyncio.run(coordinator._async_update_data())

    assert coordinator.stations == previous
    assert len(tk.calls) == 3
    assert len(pm.calls) == 1
    assert coordinator.auto_runtime_state.effective_provider == PROVIDER_PETROMAP
    _assert_runtime_usage_zero(pm)


def test_auto_pm_401_starts_provider_specific_reauth(monkeypatch):
    coordinator, tk, pm = _coordinator(
        monkeypatch, "AT", "e5", pm_error=ProviderAuthError("INVALID_CREDENTIAL")
    )

    with pytest.raises(ConfigEntryAuthFailed):
        asyncio.run(coordinator._async_update_data())

    coordinator.entry.async_start_reauth.assert_called_once_with(
        coordinator.hass, context={"provider_mode": PROVIDER_PETROMAP}
    )
    assert not tk.calls and pm.places_calls == 1
    _assert_runtime_usage_zero(pm)


@pytest.mark.parametrize(
    "error",
    [ProviderPermissionError("403"), ProviderRateLimitError("429"), ProviderUnavailableError("503"), ProviderTimeoutError("timeout")],
)
def test_auto_pm_non_auth_failures_do_not_reauth_or_fallback(monkeypatch, error):
    coordinator, tk, pm = _coordinator(monkeypatch, "AT", "e5", pm_error=error)

    with pytest.raises(UpdateFailed):
        asyncio.run(coordinator._async_update_data())

    coordinator.entry.async_start_reauth.assert_not_called()
    assert not tk.calls and len(pm.calls) == 1
    _assert_runtime_usage_zero(pm)


def test_auto_reauth_form_updates_only_petromap_key(monkeypatch):
    from mobile_fuel_stations.config_flow import MobileFuelStationsConfigFlow

    flow = MobileFuelStationsConfigFlow()
    flow.context = {"provider_mode": PROVIDER_PETROMAP}
    entry = SimpleNamespace(
        data={
            CONF_PROVIDER_MODE: PROVIDER_AUTO,
            CONF_TANKERKOENIG_API_KEY: "TK_OLD",
            CONF_PETROMAP_API_KEY: "PM_OLD",
        }
    )
    flow._get_reauth_entry = lambda: entry
    flow._validate_petromap_key = Mock(side_effect=lambda key: asyncio.sleep(0, result=None))
    flow.async_update_reload_and_abort = lambda current, **kwargs: {"type": "abort", **kwargs}
    result = asyncio.run(flow.async_step_reauth(entry.data))
    assert result["step_id"] == "reauth_auto_confirm"
    schema_keys = {getattr(key, "schema", key) for key in result["data_schema"].schema}
    assert schema_keys == {CONF_PETROMAP_API_KEY}
    result = asyncio.run(flow.async_step_reauth_auto_confirm({CONF_PETROMAP_API_KEY: "PM_NEW"}))
    assert result["data_updates"] == {CONF_PETROMAP_API_KEY: "PM_NEW"}
    assert entry.data[CONF_TANKERKOENIG_API_KEY] == "TK_OLD"


@pytest.mark.parametrize("expected", [NoSuitableProviderError("unknown"), FuelFallbackBlockedError("fallback")])
def test_first_refresh_expected_auto_state_is_accepted(monkeypatch, expected):
    class _Coordinator:
        def __init__(self, hass, entry):
            del hass, entry

        async def async_setup(self):
            pass

        async def async_config_entry_first_refresh(self):
            try:
                raise UpdateFailed("mobile") from expected
            except UpdateFailed as update_error:
                raise integration.ConfigEntryNotReady("mobile") from update_error

    entry = SimpleNamespace(
        entry_id="test-auto-entry",
        data={CONF_PROVIDER_MODE: PROVIDER_AUTO},
        options={},
        runtime_data=None,
        add_update_listener=lambda listener: listener,
        async_on_unload=lambda unsubscribe: None,
    )
    hass = SimpleNamespace(
        data={},
        async_add_executor_job=_async_executor,
        config_entries=SimpleNamespace(async_forward_entry_setups=AsyncMock()),
    )
    monkeypatch.setattr(integration, "MobileFuelStationsCoordinator", _Coordinator)
    assert asyncio.run(integration.async_setup_entry(hass, entry)) is True
    hass.config_entries.async_forward_entry_setups.assert_awaited_once()


def test_first_refresh_real_network_failure_is_not_swallowed(monkeypatch):
    class _Coordinator:
        def __init__(self, hass, entry):
            del hass, entry

        async def async_setup(self):
            pass

        async def async_config_entry_first_refresh(self):
            raise integration.ConfigEntryNotReady("network") from UpdateFailed("network")

    entry = SimpleNamespace(
        entry_id="test-auto-entry",
        data={CONF_PROVIDER_MODE: PROVIDER_AUTO},
        options={},
        runtime_data=None,
    )
    hass = SimpleNamespace(
        data={},
        async_add_executor_job=_async_executor,
        config_entries=SimpleNamespace(async_forward_entry_setups=AsyncMock()),
    )
    monkeypatch.setattr(integration, "MobileFuelStationsCoordinator", _Coordinator)
    with pytest.raises(integration.ConfigEntryNotReady):
        asyncio.run(integration.async_setup_entry(hass, entry))
