from mobile_fuel_stations.coordinator import haversine_km


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
