import asyncio
import json

import aiohttp
import pytest

from mobile_fuel_stations.api import cheapest_station, nearest_station
from mobile_fuel_stations.providers.base import (
    ProviderAuthError,
    ProviderDailyBudgetError,
    ProviderDisabledError,
    ProviderInsufficientCreditsError,
    ProviderNetworkError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderUnavailableError,
    ProviderUnsupportedFuelError,
    ProviderTimeoutError,
    StationSearchQuery,
)
from mobile_fuel_stations.providers import create_provider
from mobile_fuel_stations.providers.petromap import (
    PetromapProvider,
    build_search_request,
    map_error,
    parse_search_response,
)


class _FakeResponse:
    def __init__(self, status=200, payload=None, headers=None, json_error=None):
        self.status = status
        self._payload = payload
        self.headers = headers or {}
        self._json_error = json_error

    async def json(self, *, content_type=None):
        del content_type
        if self._json_error:
            raise self._json_error
        return self._payload


class _FakeRequest:
    def __init__(self, response=None, enter_error=None):
        self.response = response
        self.enter_error = enter_error

    async def __aenter__(self):
        if self.enter_error:
            raise self.enter_error
        return self.response

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class _FakeSession:
    def __init__(self, response=None, enter_error=None):
        self.response = response
        self.enter_error = enter_error
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _FakeRequest(self.response, self.enter_error)


def _place(**overrides):
    place = {
        "id": "DE_DEMO_1",
        "kind": "fuel",
        "country": "DE",
        "city": "Saarbruecken",
        "street": "Example Street 1",
        "postalCode": "66111",
        "name": "Demo Station",
        "location": {"lat": 49.24, "lon": 6.99},
        "distanceM": 1400,
        "openNow": True,
        "network": {"id": "DE_DEMO", "name": "Demo", "group": "demo"},
        "fuel": {
            "token": "diesel_b7",
            "family": "diesel",
            "grade": "standard",
            "price": {"amount": 1.799, "currency": "EUR", "updatedAt": "2026-10-05T10:00:00Z"},
        },
    }
    place.update(overrides)
    return place


def test_request_builder_uses_lon_lat_meters_and_verified_diesel_mapping():
    request = build_search_request(
        StationSearchQuery(49.24, 6.99, 25.0, "diesel")
    )

    assert request.url == "https://api.petromap.eu/v2/places"
    assert request.params == {
        "filter": "circle:6.99,49.24,25000",
        "fuelFamily": "diesel",
    }


def test_request_builder_maps_e5_and_rejects_unverified_e10():
    request = build_search_request(StationSearchQuery(48.2, 16.3, 1.0, "e5"))
    assert request.params["fuel"] == "petrol_95_e5"

    with pytest.raises(ProviderUnsupportedFuelError):
        build_search_request(StationSearchQuery(48.2, 16.3, 1.0, "e10"))


def test_request_builder_preserves_25_km_integration_cap():
    with pytest.raises(ProviderResponseError):
        build_search_request(StationSearchQuery(49.2, 7.0, 25.1, "diesel"))


def test_parser_normalizes_station_and_cursor_without_pagination():
    result = parse_search_response(
        {"places": [_place()], "nextCursor": "next-page", "credits": 1}
    )

    station = result.stations[0]
    assert result.next_cursor == "next-page"
    assert result.credits == 1
    assert station.station_id == "DE_DEMO_1"
    assert station.brand == "Demo"
    assert station.distance == 1.4
    assert station.currency == "EUR"
    assert station.country_code == "DE"
    assert station.price_updated_at is not None
    assert station.price_updated_at.isoformat() == "2026-10-05T10:00:00+00:00"
    assert station.is_open is True


def test_parser_handles_austrian_station_and_optional_values():
    result = parse_search_response(
        {
            "places": [
                _place(
                    id="AT_DEMO_1",
                    country="AT",
                    openNow=None,
                    network=None,
                    street=None,
                    postalCode=None,
                    fuel=None,
                )
            ]
        }
    )

    station = result.stations[0]
    assert station.country_code == "AT"
    assert station.price is None
    assert station.price_updated_at is None
    assert station.is_open is None
    assert station.brand == ""


