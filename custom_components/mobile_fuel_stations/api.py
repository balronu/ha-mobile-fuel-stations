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
                fallbacks[fuel] = station.fallback_used
        merged.append(replace(first, fuel_prices=prices or None, fuel_fallbacks=fallbacks or None))
    return merged


def sort_stations(stations: list[Station], limit: int, *, mode: str = "price", fuel: str = "diesel") -> list[Station]:
    """Sort by an explicit mode; coordinator default is distance."""
    if mode == "price":
        key = lambda station: (not station.is_open, (station.fuel_prices or {}).get(fuel) is None, (station.fuel_prices or {}).get(fuel, float("inf")), station.distance if station.distance is not None else float("inf"), station.station_id)
    else:
        key = lambda station: (station.distance is None, station.distance if station.distance is not None else float("inf"), not station.is_open, station.station_id)
    return sorted(stations, key=key)[:limit]


def nearest_station(stations: list[Station]) -> Station | None:
    """Return the nearest open station with a valid distance."""

    candidates = [
        station
        for station in stations
        if station.is_open and station.distance is not None and isfinite(station.distance)
    ]
    return min(candidates, key=lambda station: (station.distance, station.station_id)) if candidates else None


def cheapest_station(stations: list[Station]) -> Station | None:
    """Return the cheapest open station with a valid price."""

    candidates = [
        station
        for station in stations
        if station.is_open and station.price is not None and isfinite(station.price)
    ]
    return min(candidates, key=lambda station: (station.price, station.station_id)) if candidates else None


def cheapest_by_fuel(stations: list[Station]) -> dict[str, Station]:
    """Return the cheapest station independently for every requested fuel."""
    result: dict[str, Station] = {}
    for station in stations:
        if not station.is_open:
            continue
        for fuel, price in (station.fuel_prices or {}).items():
            if price is None or not isfinite(price):
                continue
            current = result.get(fuel)
            if current is None or price < (current.fuel_prices or {}).get(fuel, float("inf")):
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
        "fuel_fallbacks": station.fuel_fallbacks,
    }
    attributes.update({
        key: value
        for key, value in optional.items()
        if value is not None and (key != "fallback_used" or value)
    })
    return attributes
