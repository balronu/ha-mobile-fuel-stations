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
                    raise ProviderRateLimitError
                response.raise_for_status()
                payload: dict[str, Any] = await response.json(content_type=None)
        except ClientResponseError as err:
            raise ProviderResponseError(f"HTTP {err.status}") from err
        except TimeoutError as err:
            raise ProviderTimeoutError("Provider request timed out") from err
        except ClientError as err:
            raise ProviderNetworkError("Provider request failed") from err
        except ValueError as err:
            raise ProviderResponseError("Provider returned invalid JSON") from err

        if payload.get("ok") is not True:
            status = str(payload.get("status", "provider_error"))
            if "key" in status.lower() or "auth" in status.lower():
                raise ProviderAuthError
            if "limit" in status.lower():
                raise ProviderRateLimitError
            raise ProviderResponseError("Provider returned ok=false")

        return [
            replace(self._normalize(item), fuel_type=query.fuel_type, requested_fuel=query.fuel_type, provider="tankerkoenig")
            for item in payload.get("stations", []) if isinstance(item, dict)
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
