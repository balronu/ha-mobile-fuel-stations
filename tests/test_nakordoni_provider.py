import asyncio

import pytest

from mobile_fuel_stations.const import CONF_NAKORDONI_API_KEY, CONF_PROVIDER_MODE, PROVIDER_NAKORDONI
from mobile_fuel_stations.providers import PROVIDER_REGISTRY, create_provider
from mobile_fuel_stations.providers.base import (
    ProviderAuthError,
    ProviderConfigurationError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderUnsupportedFuelError,
    StationSearchQuery,
)
from mobile_fuel_stations.providers.nakordoni import NakordoniProvider, NAKORDONI_API_URL


class Response:
    def __init__(self, payload, status=200, headers=None):
        self.status = status
        self.payload = payload
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def json(self, content_type=None):
        return self.payload


class Session:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, *, params, headers, timeout):
        self.calls.append((url, params, headers, timeout))
        return self.response


def payload():
    return {
        "ok": True,
        "data": {
            "count": 1,
            "total_found": 1,
            "stations": [{
                "station_ref": "stable-ref",
                "id": None,
                "name": "Test Station",
                "brand": None,
                "address": {"street": "Example Street", "city": "Saarbrücken"},
                "lat": 49.24,
                "lng": 6.99,
                "distance_km": 1.2,
                "prices": {"diesel": {
                    "price": 1.799,
                    "currency": "EUR",
                    "updated_at": "2026-10-06T20:00:00Z",
                    "confirmed_at": "2026-10-06T20:30:00Z",
                    "age_hours": 0.5,
                    "stale": False,
                }},
            }],
        },
    }


def query():
    return StationSearchQuery(49.24, 6.99, 25, "diesel", station_count=10)


def test_registry_and_factory_are_enabled_without_network():
    session = Session(Response(payload()))
    provider = create_provider(session, {
        CONF_PROVIDER_MODE: PROVIDER_NAKORDONI,
        CONF_NAKORDONI_API_KEY: "nakordoni-dummy",
    })
    assert isinstance(provider, NakordoniProvider)
    assert PROVIDER_REGISTRY[PROVIDER_NAKORDONI].enabled is True
    assert session.calls == []


def test_nakordoni_never_falls_back_to_generic_legacy_key():
    with pytest.raises(ProviderConfigurationError):
        create_provider(Session(Response(payload())), {
            CONF_PROVIDER_MODE: PROVIDER_NAKORDONI,
            "api_key": "legacy-tankerkoenig-dummy",
        })


def test_nakordoni_request_uses_bearer_header_and_one_page():
    session = Session(Response(payload(), headers={"X-Devapi-Limit": "1000", "X-Devapi-Remaining": "999"}))
    provider = NakordoniProvider(session, "nakordoni-dummy")
    stations = asyncio.run(provider.async_search(query()))
    url, params, headers, _ = session.calls[0]
    assert len(session.calls) == 1
    assert url == NAKORDONI_API_URL
    assert params == {"lat": "49.2400000", "lon": "6.9900000", "radius_km": "25", "fuel_type": "diesel", "limit": "10", "lang": "de"}
    assert headers == {"Authorization": "Bearer nakordoni-dummy"}
    assert stations[0].station_id == "stable-ref"
    assert stations[0].brand == ""
    assert stations[0].price == 1.799
    assert stations[0].price_stale is False
    assert provider.last_response_metadata.quota_remaining == 999


@pytest.mark.parametrize("status, error_type", [(401, ProviderAuthError), (403, ProviderPermissionError), (429, ProviderRateLimitError)])
def test_nakordoni_http_errors_are_classified(status, error_type):
    provider = NakordoniProvider(Session(Response({"ok": False, "error": {"code": "provider_error"}}, status=status)), "dummy")
    with pytest.raises(error_type):
        asyncio.run(provider.async_search(query()))


def test_nakordoni_rejects_unverified_fuels_without_network():
    session = Session(Response(payload()))
    provider = NakordoniProvider(session, "dummy")
    with pytest.raises(ProviderUnsupportedFuelError, match="not verified"):
        asyncio.run(provider.async_search(StationSearchQuery(49.24, 6.99, 25, "hvo100")))
    assert session.calls == []
