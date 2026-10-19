"""Nakordoni v2 nearby fuel-stations provider."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Any

from aiohttp import ClientConnectionError, ClientError, ClientSession, ClientTimeout
from homeassistant import exceptions as ha_exceptions

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
NAKORDONI_ACCOUNT_USAGE_URL = "https://nakordoni.eu/api/v2/account/usage"
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
    empty_reason: str | None = None
    nearest_station_km: float | None = None
    markets_approved: tuple[str, ...] = ()
    markets_granted: tuple[str, ...] = ()
    markets_allowed: tuple[str, ...] = ()
    markets_available: tuple[str, ...] = ()
    upgrade_url: str | None = None
    coverage_countries: tuple[str, ...] = ()
    coverage_fuels: tuple[str, ...] = ()
    coverage_status: str = "unknown"


@dataclass(slots=True, frozen=True)
class NakordoniQuota:
    """One documented account-usage quota class."""

    limit: int | None = None
    used: int | None = None
    remaining: int | None = None
    reset_at: datetime | None = None


@dataclass(slots=True, frozen=True)
class NakordoniAccountUsage:
    """Secret-free projection of Nakordoni's documented usage response."""

    plan_slug: str | None = None
    plan_name: str | None = None
    qps: int | None = None
    quotas: dict[str, NakordoniQuota] | None = None
    markets_approved: tuple[str, ...] = ()
    markets_allowed: int | None = None
    markets_available: tuple[str, ...] = ()
    key_bound: bool | None = None
    pass_active: bool | None = None
    pass_expires_at: datetime | None = None
    pass_days_left: int | None = None
    upgrade_url: str | None = None
    pass_url: str | None = None

    @property
    def cheap(self) -> NakordoniQuota:
        return (self.quotas or {}).get("cheap", NakordoniQuota())

    def as_diagnostics(self) -> dict[str, object]:
        return {
            "plan": {"slug": self.plan_slug, "name": self.plan_name},
            "qps": self.qps,
            "quotas": {
                name: {
                    "limit": quota.limit,
                    "used": quota.used,
                    "remaining": quota.remaining,
                    "reset_at": quota.reset_at.isoformat() if quota.reset_at else None,
                }
                for name, quota in (self.quotas or {}).items()
            },
            "markets": {
                "approved": list(self.markets_approved),
                "allowed": self.markets_allowed,
                "available": list(self.markets_available),
                "key_bound": self.key_bound,
            },
            "pass": {
                "active": self.pass_active,
                "expires_at": self.pass_expires_at.isoformat() if self.pass_expires_at else None,
                "days_left": self.pass_days_left,
            },
            "upgrade_url": self.upgrade_url,
            "pass_url": self.pass_url,
        }


@dataclass(slots=True, frozen=True)
class NakordoniMarketAccess:
    """Secret-free market metadata from OAuth or a documented API response."""

    markets_approved: tuple[str, ...] = ()
    markets_granted: tuple[str, ...] = ()
    markets_allowed: tuple[str, ...] = ()
    markets_available: tuple[str, ...] = ()
    upgrade_url: str | None = None

    @property
    def permitted_markets(self) -> frozenset[str] | None:
        """Return an explicit permission set, or None when metadata is absent."""

        for values in (self.markets_allowed, self.markets_granted, self.markets_approved):
            if values:
                return frozenset(values)
        return None

    def status_for(self, country: str | None) -> str:
        normalized = _market_codes((country,))
        if not normalized:
            return "unknown"
        country_code = normalized[0]
        permitted = self.permitted_markets
        if permitted is None:
            return "unknown"
        return "allowed" if country_code in permitted else "not_allowed"

    def as_diagnostics(self) -> dict[str, object]:
        return {
            "markets_approved": list(self.markets_approved),
            "markets_granted": list(self.markets_granted),
            "markets_allowed": list(self.markets_allowed),
            "markets_available": list(self.markets_available),
            "upgrade_url": self.upgrade_url,
        }


def _market_codes(value: Any) -> tuple[str, ...]:
    """Normalize only country-code lists; never serialize token contents."""

    if not isinstance(value, (list, tuple, set, frozenset)):
        return ()
    return tuple(sorted({item.strip().upper() for item in value if isinstance(item, str) and len(item.strip()) == 2 and item.strip().isalpha()}))


