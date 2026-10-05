from mobile_fuel_stations.api import TankerkoenigClient


def test_normalizes_tankerkoenig_field_names():
    station = TankerkoenigClient._normalize({
        "id": "demo",
        "name": "Demo Station",
        "brand": "Demo",
        "diesel": "1.799",
        "dist": 2.4,
        "isOpen": True,
        "street": "Example Street",
        "houseNumber": "1",
        "postCode": 12345,
        "place": "Demo Town",
        "lat": 50.0,
        "lng": 8.0,
    })
    assert station.station_id == "demo"
    assert station.price == 1.799
    assert station.is_open is True
    assert station.house_number == "1"
