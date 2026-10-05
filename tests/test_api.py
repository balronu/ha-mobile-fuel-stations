from mobile_fuel_stations.api import Station, sort_stations


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