def extract_market_access(value: object) -> NakordoniMarketAccess:
    """Extract documented market fields from a token or response object."""

    if not isinstance(value, dict):
        return NakordoniMarketAccess()
    source = value.get("data") if isinstance(value.get("data"), dict) else value
    return NakordoniMarketAccess(
        markets_approved=_market_codes(source.get("markets_approved")),
        markets_granted=_market_codes(source.get("markets_granted")),
        markets_allowed=_market_codes(source.get("markets_allowed")),
        markets_available=_market_codes(source.get("markets_available")),
        upgrade_url=source.get("upgrade_url") if isinstance(source.get("upgrade_url"), str) else None,
    )


def _coverage_fields(data: dict[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...], str]:
    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        return (), (), "unknown"
    countries = _market_codes(coverage.get("countries", coverage.get("markets")))
    fuels = tuple(sorted({item.strip().lower() for item in coverage.get("fuels", ()) if isinstance(item, str) and item.strip()})) if isinstance(coverage.get("fuels", ()), (list, tuple, set)) else ()
    status = coverage.get("status") if isinstance(coverage.get("status"), str) else "confirmed"
    return countries, fuels, status


_SAFE_ERROR_CODES = frozenset(
    {
        "qps_exceeded",
        "quota_exceeded",
        "market_not_allowed",
        "integration_product_not_allowed",
        "not_approved",
        "invalid_credential",
        "invalid_grant",
    }
)

_OAUTH_TOKEN_ERRORS = tuple(
    exception_type
    for exception_name in (
        "OAuth2TokenRequestReauthError",
        "OAuth2TokenRequestError",
    )
    if isinstance(
        exception_type := getattr(ha_exceptions, exception_name, None), type
    )
)
_OAUTH_REAUTH_ERRORS = tuple(
    exception_type
    for exception_name in ("OAuth2TokenRequestReauthError",)
    if isinstance(
        exception_type := getattr(ha_exceptions, exception_name, None), type
    )
)


def _safe_error_code(value: object) -> str:
    """Keep only the documented, non-sensitive provider classifications."""

    return value if isinstance(value, str) and value in _SAFE_ERROR_CODES else "provider_error"


def _nonnegative_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _parse_account_usage(payload: object) -> NakordoniAccountUsage:
    """Parse only fields documented for GET /api/v2/account/usage."""

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise ProviderResponseError("Nakordoni account usage data is not an object")
    plan = data.get("plan") if isinstance(data.get("plan"), dict) else {}
    raw_quotas = data.get("quotas") if isinstance(data.get("quotas"), dict) else {}
    quotas: dict[str, NakordoniQuota] = {}
    for name in ("cheap", "heavy", "route"):
        raw = raw_quotas.get(name)
        if not isinstance(raw, dict):
            continue
        quotas[name] = NakordoniQuota(
            limit=_nonnegative_int(raw.get("limit")),
            used=_nonnegative_int(raw.get("used")),
            remaining=_nonnegative_int(raw.get("remaining")),
            reset_at=_timestamp(raw.get("reset_at")),
        )
    markets = data.get("markets") if isinstance(data.get("markets"), dict) else {}
    trip_pass = data.get("pass") if isinstance(data.get("pass"), dict) else {}
    return NakordoniAccountUsage(
        plan_slug=plan.get("slug") if isinstance(plan.get("slug"), str) else None,
        plan_name=plan.get("name") if isinstance(plan.get("name"), str) else None,
        qps=_nonnegative_int(data.get("qps")),
        quotas=quotas,
        markets_approved=_market_codes(markets.get("approved")),
        markets_allowed=_nonnegative_int(markets.get("allowed")),
        markets_available=_market_codes(markets.get("available")),
        key_bound=markets.get("key_bound") if isinstance(markets.get("key_bound"), bool) else None,
        pass_active=trip_pass.get("active") if isinstance(trip_pass.get("active"), bool) else None,
        pass_expires_at=_timestamp(trip_pass.get("expires_at")),
        pass_days_left=_nonnegative_int(trip_pass.get("days_left")),
        upgrade_url=data.get("upgrade_url") if isinstance(data.get("upgrade_url"), str) else None,
        pass_url=data.get("pass_url") if isinstance(data.get("pass_url"), str) else None,
    )


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


def _first_text(*values: Any) -> str:
    for value in values:
        text = _text(value).strip()
        if text:
            return text
    return ""


