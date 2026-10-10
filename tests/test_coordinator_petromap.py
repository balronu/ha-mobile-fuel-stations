import asyncio
from types import SimpleNamespace

import pytest
from homeassistant.config_entries import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from mobile_fuel_stations import coordinator as coordinator_module
from mobile_fuel_stations.const import (
    CONF_FUEL_TYPE,
    CONF_LOCATION_ENTITY,
    CONF_PROVIDER_MODE,
    CONF_RADIUS,
    CONF_STATION_COUNT,
    PROVIDER_PETROMAP,
)
from mobile_fuel_stations.coordinator import MobileFuelStationsCoordinator
from mobile_fuel_stations.providers.base import (
    ProviderAuthError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderRequestDiagnostics,
    ProviderTimeoutError,
    ProviderUnavailableError,
    Station,
)
from mobile_fuel_stations.providers.petromap import PetromapProvider


class _Store:
    async def async_save(self, data):
        del data


class _Provider:
    def __init__(self, result=None, error=None):
        self.result = result if result is not None else []
        self.error = error
        self.calls = []

    async def async_search(self, query):
        self.calls.append(query)
        if self.error:
            raise self.error
        return self.result


def _coordinator(provider, fuel="diesel"):
    coordinator = object.__new__(MobileFuelStationsCoordinator)
    coordinator.hass = SimpleNamespace(data={})
    coordinator.entry = SimpleNamespace(
        entry_id="test-entry",
        async_start_reauth=lambda *args, **kwargs: None,
    )
    coordinator.options = {
        CONF_LOCATION_ENTITY: "device_tracker.vehicle",
        CONF_RADIUS: 25.0,
        CONF_FUEL_TYPE: fuel,
        CONF_STATION_COUNT: 3,
        CONF_PROVIDER_MODE: PROVIDER_PETROMAP,
    }
    coordinator.client = provider
    coordinator.stations = []
    coordinator.nearest_station = None
    coordinator.cheapest_station = None
    coordinator.last_successful_update = None
    coordinator.reference_position = None
    coordinator.last_request = None
    coordinator._store = _Store()
    coordinator.country_auto_context = SimpleNamespace(
        observe_position=lambda position: None
    )
    return coordinator


def _station():
    return Station(
        "petro-1", "Demo", "Petromap", 1.8, 1.0, True,
        "Street", "1", "12345", "Town", 49.2, 7.0,
    )


def test_petromap_diesel_refresh_uses_one_search_query(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    result = asyncio.run(coordinator._async_update_data())

    assert result == [_station()]
    assert len(provider.calls) == 1
    assert provider.calls[0].fuel_type == "diesel"
    assert provider.calls[0].latitude == 49.2
    assert provider.calls[0].longitude == 7.0


def test_petromap_e5_refresh_uses_one_search_query(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider, fuel="e5")
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    asyncio.run(coordinator._async_update_data())

    assert len(provider.calls) == 1
    assert provider.calls[0].fuel_type == "e5"


class _NoRequestSession:
    def __init__(self):
        self.calls = 0

    def get(self, *args, **kwargs):
        del args, kwargs
        self.calls += 1
        raise AssertionError("Petromap e10 must be rejected before HTTP")


def test_petromap_e10_uses_capability_declared_e5_fallback(monkeypatch):
    session = _NoRequestSession()
    coordinator = _coordinator(PetromapProvider(session, "dummy"), fuel="e10")
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    asyncio.run(coordinator._async_update_data())
    assert session.calls == 1


def test_petromap_401_requests_reauth(monkeypatch):
    provider = _Provider(error=ProviderAuthError("INVALID_CREDENTIAL"))
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    with pytest.raises(ConfigEntryAuthFailed):
        asyncio.run(coordinator._async_update_data())
    assert len(provider.calls) == 1


def test_petromap_rate_limit_keeps_last_valid_stations(monkeypatch):
    provider = _Provider([_station()])
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))
    asyncio.run(coordinator._async_update_data())
    previous = coordinator.stations

    provider.error = ProviderRateLimitError("RATE_LIMITED")
    with pytest.raises(UpdateFailed):
        asyncio.run(coordinator._async_update_data())

    assert coordinator.stations == previous
    assert len(provider.calls) == 2


def test_nakordoni_failure_metadata_is_published_before_update_failed(monkeypatch):
    provider = _Provider(error=ProviderRateLimitError("qps_exceeded"))
    provider.error.diagnostics = ProviderRequestDiagnostics(
        "nakordoni", 429, "qps_exceeded", 60, 1000, 999, False, False
    )
    coordinator = _coordinator(provider)
    coordinator.options[CONF_PROVIDER_MODE] = "nakordoni"
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    with pytest.raises(UpdateFailed, match="qps_exceeded"):
        asyncio.run(coordinator._async_update_data())

    assert coordinator.hass.data["mobile_fuel_stations"]["last_request_diagnostics"]["test-entry"] == {
        "provider": "nakordoni",
        "http_status": 429,
        "error_code": "qps_exceeded",
        "retry_after": 60,
        "quota_limit": 1000,
        "quota_remaining": 999,
        "request_success": False,
        "response_ok": False,
    }


@pytest.mark.parametrize(
    "error",
    [
        ProviderPermissionError("SCOPE_NOT_PERMITTED"),
        ProviderRateLimitError("RATE_LIMITED"),
        ProviderUnavailableError("ROUTING_UNAVAILABLE"),
        ProviderTimeoutError("timeout"),
        ProviderResponseError("malformed"),
    ],
)
def test_petromap_non_auth_failures_are_update_failures_without_provider_switch(
    monkeypatch, error
):
    provider = _Provider(error=error)
    coordinator = _coordinator(provider)
    monkeypatch.setattr(coordinator_module, "_valid_position", lambda *_: (49.2, 7.0))

    with pytest.raises(UpdateFailed):
        asyncio.run(coordinator._async_update_data())
    assert len(provider.calls) == 1
