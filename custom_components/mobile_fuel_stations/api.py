"""Provider-neutral station model and selection helpers."""

from __future__ import annotations

from math import isfinite
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
    }
    attributes.update({key: value for key, value in optional.items() if value is not None})
    return attributes
