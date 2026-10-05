from mobile_fuel_stations.api import cheapest_station, nearest_station, Station, station_attributes, sort_stations


def station(name, price, is_open):
    return Station(name, name, "", price, None, is_open, "", "", "", "", None, None)


def test_open_stations_are_before_closed_and_prices_sort():
    result = sort_stations(
        [station("closed-cheap", 1.0, False), station("open-expensive", 2.0, True), station("open-cheap", 1.5, True)],
        5,
    )
    assert [item.name for item in result] == ["open-cheap", "open-expensive", "closed-cheap"]


def test_missing_prices_are_last_within_open_group():
    result = sort_stations([station("unknown", None, True), station("priced", 2.0, True)], 5)
    assert [item.name for item in result] == ["priced", "unknown"]


def test_nearest_uses_distance_before_slot_limiting_and_allows_missing_price():
    stations = [
        Station("far", "Far", "", 1.5, 5.0, True, "", "", "", "", None, None),
        Station("near", "Near", "", None, 1.0, True, "", "", "", "", None, None),
        Station("closed", "Closed", "", 1.0, 0.5, False, "", "", "", "", None, None),
    ]
    assert nearest_station(stations).station_id == "near"


def test_cheapest_requires_open_station_and_uses_station_id_tie_breaker():
    stations = [
        Station("z", "Z", "", 1.5, 2.0, True, "", "", "", "", None, None),
        Station("a", "A", "", 1.5, 1.0, True, "", "", "", "", None, None),
        Station("closed", "Closed", "", 1.0, 0.5, False, "", "", "", "", None, None),
    ]
    assert cheapest_station(stations).station_id == "a"


def test_station_attributes_preserve_optional_values():
    station = Station("id", "Name", "Brand", None, 1.2, True, "Street", "1", "12345", "Town", 50.0, 8.0)
    assert station_attributes(station) == {
        "station_id": "id", "station_name": "Name", "brand": "Brand", "price": None,
        "distance": 1.2, "is_open": True, "street": "Street", "house_number": "1",
        "postcode": "12345", "place": "Town", "latitude": 50.0, "longitude": 8.0,
    }
    assert station_attributes(None) is None
