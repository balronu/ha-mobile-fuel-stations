"""Nakordoni v2 nearby fuel-stations provider."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Any

from aiohttp import ClientConnectionError, ClientError, ClientSession, ClientTimeout

from ..const import DEFAULT_TIMEOUT, MAX_API_RADIUS_KM, PROVIDER_NAKORDONI
from .base import (
    CountryPriceCoverage,
    ProviderAuthError,
    ProviderCapabilities,
    ProviderNetworkError,
    ProviderPermissionError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderRequestDiagnostics,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderUnsupportedFuelError,
    Station,
    StationSearchQuery,
)

NAKORDONI_API_URL = "https://nakordoni.eu/api/v2/data/fuel-stations"
NAKORDONI_ATTRIBUTION_URL = "https://nakordoni.eu"
NAKORDONI_FUELS = frozenset({"diesel", "e5", "e10", "lpg"})
NAKORDONI_CAPABILITIES = ProviderCapabilities(
    supported_fuel_types=NAKORDONI_FUELS,
    max_radius_km=MAX_API_RADIUS_KM,
    country_price_coverage=None,
)


@dataclass(slots=True, frozen=True)
class NakordoniResponseMetadata:
    """Non-sensitive response quality and quota metadata."""

    quota_limit: int | None = None
    quota_remaining: int | None = None
    attribution_url: str = NAKORDONI_ATTRIBUTION_URL
    notices: tuple[str, ...] = ()
    total_found: int | None = None


_SAFE_ERROR_CODES = frozenset(
    {
        "qps_exceeded",
        "quota_exceeded",
        "market_not_allowed",
        "not_approved",
        "invalid_credential",
    }
)


def _safe_error_code(value: object) -> str:
    """Keep only the documented, non-sensitive provider classifications."""

    return value if isinstance(value, str) and value in _SAFE_ERROR_CODES else "provider_error"


def _number(value: Any, field: str, *, optional: bool = False) -> float | None:
    if value is None and optional:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError) as err:
        raise ProviderResponseError(f"Nakordoni field is not numeric: {field}") from err
    if not isfinite(result):
        raise ProviderResponseError(f"Nakordoni field is not finite: {field}")
    return result


def _timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ProviderResponseError("Nakordoni timestamp is not a string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as err:
        raise ProviderResponseError("Nakordoni timestamp is invalid") from err


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _error(
    status: int,
    payload: object,
    headers: Any,
    *,
    response_ok: bool | None,
) -> Exception:
    error = payload.get("error") if isinstance(payload, dict) else None
    code = error.get("code") if isinstance(error, dict) else error
    if status == 401 or code in {"missing_api_key", "invalid_api_key", "invalid_credential"}:
        exception = ProviderAuthError(_safe_error_code("invalid_credential"))
    elif status == 403 or code in {"not_approved", "market_not_allowed"}:
        exception = ProviderPermissionError(_safe_error_code(code))
    elif status == 429 or code in {"qps_exceeded", "quota_exceeded"}:
        exception = ProviderRateLimitError(_safe_error_code(code))
    elif status in {500, 503, 504} or code in {
        "internal_error", "product_unavailable", "status_unavailable", "timeout",
    }:
        exception = ProviderUnavailableError("provider_error")
    else:
        exception = ProviderResponseError("provider_error")
    exception.diagnostics = ProviderRequestDiagnostics(
        provider=PROVIDER_NAKORDONI,
        fuel_type=fuel_type,
        requested_fuel=fuel_type,
        http_status=status,
        error_code=_safe_error_code(code),
        retry_after=_header_nonnegative_int(headers, "Retry-After"),
        quota_limit=_header_nonnegative_int(headers, "X-Devapi-Limit"),
        quota_remaining=_header_nonnegative_int(headers, "X-Devapi-Remaining"),
        request_success=False,
        response_ok=response_ok,
    )
    return exception


def _parse_station(item: object, fuel_type: str) -> Station:
    if not isinstance(item, dict):
        raise ProviderResponseError("Nakordoni station is not an object")
    lat = _number(item.get("lat"), "station.lat", optional=True)
    lon = _number(item.get("lng", item.get("lon")), "station.lng", optional=True)
    station_ref = item.get("station_ref")
    if not isinstance(station_ref, str) or not station_ref:
        legacy_id = item.get("id")
        station_ref = str(legacy_id) if legacy_id is not None else f"{_text(item.get('name'))}:{lat}:{lon}"
    address = item.get("address")
    address = address if isinstance(address, dict) else {}
    prices = item.get("prices")
    prices = prices if isinstance(prices, dict) else {}
    quote = prices.get(fuel_type)
    quote = quote if isinstance(quote, dict) else {}
    return Station(
        station_id=station_ref,
        name=_text(item.get("name")),
        brand=_text(item.get("brand")),
        price=_number(quote.get("price"), "prices.price", optional=True),
        distance=_number(item.get("distance_km"), "distance_km", optional=True),
        is_open=None,
        street=_text(address.get("street", item.get("street"))),
        house_number=_text(address.get("house_number", address.get("houseNumber", item.get("house_number")))),
        postcode=_text(address.get("postcode", address.get("postal_code", item.get("postcode")))),
        place=_text(address.get("city", address.get("town", item.get("city")))),
        latitude=lat,
        longitude=lon,
        currency=_text(quote.get("currency")) or None,
        price_updated_at=_timestamp(quote.get("updated_at")),
        country_code=_text(item.get("country")) or None,
        provider=PROVIDER_NAKORDONI,
        price_confirmed_at=_timestamp(quote.get("confirmed_at")),
        price_age_hours=_number(quote.get("age_hours"), "prices.age_hours", optional=True),
        price_stale=quote.get("stale") if isinstance(quote.get("stale"), bool) else None,
    )


class NakordoniProvider:
    """One-request nearby search using Home Assistant's shared session."""

    capabilities = NAKORDONI_CAPABILITIES

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
        self.last_response_metadata: NakordoniResponseMetadata | None = None
        self.last_request_diagnostics: ProviderRequestDiagnostics | None = None

    async def async_search(self, query: StationSearchQuery) -> list[Station]:
        self.last_response_metadata = None
        self.last_request_diagnostics = None
        if query.fuel_type not in NAKORDONI_FUELS:
            raise ProviderUnsupportedFuelError(
                f"Nakordoni fuel mapping is not verified: {query.fuel_type}"
            )
        radius = min(float(query.radius_km), MAX_API_RADIUS_KM)
        limit = min(max(int(query.station_count), 1), 20)
        params = {
            "lat": f"{query.latitude:.7f}",
            "lon": f"{query.longitude:.7f}",
            "radius_km": f"{radius:g}",
            "fuel_type": query.fuel_type,
            "limit": str(limit),
            "lang": "de",
        }
        try:
            async with self._session.get(
                NAKORDONI_API_URL,
                params=params,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=self._timeout,
            ) as response:
                quota_limit = _header_nonnegative_int(response.headers, "X-Devapi-Limit")
                quota_remaining = _header_nonnegative_int(response.headers, "X-Devapi-Remaining")
                retry_after = _header_nonnegative_int(response.headers, "Retry-After")
                try:
                    payload = await response.json(content_type=None)
                except (TypeError, ValueError) as err:
                    exception = ProviderResponseError("provider_error")
                    exception.diagnostics = ProviderRequestDiagnostics(
                        PROVIDER_NAKORDONI, response.status, "provider_error", retry_after,
                        quota_limit, quota_remaining, False, None,
                    )
                    self.last_request_diagnostics = exception.diagnostics
                    raise exception from err
                response_ok = payload.get("ok") if isinstance(payload, dict) and isinstance(payload.get("ok"), bool) else None
                if response.status < 200 or response.status >= 300:
                    exception = _error(response.status, payload, response.headers, response_ok=response_ok)
                    self.last_request_diagnostics = exception.diagnostics
                    raise exception
                if not isinstance(payload, dict) or payload.get("ok") is not True:
                    exception = _error(response.status, payload, response.headers, response_ok=response_ok)
                    self.last_request_diagnostics = exception.diagnostics
                    raise exception
                data = payload.get("data")
                if not isinstance(data, dict) or not isinstance(data.get("stations"), list):
                    exception = ProviderResponseError("provider_error")
                    exception.diagnostics = ProviderRequestDiagnostics(
                        PROVIDER_NAKORDONI, response.status, "provider_error", retry_after,
                        quota_limit, quota_remaining, False, True,
                    )
                    self.last_request_diagnostics = exception.diagnostics
                    raise exception
                notices = data.get("notices")
                self.last_response_metadata = NakordoniResponseMetadata(
                    quota_limit=quota_limit,
                    quota_remaining=quota_remaining,
                    notices=tuple(
                        str(item.get("reason", item)) if isinstance(item, dict) else str(item)
                        for item in notices
                    ) if isinstance(notices, list) else (),
                    total_found=data.get("total_found") if isinstance(data.get("total_found"), int) else None,
                )
                try:
                    stations = [_parse_station(item, query.fuel_type) for item in data["stations"]]
                except ProviderError as err:
                    err.diagnostics = ProviderRequestDiagnostics(
                        PROVIDER_NAKORDONI, response.status, "provider_error", retry_after,
                        quota_limit, quota_remaining, False, True,
                    )
                    self.last_request_diagnostics = err.diagnostics
                    raise
                self.last_request_diagnostics = ProviderRequestDiagnostics(
                    PROVIDER_NAKORDONI, response.status, None, retry_after,
                    quota_limit, quota_remaining, True, True,
                )
                return stations
        except asyncio.TimeoutError as err:
            exception = ProviderTimeoutError("provider_error")
            exception.diagnostics = ProviderRequestDiagnostics(PROVIDER_NAKORDONI, None, "provider_error", None, None, None, False, None)
            self.last_request_diagnostics = exception.diagnostics
            raise exception from err
        except ClientConnectionError as err:
            exception = ProviderNetworkError("provider_error")
            exception.diagnostics = ProviderRequestDiagnostics(PROVIDER_NAKORDONI, None, "provider_error", None, None, None, False, None)
            self.last_request_diagnostics = exception.diagnostics
            raise exception from err
        except ClientError as err:
            exception = ProviderNetworkError("provider_error")
            exception.diagnostics = ProviderRequestDiagnostics(PROVIDER_NAKORDONI, None, "provider_error", None, None, None, False, None)
            self.last_request_diagnostics = exception.diagnostics
            raise exception from err


def _header_nonnegative_int(headers: Any, name: str) -> int | None:
    try:
        value = headers.get(name)
        parsed = int(value) if value is not None else None
        return parsed if parsed is not None and parsed >= 0 else None
    except (AttributeError, TypeError, ValueError):
        return None
