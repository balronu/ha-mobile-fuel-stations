from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from mobile_fuel_stations.const import (
    ADAPTIVE_CITY_INTERVAL,
    ADAPTIVE_COUNTRY_ROAD_INTERVAL,
    ADAPTIVE_MOTORWAY_INTERVAL,
    ADAPTIVE_STATIONARY_INTERVAL,
)
from mobile_fuel_stations.coordinator import (
    GpsSample,
    MobileFuelStationsCoordinator,
    _gps_sample,
    haversine_km,
)


def test_haversine_distance_supports_sub_threshold_movement():
    # Roughly 100 m north at this latitude.
    distance = haversine_km((50.000000, 8.000000), (50.000900, 8.000000))
    assert 0.09 < distance < 0.11
    assert distance < 2.0


def test_haversine_distance_supports_movement_threshold_case():
    # Roughly 2.1 km north at this latitude.
    distance = haversine_km((50.000000, 8.000000), (50.018900, 8.000000))
    assert 2.0 < distance < 2.2


def test_haversine_distance_is_zero_for_same_reference():
    assert haversine_km((50.0, 8.0), (50.0, 8.0)) == 0.0


def test_adaptive_intervals_follow_stationary_city_road_and_motorway_bands():
    assert MobileFuelStationsCoordinator._adaptive_interval(None) == ADAPTIVE_STATIONARY_INTERVAL
    assert MobileFuelStationsCoordinator._adaptive_interval(0) == ADAPTIVE_STATIONARY_INTERVAL
    assert MobileFuelStationsCoordinator._adaptive_interval(30) == ADAPTIVE_CITY_INTERVAL
    assert MobileFuelStationsCoordinator._adaptive_interval(31) == ADAPTIVE_COUNTRY_ROAD_INTERVAL
    assert MobileFuelStationsCoordinator._adaptive_interval(70) == ADAPTIVE_COUNTRY_ROAD_INTERVAL
    assert MobileFuelStationsCoordinator._adaptive_interval(70.1) == ADAPTIVE_MOTORWAY_INTERVAL


def test_adaptive_intervals_are_the_requested_upper_bounds():
    assert ADAPTIVE_STATIONARY_INTERVAL == timedelta(minutes=15)
    assert ADAPTIVE_CITY_INTERVAL == timedelta(minutes=5)
    assert ADAPTIVE_COUNTRY_ROAD_INTERVAL == timedelta(minutes=2)
    assert ADAPTIVE_MOTORWAY_INTERVAL == timedelta(minutes=1)


def test_gps_sample_rejects_stale_inaccurate_and_unrealistic_positions():
    now = datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc)
    hass = SimpleNamespace(states=SimpleNamespace(get=lambda _entity: SimpleNamespace(
        state="home",
        attributes={"latitude": 49.2, "longitude": 7.0, "gps_accuracy": 1500},
        last_reported=now,
        last_updated=now,
        last_changed=now,
    )))
    assert _gps_sample(hass, "device_tracker.vehicle", now=now) is None

    hass.states.get = lambda _entity: SimpleNamespace(
        state="home",
        attributes={"latitude": 49.2, "longitude": 7.0, "speed": 250},
        last_reported=now - timedelta(minutes=11),
        last_updated=now - timedelta(minutes=11),
        last_changed=now - timedelta(minutes=11),
    )
    assert _gps_sample(hass, "device_tracker.vehicle", now=now) is None


def test_gps_sample_derives_speed_only_from_plausible_position_pair():
    first_at = datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc)
    second_at = first_at + timedelta(minutes=5)
    previous = GpsSample((49.2, 7.0), first_at, 5, None)
    hass = SimpleNamespace(states=SimpleNamespace(get=lambda _entity: SimpleNamespace(
        state="home",
        attributes={"latitude": 49.2 + 0.018, "longitude": 7.0},
        last_reported=second_at,
        last_updated=second_at,
        last_changed=second_at,
    )))
    sample = _gps_sample(
        hass, "device_tracker.vehicle", now=second_at, previous=previous
    )
    assert sample is not None
    assert 20 < sample.speed_kmh < 30
