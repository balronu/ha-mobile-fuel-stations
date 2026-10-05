import json
import math
from pathlib import Path

import pytest

from mobile_fuel_stations.country_resolver import _point_in_polygon, clear_cache, resolve


@pytest.fixture(autouse=True)
def reset_resolver_cache():
    clear_cache()
    yield
    clear_cache()


@pytest.mark.parametrize(
    ("latitude", "longitude", "expected"),
    [
        (49.2402, 6.9969, "DE"),
        (48.8566, 2.3522, "FR"),
        (48.2082, 16.3738, "AT"),
        (41.9028, 12.4964, "IT"),
        (40.4168, -3.7038, "ES"),
        (52.2297, 21.0122, "PL"),
        (48.1486, 17.1077, "SK"),
        (51.5074, -0.1278, "GB"),
        (35.8989, 14.5146, "MT"),
        (34.6800, 33.0400, "CY"),
        (39.5696, 2.6502, "ES"),
        (40.1209, 9.0129, "IT"),
        (37.5999, 14.0154, "IT"),
        (42.0396, 9.0129, "FR"),
    ],
)
def test_representative_european_points(latitude, longitude, expected):
    assert resolve(latitude, longitude) == expected


@pytest.mark.parametrize(
    ("latitude", "longitude", "expected"),
    [
        (49.2402, 6.9969, "DE"),
        (49.1833, 6.9, "FR"),
        (48.1351, 11.5820, "DE"),
        (47.8095, 13.0550, "AT"),
        (47.9990, 7.8420, "DE"),
        (47.5596, 7.5886, "CH"),
        (50.6292, 3.0573, "FR"),
        (50.8503, 4.3517, "BE"),
    ],
)
def test_clear_boundary_side_points(latitude, longitude, expected):
    assert resolve(latitude, longitude) == expected


@pytest.mark.parametrize(
    "latitude,longitude",
    [
        (None, 0),
        (0, None),
        ("49.2", 7.0),
        (49.2, "7.0"),
        (True, 7.0),
        (49.2, False),
        (math.nan, 7.0),
        (49.2, math.inf),
        (90.1, 0),
        (-90.1, 0),
        (0, 180.1),
        (0, -180.1),
    ],
)
def test_invalid_coordinates_return_none(latitude, longitude):
    assert resolve(latitude, longitude) is None


@pytest.mark.parametrize("latitude,longitude", [(40.7, -74.0), (0.0, 0.0), (45.0, 45.0)])
def test_outside_embedded_europe_returns_none(latitude, longitude):
    assert resolve(latitude, longitude) is None


def test_dataset_integrity():
    path = Path(__file__).parents[1] / "custom_components/mobile_fuel_stations/data/countries_50m.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    countries = payload["countries"]
    assert len(countries) == 50
    assert {country["iso"] for country in countries} >= {
        "DE", "AT", "FR", "IT", "ES", "PL", "SK", "BG", "ME", "RS", "BE", "CH", "GB", "MT", "CY"
    }
    assert all(len(country["iso"]) == 2 and country["iso"].isupper() for country in countries)
    assert all(country["iso"] != "-99" and country["iso"] != "XK" for country in countries)
    assert all(len(country["bbox"]) == 4 for country in countries)
    assert all(country["bbox"][0] <= country["bbox"][2] and country["bbox"][1] <= country["bbox"][3] for country in countries)
    assert sum(len(country["polygons"]) for country in countries) == 50
    assert sum(len(polygon["rings"]) for country in countries for polygon in country["polygons"]) == 343
    assert sum(len(ring) for country in countries for polygon in country["polygons"] for ring in polygon["rings"]) == 21690


def test_boundary_is_deterministic():
    result = resolve(49.0, 7.0)
    assert result == resolve(49.0, 7.0)


def test_polygon_hole_is_not_classified_as_country():
    polygon = {
        "bbox": [0.0, 0.0, 10.0, 10.0],
        "rings": [
            [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]],
            [[3.0, 3.0], [7.0, 3.0], [7.0, 7.0], [3.0, 7.0]],
        ],
    }
    assert _point_in_polygon(1.0, 1.0, polygon)
    assert not _point_in_polygon(5.0, 5.0, polygon)
