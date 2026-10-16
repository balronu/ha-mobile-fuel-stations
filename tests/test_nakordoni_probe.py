import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mobile_fuel_stations.const import (
    CONF_NAKORDONI_API_KEY,
    CONF_NAKORDONI_AUTH_METHOD,
    CONF_PROVIDER_MODE,
    CONF_PROVIDER_MODES,
    DOMAIN,
    PROVIDER_AUTO,
    PROVIDER_NAKORDONI,
)
from mobile_fuel_stations.probe import (
    MAX_PROBE_CALLS,
    _configured_for_nakordoni,
    async_probe_nakordoni,
    async_register_probe_service,
)
from mobile_fuel_stations.providers.base import (
    ProviderNetworkError,
    ProviderRateLimitError,
    ProviderRequestDiagnostics,
    Station,
)


class FakeProvider:
    def __init__(self, stations=None, error=None, metadata=None):
        self.stations = stations or []
        self.error = error
        self.last_response_metadata = metadata
        self.last_request_diagnostics = ProviderRequestDiagnostics(
            "nakordoni", 200, None, 0, 100, 99, True, True
        )
        self.calls = []

    async def async_search(self, query):
        self.calls.append(query)
        if self.error:
            self.last_request_diagnostics = self.error.diagnostics
            raise self.error
        return self.stations


def entry(**data):
    return SimpleNamespace(
        entry_id="entry-1",
        domain=DOMAIN,
        data=data,
        options={},
        runtime_data=SimpleNamespace(
            stations=["untouched"],
            options={CONF_PROVIDER_MODE: PROVIDER_AUTO},
        ),
    )


def hass():
    return SimpleNamespace(data={})


