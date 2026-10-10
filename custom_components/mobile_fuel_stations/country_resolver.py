"""Offline latitude/longitude to ISO-3166-1 alpha-2 resolution.

This module is deliberately provider-neutral and has no Home Assistant or GIS
dependency.  The Natural Earth dataset is loaded lazily on first use and then
cached for the lifetime of the process.
"""

from __future__ import annotations

import json
import math
from numbers import Real
from pathlib import Path
from typing import Any

_DATA_PATH = Path(__file__).with_name("data") / "countries_50m.json"
_EPSILON = 1e-12
_COUNTRIES: tuple[dict[str, Any], ...] | None = None


def _valid_coordinates(latitude: object, longitude: object) -> tuple[float, float] | None:
    if isinstance(latitude, bool) or isinstance(longitude, bool):
        return None
    if not isinstance(latitude, Real) or not isinstance(longitude, Real):
        return None
    lat, lon = float(latitude), float(longitude)
    if not math.isfinite(lat) or not math.isfinite(lon):
        return None
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        return None
    return lat, lon


def _on_segment(x: float, y: float, first: list[float], second: list[float]) -> bool:
    x1, y1 = first
    x2, y2 = second
    cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    if abs(cross) > _EPSILON:
        return False
    return min(x1, x2) - _EPSILON <= x <= max(x1, x2) + _EPSILON and min(y1, y2) - _EPSILON <= y <= max(y1, y2) + _EPSILON


def _point_in_ring(longitude: float, latitude: float, ring: list[list[float]]) -> tuple[bool, bool]:
    inside = False
    for first, second in zip(ring, ring[1:] + ring[:1]):
        if _on_segment(longitude, latitude, first, second):
            return True, True
        x1, y1 = first
        x2, y2 = second
        if (y1 > latitude) != (y2 > latitude):
            crossing_lon = (x2 - x1) * (latitude - y1) / (y2 - y1) + x1
            if longitude < crossing_lon:
                inside = not inside
    return inside, False


def _point_in_polygon(longitude: float, latitude: float, polygon: dict[str, Any]) -> bool:
    xmin, ymin, xmax, ymax = polygon["bbox"]
    if not xmin <= longitude <= xmax or not ymin <= latitude <= ymax:
        return False
    parity = False
    for ring in polygon["rings"]:
        inside, boundary = _point_in_ring(longitude, latitude, ring)
        if boundary:
            return True
        parity ^= inside
    return parity


def _load_countries() -> tuple[dict[str, Any], ...]:
    global _COUNTRIES
    if _COUNTRIES is None:
        try:
            payload = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
            _COUNTRIES = tuple(payload["countries"])
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            # Remember a failed load so a missing/corrupt optional dataset is
            # fail-open and cannot cause repeated synchronous file I/O during
            # coordinator refreshes.
            _COUNTRIES = ()
            raise
    return _COUNTRIES


def load_countries() -> tuple[dict[str, Any], ...]:
    """Load and cache the dataset once.

    Home Assistant calls this through ``async_add_executor_job`` during entry
    setup.  Runtime resolution then only walks the in-memory cache.
    """

    return _load_countries()


def resolve(latitude: float, longitude: float) -> str | None:
    """Return the Natural Earth ISO code for latitude/longitude, or None.

    The public argument order intentionally follows MFS/HA (latitude,
    longitude).  Stored polygon coordinates follow GeoJSON order (longitude,
    latitude).
    """

    coordinates = _valid_coordinates(latitude, longitude)
    if coordinates is None:
        return None
    lat, lon = coordinates
    for country in _load_countries():
        xmin, ymin, xmax, ymax = country["bbox"]
        if not xmin <= lon <= xmax or not ymin <= lat <= ymax:
            continue
        if any(_point_in_polygon(lon, lat, polygon) for polygon in country["polygons"]):
            return country["iso"]
    return None


def clear_cache() -> None:
    """Clear the process-local cache for tests and tooling."""

    global _COUNTRIES
    _COUNTRIES = None


__all__ = ["clear_cache", "load_countries", "resolve"]
