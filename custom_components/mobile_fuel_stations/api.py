"""Provider-neutral station model and selection helpers."""

from __future__ import annotations

from math import isfinite
from collections import defaultdict
from dataclasses import replace
from .providers.base import (
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    Station,
)


MobileFuelStationsError = ProviderError
MobileFuelStationsAuthError = ProviderAuthError
MobileFuelStationsRateLimitError = ProviderRateLimitError


from .providers.tankerkoenig import TankerkoenigProvider

TankerkoenigClient = TankerkoenigProvider


def merge_stations(stations: list[Station]) -> list[Station]:
    """Merge fuel-specific results into one station card per safe identity."""
    groups: dict[tuple[str, str], list[Station]] = defaultdict(list)
    for station in stations:
        groups[(station.provider or "unknown", station.station_id)].append(station)
    merged: list[Station] = []
    for group in groups.values():
        first = group[0]
        prices: dict[str, float | None] = {}
        currencies: dict[str, str | None] = {}
        fallbacks: dict[str, bool] = {}
        for station in group:
            fuel = station.requested_fuel or station.fuel_type
            if fuel:
                effective = station.fuel_type
                if station.fallback_used and effective and any(
                    existing_price == station.price and existing_fuel == effective
                    for existing_fuel, existing_price in prices.items()
                ):
                    continue
                prices[fuel] = station.price
                if station.fuel_currencies and fuel in station.fuel_currencies:
                    currencies[fuel] = station.fuel_currencies[fuel]
                elif fuel:
                    currencies[fuel] = station.currency
                fallbacks[fuel] = station.fallback_used
        merged.append(replace(first, fuel_prices=prices or None, fuel_currencies=currencies or None, fuel_fallbacks=fallbacks or None))
    return merged


def sort_stations(stations: list[Station], limit: int, *, mode: str = "price", fuel: str = "diesel") -> list[Station]:
    """Sort by an explicit mode; coordinator default is distance."""
    if mode == "price":
        currency = _comparison_currency(stations, fuel)
        key = lambda station: (not station.is_open, _price_for_currency(station, fuel, currency) is None, _price_for_currency(station, fuel, currency) if _price_for_currency(station, fuel, currency) is not None else float("inf"), station.distance if station.distance is not None else float("inf"), station.station_id)
    else:
        key = lambda station: (station.distance is None, station.distance if station.distance is not None else float("inf"), not station.is_open, station.station_id)
    return sorted(stations, key=key)[:limit]


def nearest_station(stations: list[Station]) -> Station | None:
    """Return the nearest non-closed station with a valid distance.

    Providers such as Nakordoni may not expose opening status.  ``None`` means
    unknown, not closed, so those stations remain eligible for a distance-based
    highlight while the frontend still omits a made-up open/closed label.
    """

    candidates = [
        station
        for station in stations
        if station.is_open is not False
        and station.distance is not None
        and isfinite(station.distance)
    ]
    return min(
        candidates,
        key=lambda station: (
            station.distance,
            station.is_open is not True,
            station.station_id,
        ),
    ) if candidates else None


def cheapest_station(stations: list[Station]) -> Station | None:
    """Return the cheapest non-closed station with a valid price.

    An unknown opening status must not suppress a comparable provider price;
    only an explicitly closed station is excluded.
    """

    currency = _comparison_currency(stations, None)
    candidates = [
        station
        for station in stations
        if station.is_open is not False
        and station.price_stale is not True
        and station.price is not None
        and isfinite(station.price)
        and _currency_matches(station, None, currency)
    ]
    return min(
        candidates,
        key=lambda station: (
            station.price,
            station.is_open is not True,
            station.station_id,
        ),
    ) if candidates else None


def cheapest_by_fuel(stations: list[Station]) -> dict[str, Station]:
    """Return the cheapest non-closed station for every requested fuel."""
    result: dict[str, Station] = {}
    for station in stations:
        if station.is_open is False:
            continue
        for fuel, price in (station.fuel_prices or {}).items():
            currency = _comparison_currency(stations, fuel)
            if station.price_stale is True or price is None or not isfinite(price):
                continue
            if not _currency_matches(station, fuel, currency):
                continue
            current = result.get(fuel)
            current_price = (current.fuel_prices or {}).get(fuel, float("inf")) if current else float("inf")
            if current is None or (price, station.is_open is not True, station.station_id) < (
                current_price,
                current.is_open is not True,
                current.station_id,
            ):
                result[fuel] = station
    return result


def station_attributes(station: Station | None) -> dict[str, object] | None:
    """Serialize a station for structured Home Assistant attributes."""

    if station is None:
        return None
    attributes = {
        "station_id": station.station_id,
        "station_name": station.name,
        "brand": station.brand,
        "price": station.price,
        "distance": station.distance,
        "is_open": station.is_open,
        "street": station.street,
        "house_number": station.house_number,
        "postcode": station.postcode,
        "place": station.place,
        "latitude": station.latitude,
        "longitude": station.longitude,
    }
    optional = {
        "currency": station.currency,
        "provider": station.provider,
        "price_updated_at": station.price_updated_at.isoformat() if station.price_updated_at else None,
        "price_confirmed_at": station.price_confirmed_at.isoformat() if station.price_confirmed_at else None,
        "price_age_hours": station.price_age_hours,
        "price_stale": station.price_stale,
        "fuel_type": station.fuel_type,
        "requested_fuel": station.requested_fuel,
        "fallback_used": station.fallback_used,
        "fuel_prices": station.fuel_prices,
        "fuel_currencies": station.fuel_currencies,
        "fuel_fallbacks": station.fuel_fallbacks,
    }
    attributes.update({
        key: value
        for key, value in optional.items()
        if value is not None and (key != "fallback_used" or value)
    })
    return attributes


def _station_currency(station: Station, fuel: str | None) -> str | None:
    if fuel and station.fuel_currencies and fuel in station.fuel_currencies:
        value = station.fuel_currencies[fuel]
    else:
        value = station.currency
    return value.strip().upper() if isinstance(value, str) and value.strip() else None


def _comparison_currency(stations: list[Station], fuel: str | None) -> str | None:
    """Choose one currency group; never rank explicit currencies together."""
    explicit = [_station_currency(station, fuel) for station in stations]
    explicit = [value for value in explicit if value]
    return sorted(set(explicit))[0] if explicit else None


def _currency_matches(station: Station, fuel: str | None, currency: str | None) -> bool:
    actual = _station_currency(station, fuel)
    return currency is None or actual == currency


def _price_for_currency(station: Station, fuel: str, currency: str | None) -> float | None:
    price = (station.fuel_prices or {}).get(fuel)
    if price is None or not isfinite(price) or not _currency_matches(station, fuel, currency):
        return None
    return price