def _address_fields(item: dict[str, Any]) -> tuple[str, str, str, str]:
    """Normalize only address fields explicitly returned by Nakordoni."""

    raw_address = item.get("address")
    address = raw_address if isinstance(raw_address, dict) else {}
    street = _first_text(
        address.get("street"), address.get("street_name"), address.get("road"), item.get("street")
    )
    house_number = _first_text(
        address.get("house_number"), address.get("houseNumber"), address.get("number"),
        item.get("house_number"), item.get("houseNumber"),
    )
    postcode = _first_text(
        address.get("postcode"), address.get("postal_code"), address.get("postCode"), address.get("zip"),
        item.get("postcode"), item.get("postal_code"),
    )
    place = _first_text(
        address.get("city"), address.get("town"), address.get("locality"), item.get("city"), item.get("town")
    )
    # Some responses expose only one formatted address string. Preserve that
    # provider value as-is; never parse or invent postal components.
    if not any((street, house_number, postcode, place)) and isinstance(raw_address, str):
        street = raw_address.strip()
    return street, house_number, postcode, place


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
    elif status == 403 or code in {
        "not_approved", "market_not_allowed", "integration_product_not_allowed"
    }:
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
    prices = item.get("prices")
    prices = prices if isinstance(prices, dict) else {}
    quote = prices.get(fuel_type)
    quote = quote if isinstance(quote, dict) else {}
    street, house_number, postcode, place = _address_fields(item)
    price = _number(quote.get("price"), "prices.price", optional=True)
    return Station(
        station_id=station_ref,
        name=_text(item.get("name")),
        brand=_text(item.get("brand")),
        price=price,
        distance=_number(item.get("distance_km"), "distance_km", optional=True),
        is_open=None,
        street=street,
        house_number=house_number,
        postcode=postcode,
        place=place,
        latitude=lat,
        longitude=lon,
        currency=_text(quote.get("currency")) or None,
        price_updated_at=_timestamp(quote.get("updated_at")),
        country_code=_text(item.get("country")) or None,
        provider=PROVIDER_NAKORDONI,
        price_confirmed_at=_timestamp(quote.get("confirmed_at")),
        price_age_hours=_number(quote.get("age_hours"), "prices.age_hours", optional=True),
        price_stale=quote.get("stale") if isinstance(quote.get("stale"), bool) else None,
        fuel_type=fuel_type,
        requested_fuel=fuel_type,
        fuel_prices={fuel_type: price} if price is not None else None,
    )


