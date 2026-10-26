from mobile_fuel_stations.api import cheapest_by_fuel, cheapest_station, merge_stations, nearest_station, Station, station_attributes, sort_stations


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


def test_nearest_includes_unknown_open_status_but_excludes_closed():
    stations = [
        Station("unknown", "Unknown", "", None, 1.0, None, "", "", "", "", None, None),
        Station("closed", "Closed", "", None, 0.5, False, "", "", "", "", None, None),
    ]
    assert nearest_station(stations).station_id == "unknown"


def test_cheapest_includes_unknown_open_status_but_excludes_closed():
    stations = [
        Station("z", "Z", "", 1.5, 2.0, True, "", "", "", "", None, None),
        Station("a", "A", "", 1.5, 1.0, True, "", "", "", "", None, None),
        Station("closed", "Closed", "", 1.0, 0.5, False, "", "", "", "", None, None),
        Station("unknown", "Unknown", "", 0.9, 3.0, None, "", "", "", "", None, None),
    ]
    assert cheapest_station(stations).station_id == "unknown"


def test_cheapest_ignores_explicitly_stale_price():
    stale = Station("stale", "Stale", "", 1.0, 1.0, None, "", "", "", "", None, None, price_stale=True)
    current = Station("current", "Current", "", 1.1, 2.0, None, "", "", "", "", None, None, price_stale=False)
    assert cheapest_station([stale, current]).station_id == "current"


def test_unknown_open_status_wins_per_fuel_price_comparison():
    stations = [
        Station("closed", "Closed", "", 1.0, 1.0, False, "", "", "", "", None, None, fuel_prices={"e10": 1.0}),
        Station("unknown", "Unknown", "", 1.8, 2.0, None, "", "", "", "", None, None, fuel_prices={"e10": 1.8}),
    ]
    assert cheapest_by_fuel(stations) == {"e10": stations[1]}


def test_stale_per_fuel_price_is_not_selected_as_current_cheapest():
    stale = Station(
        "stale", "Stale", "", 1.0, 1.0, None, "", "", "", "", None, None,
        price_stale=True, fuel_prices={"e10": 1.0},
    )
    current = Station(
        "current", "Current", "", 1.1, 2.0, None, "", "", "", "", None, None,
        price_stale=False, fuel_prices={"e10": 1.1},
    )
    assert cheapest_by_fuel([stale, current]) == {"e10": current}


def test_station_attributes_preserve_optional_values():
    station = Station("id", "Name", "Brand", None, 1.2, True, "Street", "1", "12345", "Town", 50.0, 8.0)
    assert station_attributes(station) == {
        "station_id": "id", "station_name": "Name", "brand": "Brand", "price": None,
        "distance": 1.2, "is_open": True, "street": "Street", "house_number": "1",
        "postcode": "12345", "place": "Town", "latitude": 50.0, "longitude": 8.0,
    }
    assert station_attributes(None) is None


def test_multi_fuel_results_merge_without_cross_fuel_price_comparison():
    diesel = Station("same", "Station", "Brand", 2.079, 4.2, True, "Street", "1", "1", "Town", 50.0, 8.0, provider="demo", fuel_type="diesel", requested_fuel="diesel")
    e10 = Station("same", "Station", "Brand", 2.018, 4.2, True, "Street", "1", "1", "Town", 50.0, 8.0, provider="demo", fuel_type="e10", requested_fuel="e10")
    merged = merge_stations([diesel, e10])
    assert len(merged) == 1
    assert merged[0].fuel_prices == {"diesel": 2.079, "e10": 2.018}
    assert cheapest_by_fuel(merged) == {"diesel": merged[0], "e10": merged[0]}


def test_price_sort_uses_explicit_fuel_and_missing_prices_last():
    diesel = Station("diesel", "Diesel", "", 2.1, 4, True, "", "", "", "", None, None, fuel_prices={"diesel": 2.1})
    e10 = Station("e10", "E10", "", 1.8, 5, True, "", "", "", "", None, None, fuel_prices={"e10": 1.8})
    result = sort_stations([diesel, e10], 5, mode="price", fuel="diesel")
    assert [station.station_id for station in result] == ["diesel", "e10"]


def test_price_sort_does_not_compare_explicit_currencies():
    eur = Station("eur", "EUR", "", 2.0, 1, True, "", "", "", "", None, None,
                  currency="EUR", fuel_prices={"diesel": 2.0}, fuel_currencies={"diesel": "EUR"})
    pln = Station("pln", "PLN", "", 5.0, 1, True, "", "", "", "", None, None,
                  currency="PLN", fuel_prices={"diesel": 5.0}, fuel_currencies={"diesel": "PLN"})
    assert [station.station_id for station in sort_stations([pln, eur], 2, mode="price", fuel="diesel")] == ["eur", "pln"]
    assert cheapest_by_fuel([pln, eur])["diesel"].station_id == "eur"
