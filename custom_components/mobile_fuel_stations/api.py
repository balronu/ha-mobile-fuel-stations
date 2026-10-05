"""Async client for the Tankerkönig nearby-stations endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import API_URL


class MobileFuelStationsError(Exception):
    """Base exception for provider errors."""


class MobileFuelStationsAuthError(MobileFuelStationsError):
    """The provider rejected the API key."""


class MobileFuelStationsRateLimitError(MobileFuelStationsError):
    """The provider rate limit was reached."""


@dataclass(slots=True, frozen=True)
class Station:
    """Normalized provider station data."""

    station_id: str
    name: str
    brand: str
    price: float | None
    distance: float | None
    is_open: bool
    street: str
    house_number: str
    postcode: str
    place: str
    latitude: float | None
    longitude: float | None


class TankerkoenigClient:
    """Minimal async API client; the key is kept only in memory."""

    def __init__(self, session: ClientSession, api_key: str, timeout: float = 15) -> None:
        self._session = session
        self._api_key = api_key
        self._timeout = timeout

    async def async_search(
        self, latitude: float, longitude: float, radius: float, fuel_type: str
    ) -> list[Station]:
        params = {
            "lat": f"{latitude:.7f}",
            "lng": f"{longitude:.7f}",
            "rad": f"{radius:g}",
            "sort": "price",
            "type": fuel_type,
            "apikey": self._api_key,
        }
        try:
            async with self._session.get(API_URL, params=params, timeout=self._timeout) as response:
                if response.status == 429:
                    raise MobileFuelStationsRateLimitError
                response.raise_for_status()
                payload: dict[str, Any] = await response.json(content_type=None)
        except ClientResponseError as err:
            raise MobileFuelStationsError(f"HTTP {err.status}") from err
        except (ClientError, TimeoutError, ValueError) as err:
            raise MobileFuelStationsError("Provider request failed") from err

        if payload.get("ok") is not True:
            status = str(payload.get("status", "provider_error"))
            if "key" in status.lower() or "auth" in status.lower():
                raise MobileFuelStationsAuthError
            if "limit" in status.lower():
                raise MobileFuelStationsRateLimitError
            raise MobileFuelStationsError("Provider returned ok=false")

        return [self._normalize(item) for item in payload.get("stations", []) if isinstance(item, dict)]

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


def sort_stations(stations: list[Station], limit: int) -> list[Station]:
    """Prefer open stations, then valid prices, then ascending price."""

    return sorted(
        stations,
        key=lambda station: (
            not station.is_open,
            station.price is None,
            station.price if station.price is not None else float("inf"),
        ),
    )[:limit]