def test_parser_accepts_iso_offset_and_invalid_timestamp_is_unavailable():
    offset_result = parse_search_response(
        {"places": [_place(fuel={"price": {"amount": 1.8, "updatedAt": "2026-10-05T12:00:00+02:00"}})]}
    )
    assert offset_result.stations[0].price_updated_at is not None
    assert offset_result.stations[0].price_updated_at.isoformat() == "2026-10-05T12:00:00+02:00"

    null_result = parse_search_response(
        {"places": [_place(fuel={"price": {"amount": 1.8, "updatedAt": None}})]}
    )
    assert null_result.stations[0].price_updated_at is None

    invalid_result = parse_search_response(
        {"places": [_place(fuel={"price": {"amount": 1.8, "updatedAt": "not-a-timestamp"}})]}
    )
    assert invalid_result.stations[0].price_updated_at is None


def test_parser_rejects_invalid_required_data():
    with pytest.raises(ProviderResponseError):
        parse_search_response({"places": [_place(location={"lat": "bad", "lon": 7.0})]})
    with pytest.raises(ProviderResponseError):
        parse_search_response({"places": [_place(id="")]})


def test_unknown_open_state_and_missing_price_cannot_be_selected():
    result = parse_search_response(
        {
            "places": [
                _place(id="unknown", openNow=None, fuel=None),
                _place(id="closed", openNow=False),
            ]
        }
    )

    assert nearest_station(result.stations) is None
    assert cheapest_station(result.stations) is None


@pytest.mark.parametrize(
    ("status", "code", "exception"),
    [
        (401, "INVALID_CREDENTIAL", ProviderAuthError),
        (403, "SCOPE_NOT_PERMITTED", ProviderPermissionError),
        (429, "RATE_LIMITED", ProviderRateLimitError),
        (429, "DAILY_BUDGET_EXHAUSTED", ProviderDailyBudgetError),
        (429, "INSUFFICIENT_CREDITS", ProviderInsufficientCreditsError),
        (503, "CURRENCY_UNAVAILABLE", ProviderUnavailableError),
    ],
)
def test_documented_errors_map_to_provider_errors(status, code, exception):
    assert isinstance(map_error(status, {"error": code}), exception)


def _query(fuel_type="diesel"):
    return StationSearchQuery(49.24, 6.99, 25.0, fuel_type)


def test_transport_diesel_uses_one_request_and_injected_key_without_pagination():
    session = _FakeSession(
        _FakeResponse(
            payload={"places": [_place()], "nextCursor": "next", "credits": 1},
            headers={
                "X-Credits-Charged": "1",
                "X-Credits-Remaining": "249",
                "X-RateLimit-Limit": "1000",
            },
        )
    )
    provider = PetromapProvider(session, "dummy-r2e2-key")

    stations = asyncio.run(provider.async_search(_query()))

    assert len(stations) == 1
    assert len(session.calls) == 1
    url, kwargs = session.calls[0]
    assert url == "https://api.petromap.eu/v2/places"
    assert kwargs["headers"] == {"x-api-key": "dummy-r2e2-key"}
    assert kwargs["params"] == {
        "filter": "circle:6.99,49.24,25000",
        "fuelFamily": "diesel",
    }
    assert "sort" not in kwargs["params"]
    assert "cursor" not in kwargs["params"]
    assert provider.last_response_metadata is not None
    assert provider.last_response_metadata.next_cursor == "next"
    assert provider.last_response_metadata.body_credits == 1
    assert provider.last_response_metadata.credits_charged == 1
    assert provider.last_response_metadata.credits_remaining == 249
    assert provider.last_response_metadata.rate_limit == 1000


def test_transport_e5_uses_super_95_token():
    session = _FakeSession(_FakeResponse(payload={"places": []}))
    provider = PetromapProvider(session, "dummy-key")

    asyncio.run(provider.async_search(_query("e5")))

    assert len(session.calls) == 1
    assert session.calls[0][1]["params"]["fuel"] == "petrol_95_e5"
    assert "petrol_98_e5" not in session.calls[0][1]["params"].values()
    assert "fuelFamily" not in session.calls[0][1]["params"]


