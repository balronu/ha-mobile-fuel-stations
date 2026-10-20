"""Tankerkönig provider adapter."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from ..const import API_URL
from .base import (
    CountryPriceCoverage,
    ProviderAuthError,
    ProviderCapabilities,
    ProviderNetworkError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderRequestDiagnostics,
    Station,
    StationSearchQuery,
)


class TankerkoenigProvider:
    """Preserve the v0.4 Tankerkönig request and normalization behavior."""

    capabilities = ProviderCapabilities(
        supported_countries=frozenset({"DE"}),
        supported_fuel_types=frozenset({"diesel", "e5", "e10"}),
        max_radius_km=25.0,
        country_price_coverage={"DE": CountryPriceCoverage.PER_STATION},
    )

    def __init__(self, session: ClientSession, api_key: str, timeout: float = 15) -> None:
        self._session = session
        self._api_key = api_key
        self._timeout = timeout

    async def async_search(self, query: StationSearchQuery) -> list[Station]:
        params = {
            "lat": f"{query.latitude:.7f}",
            "lng": f"{query.longitude:.7f}",
            "rad": f"{query.radius_km:g}",
            "sort": "price",
            "type": query.fuel_type,
            "apikey": self._api_key,
        }
        try:
            async with self._session.get(API_URL, params=params, timeout=self._timeout) as response:
                if response.status == 429:
                    error = ProviderRateLimitError("rate_limited")
                    try:
                        retry_after = int(response.headers.get("Retry-After", ""))
                    except (TypeError, ValueError):
                        retry_after = None
                    if retry_after is not None and retry_after >= 0:
                        error.retry_after = retry_after
                    error.diagnostics = ProviderRequestDiagnostics(
                        provider="tankerkoenig", http_status=429,
                        error_code="rate_limited", retry_after=retry_after,
                        quota_limit=None, quota_remaining=None,
                        request_success=False, response_ok=None,
                    )
                    raise error
                if response.status in (401, 403):
                    error = ProviderAuthError("authentication_failed")
                    error.diagnostics = ProviderRequestDiagnostics(
                        provider="tankerkoenig", http_status=response.status,
                        error_code="authentication_failed", retry_after=None,
                        quota_limit=None, quota_remaining=None,
                        request_success=False, response_ok=None,
                    )
                    raise error
                if response.status >= 500:
                    error = ProviderUnavailableError(f"http_{response.status}")
                    error.diagnostics = ProviderRequestDiagnostics(
                        provider="tankerkoenig", http_status=response.status,
                        error_code="provider_unavailable", retry_after=None,
                        quota_limit=None, quota_remaining=None,
                        request_success=False, response_ok=None,
                    )
                    raise error
                response.raise_for_status()
                raw_payload = await response.json(content_type=None)
                if not isinstance(raw_payload, dict):
                    error = ProviderResponseError("invalid_json_shape")
                    error.diagnostics = ProviderRequestDiagnostics(
                        provider="tankerkoenig", http_status=200,
                        error_code="invalid_json_shape", retry_after=None,
                        quota_limit=None, quota_remaining=None,
                        request_success=False, response_ok=None,
                    )
                    raise error
                payload: dict[str, Any] = raw_payload
        except ClientResponseError as err:
            error = ProviderResponseError(f"http_{err.status}")
            error.diagnostics = ProviderRequestDiagnostics(
                provider="tankerkoenig", http_status=err.status,
                error_code="http_error", retry_after=None,
                quota_limit=None, quota_remaining=None,
                request_success=False, response_ok=None,
            )
            raise error from err
        except TimeoutError as err:
            raise ProviderTimeoutError("Provider request timed out") from err
        except ClientError as err:
            raise ProviderNetworkError("Provider request failed") from err
        except ValueError as err:
            error = ProviderResponseError("invalid_json")
            error.diagnostics = ProviderRequestDiagnostics(
                provider="tankerkoenig", http_status=200,
                error_code="invalid_json", retry_after=None,
                quota_limit=None, quota_remaining=None,
                request_success=False, response_ok=None,
            )
            raise error from err

        if payload.get("ok") is not True:
            status = str(payload.get("status", "provider_error"))
            if "key" in status.lower() or "auth" in status.lower():
                error = ProviderAuthError("authentication_failed")
            elif any(token in status.lower() for token in ("limit", "rate", "quota")):
                error = ProviderRateLimitError("rate_limited")
            else:
                error = ProviderResponseError("provider_response_rejected")
            error.diagnostics = ProviderRequestDiagnostics(
                provider="tankerkoenig", http_status=200,
                error_code=status[:80], retry_after=None,
                quota_limit=None, quota_remaining=None,
                request_success=False, response_ok=False,
            )
            raise error

        stations = payload.get("stations")
        if not isinstance(stations, list):
            error = ProviderResponseError("invalid_stations_payload")
            error.diagnostics = ProviderRequestDiagnostics(
                provider="tankerkoenig", http_status=200,
                error_code="invalid_stations_payload", retry_after=None,
                quota_limit=None, quota_remaining=None,
                request_success=False, response_ok=True,
            )
            raise error

        return [
            replace(self._normalize(item), fuel_type=query.fuel_type, requested_fuel=query.fuel_type, provider="tankerkoenig")
            for item in stations if isinstance(item, dict)
        ]

    @staticmethod
    def _number(value: Any) -> float | None:
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @classmethod
    def _normalize(cls, item: dict[str, Any]) -> Station:
        price = cls._number(item.get("price", item.get("diesel")))
        return Station(
            station_id=str(item.get("id", item.get("station_id", ""))),
            name=str(item.get("name", "")),
            brand=str(item.get("brand", "")),
            price=price,
            distance=cls._number(item.get("dist", item.get("distance"))),
            is_open=bool(item.get("isOpen", item.get("is_open", False))),
            street=str(item.get("street", "")),
            house_number=str(item.get("houseNumber", item.get("house_number", ""))),
            postcode=str(item.get("postCode", item.get("postcode", ""))),
            place=str(item.get("place", item.get("city", ""))),
            latitude=cls._number(item.get("lat", item.get("latitude"))),
            longitude=cls._number(item.get("lng", item.get("longitude"))),
        )
