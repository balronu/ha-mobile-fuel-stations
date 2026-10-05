import asyncio

import pytest

from mobile_fuel_stations.api import cheapest_station, nearest_station
from mobile_fuel_stations.providers.base import (
    ProviderAuthError,
    ProviderDailyBudgetError,
    ProviderDisabledError,
    ProviderInsufficientCreditsError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderUnavailableError,
    ProviderUnsupportedFuelError,
    StationSearchQuery,
)
from mobile_fuel_stations.providers.petromap import (
    PetromapProvider,
    build_search_request,
    map_error,
    parse_search_response,
)


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


def test_disabled_provider_contract_has_no_network_path():
    with pytest.raises(ProviderDisabledError):
        asyncio.run(PetromapProvider().async_search(StationSearchQuery(1, 1, 1, "diesel")))