def test_transport_rejects_e10_before_network():
    session = _FakeSession(_FakeResponse(payload={"places": []}))
    provider = PetromapProvider(session, "dummy-key")

    with pytest.raises(ProviderUnsupportedFuelError):
        asyncio.run(provider.async_search(_query("e10")))
    assert session.calls == []


@pytest.mark.parametrize(
    ("status", "code", "exception"),
    [
        (400, "INVALID_QUERY", ProviderResponseError),
        (401, "INVALID_CREDENTIAL", ProviderAuthError),
        (403, "SCOPE_NOT_PERMITTED", ProviderPermissionError),
        (404, "PLACE_NOT_FOUND", ProviderResponseError),
        (429, "RATE_LIMITED", ProviderRateLimitError),
        (429, "DAILY_BUDGET_EXHAUSTED", ProviderDailyBudgetError),
        (429, "INSUFFICIENT_CREDITS", ProviderInsufficientCreditsError),
        (503, "ROUTING_UNAVAILABLE", ProviderUnavailableError),
        (503, "CURRENCY_UNAVAILABLE", ProviderUnavailableError),
    ],
)
def test_transport_maps_http_errors_without_retry(status, code, exception):
    session = _FakeSession(_FakeResponse(status=status, payload={"error": code}))
    provider = PetromapProvider(session, "dummy-secret-key")

    with pytest.raises(exception) as caught:
        asyncio.run(provider.async_search(_query()))

    assert len(session.calls) == 1
    assert "dummy-secret-key" not in str(caught.value)


def test_transport_records_retry_after_without_sleep_or_retry():
    session = _FakeSession(
        _FakeResponse(
            status=429,
            payload={"error": "RATE_LIMITED"},
            headers={"Retry-After": "7"},
        )
    )
    provider = PetromapProvider(session, "dummy-key")

    with pytest.raises(ProviderRateLimitError):
        asyncio.run(provider.async_search(_query()))

    assert len(session.calls) == 1
    assert provider.last_response_metadata is not None
    assert provider.last_response_metadata.retry_after == 7


def test_transport_maps_timeout_and_connection_errors_without_retry():
    timeout_session = _FakeSession(enter_error=asyncio.TimeoutError())
    with pytest.raises(ProviderTimeoutError):
        asyncio.run(PetromapProvider(timeout_session, "dummy").async_search(_query()))
    assert len(timeout_session.calls) == 1

    connection_session = _FakeSession(enter_error=aiohttp.ClientConnectionError())
    with pytest.raises(ProviderNetworkError):
        asyncio.run(PetromapProvider(connection_session, "dummy").async_search(_query()))
    assert len(connection_session.calls) == 1


def test_transport_maps_invalid_json_to_response_error():
    session = _FakeSession(
        _FakeResponse(json_error=json.JSONDecodeError("bad", "{}", 0))
    )
    with pytest.raises(ProviderResponseError):
        asyncio.run(PetromapProvider(session, "dummy").async_search(_query()))
    assert len(session.calls) == 1


def test_transport_does_not_swallow_unexpected_programming_error():
    session = _FakeSession(_FakeResponse(json_error=RuntimeError("programming bug")))
    with pytest.raises(RuntimeError, match="programming bug"):
        asyncio.run(PetromapProvider(session, "dummy").async_search(_query()))


def test_transport_allows_optional_headers_to_be_missing_or_invalid():
    session = _FakeSession(
        _FakeResponse(
            payload={"places": []},
            headers={"X-Credits-Charged": "not-a-number", "Retry-After": "-1"},
        )
    )
    provider = PetromapProvider(session, "dummy")

    assert asyncio.run(provider.async_search(_query())) == []
    assert provider.last_response_metadata is not None
    assert provider.last_response_metadata.credits_charged is None
    assert provider.last_response_metadata.retry_after is None


def test_registry_keeps_petromap_disabled_before_network():
    with pytest.raises(ProviderDisabledError):
        create_provider(object(), {"provider_mode": "petromap", "api_key": "dummy"})
