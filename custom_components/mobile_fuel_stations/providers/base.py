"""Provider-neutral contracts and errors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from aiohttp import ClientSession



@dataclass(slots=True, frozen=True)
class Station:
    """Provider-neutral normalized station data."""

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


class ProviderError(Exception):
    """Base error raised by a station provider."""


class ProviderAuthError(ProviderError):
    """The provider rejected the configured credential."""


class ProviderRateLimitError(ProviderError):
    """The provider rate limit was reached."""


class ProviderConfigurationError(ProviderError):
    """The selected provider is not available in this release."""


class FuelStationProvider(Protocol):
    """Minimal interface required by the coordinator."""

    def __init__(self, session: ClientSession, api_key: str) -> None: ...

    async def async_search(
        self, latitude: float, longitude: float, radius: float, fuel_type: str
    ) -> list[Station]: ...
