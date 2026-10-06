"""Petromap v2 contract and injected-session transport helpers.

The provider remains disabled in the registry until credentials, licensing,
and budget policy are approved.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Any

from aiohttp import ClientConnectionError, ClientError, ClientSession, ClientTimeout

from ..const import DEFAULT_TIMEOUT, MAX_API_RADIUS_KM
from .base import (
    ProviderAuthError,
    ProviderDailyBudgetError,
    ProviderInsufficientCreditsError,
    ProviderNetworkError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderUnsupportedFuelError,
    Station,
    StationSearchQuery,
)

PETROMAP_API_BASE_URL = "https://api.petromap.eu/v2"
PETROMAP_PLACES_PATH = "/places"
PETROMAP_USAGE_PATH = "/usage"
MFS_RADIUS_LIMIT_KM = MAX_API_RADIUS_KM

_FUEL_PARAMS: dict[str, dict[str, str]] = {
    "diesel": {"fuelFamily": "diesel"},
    "e5": {"fuel": "petrol_95_e5"},
}


@dataclass(slots=True, frozen=True)
class PetromapSearchRequest:
    """A serializable request description; it performs no I/O."""

    url: str
    params: dict[str, str]


@dataclass(slots=True, frozen=True)
class PetromapSearchResult:
    """Normalized page plus the provider cursor and optional charge."""

    stations: list[Station]
    next_cursor: str | None
    credits: int | None


@dataclass(slots=True, frozen=True)
class PetromapResponseMetadata:
    """Documented response accounting metadata kept out of HA entities."""

    credits_charged: int | None = None
    payg_credits_charged: int | None = None
    credits_remaining: int | None = None
    payg_credits_remaining: int | None = None
    rate_limit: int | None = None
    retry_after: int | None = None
    body_credits: int | None = None
    next_cursor: str | None = None


def _finite_number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as err:
        raise ProviderResponseError(f"Petromap field is not numeric: {field}") from err
    if not isfinite(number):
        raise ProviderResponseError(f"Petromap field is not finite: {field}")
    return number


def _optional_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def build_search_request(query: StationSearchQuery) -> PetromapSearchRequest:
    """Build a documented v2 places request without creating a transport."""

    latitude = _finite_number(query.latitude, "latitude")
    longitude = _finite_number(query.longitude, "longitude")
    radius_km = _finite_number(query.radius_km, "radius_km")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ProviderResponseError("Petromap coordinates are outside valid ranges")
    if not 0 < radius_km <= MFS_RADIUS_LIMIT_KM:
        raise ProviderResponseError("Mobile Fuel Stations radius must be between 0 and 25 km")
    try:
        fuel_params = _FUEL_PARAMS[query.fuel_type]
    except KeyError as err:
        raise ProviderUnsupportedFuelError(
            f"Petromap fuel mapping is not verified: {query.fuel_type}"
        ) from err
    params = {
        "filter": f"circle:{longitude:g},{latitude:g},{radius_km * 1000:g}",
        **fuel_params,
    }
    return PetromapSearchRequest(
        url=f"{PETROMAP_API_BASE_URL}{PETROMAP_PLACES_PATH}",
        params=params,
    )


def map_error(status: int, payload: object) -> Exception:
    """Map documented v2 errors without coupling the coordinator to Petromap."""

    code = payload.get("error") if isinstance(payload, dict) else None
    code = str(code or "provider_error")
    if status == 401 or code == "INVALID_CREDENTIAL":
        return ProviderAuthError(code)
    if status == 403 or code == "SCOPE_NOT_PERMITTED":
        return ProviderPermissionError(code)
    if code == "DAILY_BUDGET_EXHAUSTED":
        return ProviderDailyBudgetError(code)
    if code == "INSUFFICIENT_CREDITS":
        return ProviderInsufficientCreditsError(code)
    if status == 429 or code == "RATE_LIMITED":
        return ProviderRateLimitError(code)
    if status == 503:
        return ProviderUnavailableError(code)
    return ProviderResponseError(code)


def _station_from_place(place: object) -> Station | None:
    if not isinstance(place, dict):
        raise ProviderResponseError("Petromap place is not an object")
    if place.get("kind", "fuel") != "fuel":
        return None
    station_id = place.get("id")
    if not isinstance(station_id, str) or not station_id:
        raise ProviderResponseError("Petromap place has no station id")
    location = place.get("location")
    if not isinstance(location, dict):
        raise ProviderResponseError("Petromap place has no location")
    latitude = _finite_number(location.get("lat"), "location.lat")
    longitude = _finite_number(location.get("lon"), "location.lon")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ProviderResponseError("Petromap station coordinates are invalid")
    distance_value = place.get("distanceM")
    distance = None if distance_value is None else _finite_number(distance_value, "distanceM") / 1000
    if distance is not None and distance < 0:
        raise ProviderResponseError("Petromap distanceM is negative")
    network = place.get("network")
    network = network if isinstance(network, dict) else {}
    fuel = place.get("fuel")
    fuel = fuel if isinstance(fuel, dict) else {}
    price_data = fuel.get("price")
    price_data = price_data if isinstance(price_data, dict) else None
    price = None
    currency = None
    price_updated_at = None
    if price_data is not None:
        if price_data.get("amount") is None:
            raise ProviderResponseError("Petromap price object has no amount")
        price = _finite_number(price_data.get("amount"), "fuel.price.amount")
        currency_value = price_data.get("currency")
        currency = currency_value if isinstance(currency_value, str) else None
        price_updated_at = _optional_timestamp(price_data.get("updatedAt"))
    open_value = place.get("openNow")
    is_open = open_value if isinstance(open_value, bool) else None
    return Station(
        station_id=station_id,
        name=_text(place.get("name")),
        brand=_text(network.get("name")),
        price=price,
        distance=distance,
        is_open=is_open,
        street=_text(place.get("street")),
        house_number="",
        postcode=_text(place.get("postalCode")),
        place=_text(place.get("city")),
        latitude=latitude,
        longitude=longitude,
        currency=currency,
        price_updated_at=price_updated_at,
        country_code=place.get("country") if isinstance(place.get("country"), str) else None,
    )


def parse_search_response(payload: object) -> PetromapSearchResult:
    """Parse one documented v2 places page; never fetches another cursor."""

    if not isinstance(payload, dict) or not isinstance(payload.get("places"), list):
        raise ProviderResponseError("Petromap response has no places list")
    stations = [station for item in payload["places"] if (station := _station_from_place(item))]
    next_cursor = payload.get("nextCursor")
    if next_cursor is not None and not isinstance(next_cursor, str):
        raise ProviderResponseError("Petromap nextCursor is not a string")
    credits = payload.get("credits")
    if credits is not None and (not isinstance(credits, int) or isinstance(credits, bool)):
        raise ProviderResponseError("Petromap credits is not an integer")
    return PetromapSearchResult(stations, next_cursor, credits)


class PetromapProvider:
    """Petromap v2 one-page transport using an injected aiohttp session."""

    def __init__(
        self,
        session: ClientSession,
        api_key: str,
        *,
        timeout: ClientTimeout | None = None,
    ) -> None:
        self._session = session
        self._api_key = api_key
        self._timeout = timeout or ClientTimeout(total=DEFAULT_TIMEOUT.total_seconds())
        self.last_response_metadata: PetromapResponseMetadata | None = None

    async def async_search(self, query: StationSearchQuery) -> list[Station]:
        self.last_response_metadata = None
        request = build_search_request(query)
        try:
            async with self._session.get(
                request.url,
                params=request.params,
                headers={"x-api-key": self._api_key},
                timeout=self._timeout,
            ) as response:
                status = response.status
                if not 200 <= status < 300:
                    try:
                        payload = await response.json(content_type=None)
                    except (TypeError, ValueError):
                        payload = {}
                    self.last_response_metadata = PetromapResponseMetadata(
                        rate_limit=_optional_header_int(response.headers, "X-RateLimit-Limit"),
                        retry_after=_optional_header_int(response.headers, "Retry-After"),
                    )
                    raise map_error(status, payload)
                try:
                    payload = await response.json(content_type=None)
                except (TypeError, ValueError) as err:
                    raise ProviderResponseError("Petromap response is not valid JSON") from err
                result = parse_search_response(payload)
                self.last_response_metadata = PetromapResponseMetadata(
                    credits_charged=_optional_header_int(response.headers, "X-Credits-Charged"),
                    payg_credits_charged=_optional_header_int(
                        response.headers, "X-PAYG-Credits-Charged"
                    ),
                    credits_remaining=_optional_header_int(
                        response.headers, "X-Credits-Remaining"
                    ),
                    payg_credits_remaining=_optional_header_int(
                        response.headers, "X-PAYG-Credits-Remaining"
                    ),
                    rate_limit=_optional_header_int(response.headers, "X-RateLimit-Limit"),
                    retry_after=_optional_header_int(response.headers, "Retry-After"),
                    body_credits=result.credits,
                    next_cursor=result.next_cursor,
                )
                return result.stations
        except asyncio.TimeoutError as err:
            raise ProviderTimeoutError("Petromap request timed out") from err
        except ClientConnectionError as err:
            raise ProviderNetworkError("Petromap connection failed") from err
        except ClientError as err:
            raise ProviderNetworkError("Petromap network request failed") from err


def _optional_header_int(headers: Any, name: str) -> int | None:
    """Read an optional documented integer header without breaking a response."""

    try:
        value = headers.get(name)
    except AttributeError:
        return None
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


async def async_validate_petromap_credentials(
    session: ClientSession,
    api_key: str,
    *,
    timeout: ClientTimeout | None = None,
) -> None:
    """Validate a Petromap credential without making a billable search.

    The usage endpoint only proves that the credential is accepted for that
    endpoint.  It does not prove that the credential has Places scope.
    """

    try:
        async with session.get(
            f"{PETROMAP_API_BASE_URL}{PETROMAP_USAGE_PATH}",
            headers={"x-api-key": api_key},
            timeout=timeout or ClientTimeout(total=DEFAULT_TIMEOUT.total_seconds()),
        ) as response:
            if 200 <= response.status < 300:
                return
            try:
                payload = await response.json(content_type=None)
            except (TypeError, ValueError, ClientError):
                payload = {}
            raise map_error(response.status, payload)
    except asyncio.TimeoutError as err:
        raise ProviderTimeoutError("Petromap credential validation timed out") from err
    except ClientConnectionError as err:
        raise ProviderNetworkError("Petromap credential validation connection failed") from err
    except ClientError as err:
        raise ProviderNetworkError("Petromap credential validation failed") from err