def station(price=1.799, age=0.5):
    return Station(
        station_id="private-id", name="Private station", brand="Private brand",
        price=price, distance=1.2, is_open=True, street="Private street",
        house_number="1", postcode="66111", place="Saarbrücken", latitude=49.2,
        longitude=6.9, currency="EUR", price_age_hours=age,
        price_updated_at=datetime(2026, 10, 16, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_success_is_aggregated_without_station_identity_or_coordinates():
    provider = FakeProvider([station(), station(price=None, age=None)])
    result = await async_probe_nakordoni(
        hass(), entry(**{CONF_PROVIDER_MODE: PROVIDER_NAKORDONI, CONF_NAKORDONI_API_KEY: "SECRET"}),
        49.24, 6.99, 5, "diesel", provider=provider,
    )
    assert result["station_count"] == 2
    assert result["priced_station_count"] == 1
    assert result["price_coverage_percent"] == 50.0
    assert result["request_success"] is True
    assert "Private station" not in repr(result)
    assert "49.2" not in repr(result)
    assert "SECRET" not in repr(result)
    assert len(provider.calls) == 1


@pytest.mark.asyncio
async def test_empty_result_is_success_and_preserves_coverage_fields():
    metadata = SimpleNamespace(empty_reason="outside_coverage", nearest_station_km=31.4)
    provider = FakeProvider(metadata=metadata)
    result = await async_probe_nakordoni(
        hass(), entry(**{CONF_PROVIDER_MODES: [PROVIDER_NAKORDONI]}),
        49.24, 6.99, 25, "lpg", provider=provider,
    )
    assert result["request_success"] is True
    assert result["station_count"] == 0
    assert result["price_coverage_percent"] == 0.0
    assert result["empty_reason"] == "outside_coverage"
    assert result["nearest_station_km"] == 31.4


@pytest.mark.asyncio
async def test_rate_limit_returns_safe_diagnostics_without_retry():
    error = ProviderRateLimitError("private response")
    error.diagnostics = ProviderRequestDiagnostics(
        "nakordoni", 429, "qps_exceeded", 60, 100, 0, False, False
    )
    provider = FakeProvider(error=error)
    result = await async_probe_nakordoni(
        hass(), entry(**{CONF_PROVIDER_MODE: PROVIDER_NAKORDONI}),
        49.24, 6.99, 5, "e5", provider=provider,
    )
    assert result["error_code"] == "qps_exceeded"
    assert result["retry_after"] == 60
    assert len(provider.calls) == 1
    assert "private response" not in repr(result)


@pytest.mark.asyncio
async def test_network_error_is_sanitized():
    error = ProviderNetworkError("secret network detail")
    error.diagnostics = ProviderRequestDiagnostics(
        "nakordoni", None, "provider_error", None, None, None, False, None
    )
    provider = FakeProvider(error=error)
    result = await async_probe_nakordoni(
        hass(), entry(**{CONF_PROVIDER_MODE: PROVIDER_NAKORDONI}),
        49.24, 6.99, 5, "e10", provider=provider,
    )
    assert result["error_code"] == "provider_error"
    assert result["http_status"] is None
    assert "secret network detail" not in repr(result)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("latitude", "longitude", "radius", "fuel", "message"),
    [
        (91, 6.99, 5, "diesel", "coordinates"),
        (49.24, 181, 5, "diesel", "coordinates"),
        (49.24, 6.99, 0, "diesel", "radius"),
        (49.24, 6.99, 26, "diesel", "radius"),
        (49.24, 6.99, 5, "hvo100", "fuel_type"),
    ],
)
async def test_invalid_parameters_are_rejected(latitude, longitude, radius, fuel, message):
    with pytest.raises(ValueError, match=message):
        await async_probe_nakordoni(
            hass(), entry(**{CONF_PROVIDER_MODE: PROVIDER_NAKORDONI}),
            latitude, longitude, radius, fuel, provider=FakeProvider(),
        )


def test_nakordoni_configuration_detection_does_not_guess_auto_mode():
    assert _configured_for_nakordoni(entry(**{CONF_PROVIDER_MODE: PROVIDER_NAKORDONI}))
    assert _configured_for_nakordoni(entry(**{CONF_PROVIDER_MODES: [PROVIDER_NAKORDONI]}))
    assert not _configured_for_nakordoni(entry(**{CONF_PROVIDER_MODE: PROVIDER_AUTO}))
    assert not _configured_for_nakordoni(entry(**{"api_key": "legacy"}))


@pytest.mark.asyncio
async def test_api_key_and_oauth_configuration_is_not_mutated_or_returned():
    config = {
        CONF_PROVIDER_MODE: PROVIDER_NAKORDONI,
        CONF_PROVIDER_MODES: [PROVIDER_NAKORDONI],
        CONF_NAKORDONI_API_KEY: "SECRET",
        CONF_NAKORDONI_AUTH_METHOD: "oauth2",
    }
    test_entry = entry(**config)
    before = dict(test_entry.data)
    result = await async_probe_nakordoni(
        hass(), test_entry, 49.24, 6.99, 5, "diesel", provider=FakeProvider([station()])
    )
    assert test_entry.data == before
    assert "SECRET" not in repr(result)
    assert "oauth2" not in repr(result)


@pytest.mark.asyncio
async def test_probe_does_not_touch_coordinator_or_cache():
    test_hass = hass()
    test_hass.data[DOMAIN] = {"last_request_diagnostics": {"old": "value"}}
    test_entry = entry(**{CONF_PROVIDER_MODE: PROVIDER_NAKORDONI})
    before_runtime = repr(test_entry.runtime_data)
    await async_probe_nakordoni(
        test_hass, test_entry, 49.24, 6.99, 5, "diesel", provider=FakeProvider([station()])
    )
    assert repr(test_entry.runtime_data) == before_runtime
    assert test_hass.data[DOMAIN] == {"last_request_diagnostics": {"old": "value"}}


def test_probe_budget_is_bounded_and_no_retry_contract_is_explicit():
    assert MAX_PROBE_CALLS == 3


@pytest.mark.asyncio
async def test_service_requires_admin_and_returns_only_probe_response():
    registered = {}
    test_entry = entry(**{CONF_PROVIDER_MODE: PROVIDER_NAKORDONI})
    test_hass = SimpleNamespace(
        data={},
        services=SimpleNamespace(async_register=lambda domain, name, handler, **kwargs: registered.update(
            {"handler": handler, "domain": domain, "name": name, "kwargs": kwargs}
        )),
        auth=SimpleNamespace(async_get_user=AsyncMock(return_value=SimpleNamespace(is_admin=True))),
        config_entries=SimpleNamespace(async_get_entry=lambda entry_id: test_entry),
    )
    await async_register_probe_service(test_hass)
    assert registered["domain"] == DOMAIN
    assert registered["name"] == "probe_nakordoni"
    assert registered["kwargs"]["supports_response"].value == "only"
    call = SimpleNamespace(
        context=SimpleNamespace(user_id="admin"),
        data={"entry_id": "entry-1", "latitude": 49.24, "longitude": 6.99, "radius_km": 5, "fuel_type": "diesel"},
    )
    with patch("mobile_fuel_stations.probe.async_probe_nakordoni", new=AsyncMock(return_value={"ok": True})) as probe:
        assert await registered["handler"](call) == {"ok": True}
        probe.assert_awaited_once()
    test_hass.auth.async_get_user.return_value = SimpleNamespace(is_admin=False)
    with pytest.raises(Exception, match="Administrator"):
        await registered["handler"](call)
