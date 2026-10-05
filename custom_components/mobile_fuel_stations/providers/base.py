"""Provider-neutral contracts and errors."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
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
    is_open: bool | None
    street: str
    house_number: str
    postcode: str
    place: str
    latitude: float | None
    longitude: float | None
    currency: str | None = None
    price_updated_at: datetime | None = None
    country_code: str | None = None


@dataclass(slots=True, frozen=True)
class StationSearchQuery:
    """Provider-neutral inputs for a nearby-station search."""

    latitude: float
    longitude: float
    radius_km: float
    fuel_type: str


class CountryPriceCoverage(StrEnum):
    """How a provider can supply station prices for a country."""

    PER_STATION = "per_station"
    NATIONAL_ONLY = "national_only"
    NO_PRICES = "no_prices"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class ProviderCapabilities:
    """Optional provider metadata; unknown future values remain None."""

    supported_countries: frozenset[str] | None = None
    supported_fuel_types: frozenset[str] | None = None
    max_radius_km: float | None = None
    requires_api_key: bool = True
    country_price_coverage: dict[str, CountryPriceCoverage] | None = None


class ProviderError(Exception):
    """Base error raised by a station provider."""


class ProviderAuthError(ProviderError):
    """The provider rejected the configured credential."""


class ProviderRateLimitError(ProviderError):
    """The provider rate limit was reached."""


class ProviderConfigurationError(ProviderError):
    """The selected provider is not available in this release."""


class UnknownProviderError(ProviderConfigurationError):
    """No provider registration exists for the requested mode."""


class ProviderDisabledError(ProviderConfigurationError):
    """A known provider is deliberately disabled in this release."""


class ProviderTimeoutError(ProviderError):
    """The provider request timed out."""


class ProviderNetworkError(ProviderError):
    """The provider request failed at the network layer."""


class ProviderResponseError(ProviderError):
    """The provider returned an unusable response."""


class ProviderPermissionError(ProviderError):
    """The credential lacks permission for the requested provider operation."""


class ProviderCreditError(ProviderError):
    """The provider rejected a request because of the credit budget."""


class ProviderDailyBudgetError(ProviderCreditError):
    """The provider daily budget is exhausted."""


class ProviderInsufficientCreditsError(ProviderCreditError):
    """The provider balance cannot cover the requested response."""


class ProviderUnavailableError(ProviderError):
    """The provider service is temporarily unavailable."""


class ProviderUnsupportedFuelError(ProviderConfigurationError):
    """The provider contract does not define the requested fuel mapping."""


class FuelStationProvider(Protocol):
    """Minimal interface required by the coordinator."""

    def __init__(self, session: ClientSession, api_key: str) -> None: ...

    capabilities: ProviderCapabilities

    async def async_search(self, query: StationSearchQuery) -> list[Station]: ...