class NakordoniProvider:
    """One-request nearby search using Home Assistant's shared session."""

    capabilities = NAKORDONI_CAPABILITIES

    def __init__(
        self,
        session: ClientSession,
        api_key: str | None,
        *,
        timeout: ClientTimeout | None = None,
        oauth_session=None,
    ) -> None:
        self._session = session
        self._api_key = api_key
        self._oauth_session = oauth_session
        self._timeout = timeout or ClientTimeout(total=DEFAULT_TIMEOUT.total_seconds())
        self.last_response_metadata: NakordoniResponseMetadata | None = None
        self.last_request_diagnostics: ProviderRequestDiagnostics | None = None
        self.last_account_usage: NakordoniAccountUsage | None = None

    async def async_get_account_usage(self) -> NakordoniAccountUsage:
        """Fetch the unmetered, documented account usage endpoint."""

        self.last_account_usage = None
        try:
            if self._oauth_session is not None:
                response = await self._oauth_session.async_request(
                    "GET", NAKORDONI_ACCOUNT_USAGE_URL, params={}, timeout=self._timeout
                )
            else:
                response = self._session.get(
                    NAKORDONI_ACCOUNT_USAGE_URL,
                    params={},
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    timeout=self._timeout,
                )
            async with response as response:
                try:
                    payload = await response.json(content_type=None)
                except (TypeError, ValueError) as err:
                    exception = ProviderResponseError("provider_error")
                    exception.diagnostics = ProviderRequestDiagnostics(
                        PROVIDER_NAKORDONI, response.status, "provider_error", None,
                        None, None, False, None,
                    )
                    raise exception from err
                response_ok = (
                    payload.get("ok")
                    if isinstance(payload, dict) and isinstance(payload.get("ok"), bool)
                    else None
                )
                if response.status < 200 or response.status >= 300 or not isinstance(payload, dict) or payload.get("ok") is not True:
                    exception = _error(response.status, payload, response.headers, response_ok=response_ok)
                    self.last_request_diagnostics = exception.diagnostics
                    error = payload.get("error") if isinstance(payload, dict) else None
                    if isinstance(error, dict):
                        setattr(exception, "reset_at", _timestamp(error.get("reset_at")))
                        setattr(exception, "upgrade_url", error.get("upgrade_url") if isinstance(error.get("upgrade_url"), str) else None)
                        setattr(exception, "pass_url", error.get("pass_url") if isinstance(error.get("pass_url"), str) else None)
                    raise exception
                try:
                    usage = _parse_account_usage(payload)
                except ProviderResponseError as err:
                    err.diagnostics = ProviderRequestDiagnostics(
                        PROVIDER_NAKORDONI, response.status, "provider_error", None,
                        None, None, False, True,
                    )
                    self.last_request_diagnostics = err.diagnostics
                    raise
                self.last_account_usage = usage
                self.last_request_diagnostics = ProviderRequestDiagnostics(
                    PROVIDER_NAKORDONI, response.status, None, None, None, None, True, True,
                )
                return usage
        except asyncio.TimeoutError as err:
            exception = ProviderTimeoutError("provider_error")
            exception.diagnostics = ProviderRequestDiagnostics(PROVIDER_NAKORDONI, None, "provider_error", None, None, None, False, None)
            raise exception from err
        except ClientConnectionError as err:
            exception = ProviderNetworkError("provider_error")
            exception.diagnostics = ProviderRequestDiagnostics(PROVIDER_NAKORDONI, None, "provider_error", None, None, None, False, None)
            raise exception from err
        except _OAUTH_TOKEN_ERRORS as err:
            error_code = "invalid_grant" if _OAUTH_REAUTH_ERRORS and isinstance(err, _OAUTH_REAUTH_ERRORS) else "invalid_credential"
            exception = ProviderAuthError(error_code)
            exception.diagnostics = ProviderRequestDiagnostics(PROVIDER_NAKORDONI, None, error_code, None, None, None, False, None)
            raise exception from err
        except ClientError as err:
            exception = ProviderNetworkError("provider_error")
            exception.diagnostics = ProviderRequestDiagnostics(PROVIDER_NAKORDONI, None, "provider_error", None, None, None, False, None)
            raise exception from err

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
            if self._oauth_session is not None:
                response = await self._oauth_session.async_request(
                    "GET", NAKORDONI_API_URL, params=params, timeout=self._timeout
                )
            else:
                response = self._session.get(
                    NAKORDONI_API_URL,
                    params=params,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    timeout=self._timeout,
                )
            # ``ClientSession.get`` returns aiohttp's request context manager,
            # not the response itself.  Binding the result of ``__aenter__``
            # is required before accessing response headers/status/body.
            async with response as response:
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
                market_access = extract_market_access(payload)
                coverage_countries, coverage_fuels, coverage_status = _coverage_fields(data)
                if not coverage_countries and data["stations"]:
                    coverage_countries = tuple(
                        sorted({station.country_code for station in (
                            _parse_station(item, query.fuel_type) for item in data["stations"]
                        ) if station.country_code})
                    )
                    coverage_status = "observed" if coverage_countries else coverage_status
                self.last_response_metadata = NakordoniResponseMetadata(
                    quota_limit=quota_limit,
                    quota_remaining=quota_remaining,
                    notices=tuple(
                        str(item.get("reason", item)) if isinstance(item, dict) else str(item)
                        for item in notices
                    ) if isinstance(notices, list) else (),
                    total_found=data.get("total_found") if isinstance(data.get("total_found"), int) else None,
                    empty_reason=data.get("empty_reason") if isinstance(data.get("empty_reason"), str) else None,
                    nearest_station_km=(
                        _number(data.get("nearest_station_km"), "nearest_station_km", optional=True)
                        if data.get("nearest_station_km") is not None else None
                    ),
                    markets_approved=market_access.markets_approved,
                    markets_granted=market_access.markets_granted,
                    markets_allowed=market_access.markets_allowed,
                    markets_available=market_access.markets_available,
                    upgrade_url=market_access.upgrade_url,
                    coverage_countries=coverage_countries,
                    coverage_fuels=coverage_fuels,
                    coverage_status=coverage_status,
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
        except _OAUTH_TOKEN_ERRORS as err:
            error_code = "invalid_grant" if _OAUTH_REAUTH_ERRORS and isinstance(err, _OAUTH_REAUTH_ERRORS) else "invalid_credential"
            exception = ProviderAuthError(error_code)
            exception.diagnostics = ProviderRequestDiagnostics(
                PROVIDER_NAKORDONI, None, error_code, None, None, None, False, None
            )
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


__all__ = [
    "NAKORDONI_ACCOUNT_USAGE_URL",
    "NAKORDONI_API_URL",
    "NAKORDONI_ATTRIBUTION_URL",
    "NAKORDONI_CAPABILITIES",
    "NAKORDONI_FUELS",
    "NakordoniMarketAccess",
    "NakordoniAccountUsage",
    "NakordoniQuota",
    "NakordoniProvider",
    "NakordoniResponseMetadata",
    "extract_market_access",
]
